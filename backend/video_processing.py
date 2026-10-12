import cv2
import os
import uuid
import math
import numpy as np

# Load YOLOv8-pose model for robust human keypoint extraction
_yolo_model = None
def get_pose_model():
    global _yolo_model
    if _yolo_model is None:
        try:
            from ultralytics import YOLO
            _yolo_model = YOLO("yolov8n-pose.pt")
        except Exception as e:
            print(f"Error loading YOLO pose model: {e}")
            _yolo_model = None
    return _yolo_model

def calculate_angle_vertical(point1, point2):
    """Calculate the angle of a line segment with the vertical."""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.degrees(math.atan2(dx, dy))
    return abs(angle)

def calculate_angle(a, b, c):
    """Calculate the angle between three points (a -> b -> c)."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def classify_activity(
    stride_spreads,
    ankle_y_diffs,
    knee_angles_l,
    knee_angles_r,
    hip_y_positions,
    target_h,
    athletic_pose_frames,
    person_detected_frames,
    requested_activity
):
    """
    Distinguishes true athletic movements from non-sports videos (e.g. video resumes, talking heads, static poses):
    - Non-Sports: Lower kinetic chain not visible OR motion range of motion is negligible.
    - Running / Sprinting: Alternating asymmetric foot strikes, high stride spread, alternating ankle elevation.
    - Squatting: Synchronous bilateral knee flexion (both knees bend together through active ROM > 25 deg, feet planted).
    - Jumping / Landing: Simultaneous vertical extension / compression of both limbs with high hip elevation.
    """
    # 1. Require athlete's kinetic chain to be visible in a reasonable portion of the video
    if athletic_pose_frames < 8 or person_detected_frames < 8:
        return "Non-Sports / No Athletic Movement Detected"

    athletic_ratio = athletic_pose_frames / max(1, person_detected_frames)
    if athletic_ratio < 0.20:
        # Lower body is absent in over 80% of frames (talking head, bust shot, webcam interview, video resume)
        return "Non-Sports / No Athletic Movement Detected"

    if not knee_angles_l or not knee_angles_r or len(knee_angles_l) < 5:
        return "Non-Sports / No Athletic Movement Detected"

    mean_stride = float(np.mean(stride_spreads)) if stride_spreads else 0.0
    max_stride = float(np.max(stride_spreads)) if stride_spreads else 0.0
    mean_ankle_y_diff = float(np.mean(ankle_y_diffs)) if ankle_y_diffs else 0.0

    n = min(len(knee_angles_l), len(knee_angles_r))
    if n > 10 and np.std(knee_angles_l[:n]) > 2 and np.std(knee_angles_r[:n]) > 2:
        knee_corr = float(np.corrcoef(knee_angles_l[:n], knee_angles_r[:n])[0, 1])
    else:
        knee_corr = 0.0

    min_knee = min(float(np.min(knee_angles_l)), float(np.min(knee_angles_r)))
    knee_rom = max(
        float(np.max(knee_angles_l) - np.min(knee_angles_l)),
        float(np.max(knee_angles_r) - np.min(knee_angles_r))
    )
    hip_vert_rom = (float(np.max(hip_y_positions) - np.min(hip_y_positions)) / target_h) if hip_y_positions else 0.0

    # 2. Check for dynamic athletic energy:
    # If knees barely bend (< 15 degrees ROM), stride spread is tiny, and hips don't move, it is static / non-sports
    if knee_rom < 15.0 and mean_stride < 0.08 and hip_vert_rom < 0.05:
        return "Non-Sports / No Athletic Movement Detected"

    # 3. Running / Sprinting: Alternating gait with significant stride spread or ankle elevation
    is_alternating_gait = (mean_stride > 0.12 or max_stride > 0.22 or mean_ankle_y_diff > 0.05)
    if is_alternating_gait:
        if mean_stride > 0.25 or requested_activity == "Sprinting":
            return "Sprinting"
        return "Running"

    # 4. Squatting: Requires active knee extension-flexion rep cycle (down and up, knee_rom > 25°),
    # high bilateral knee correlation, and stationary feet
    if knee_corr > 0.40 and min_knee < 125 and knee_rom > 25.0 and mean_stride < 0.10:
        return "Squatting"

    # 5. Jumping / Landing: High vertical hip excursion with simultaneous knee action
    if hip_vert_rom > 0.10 and not is_alternating_gait:
        return "Jumping"

    # 6. Upper-body / Other sports activities
    if requested_activity in ["Throwing", "Cutting Movements", "Sport-Specific Drills"] and knee_rom > 15.0:
        return requested_activity

    if is_alternating_gait or mean_stride > 0.08:
        return "Running"

    return "Non-Sports / No Athletic Movement Detected"

def process_video_with_mediapipe(
    input_path: str,
    output_dir: str,
    activity: str = "Unknown",
    surface_type: str = "Unknown",
    footwear: str = "Unknown",
    rpe: int = 5,
    sleep_quality: int = 5
):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception("Error opening video stream or file")

    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if orig_width < 320 or orig_height < 240:
        cap.release()
        raise Exception(f"Video resolution too low: {orig_width}x{orig_height}. Minimum required is 320x240.")

    # Target resolution (max 1280 on largest dimension) for high performance & universal device support
    max_dim = max(orig_width, orig_height)
    if max_dim > 1280:
        scale = 1280.0 / max_dim
        target_w = int(orig_width * scale)
        target_h = int(orig_height * scale)
    else:
        target_w = orig_width
        target_h = orig_height
        
    # Ensure even dimensions for H.264
    target_w = target_w - (target_w % 2)
    target_h = target_h - (target_h % 2)

    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, filename)
    temp_raw_path = os.path.join(output_dir, f"raw_{filename}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_raw_path, fourcc, fps, (target_w, target_h))

    risk_flags = []
    knee_angles_l = []
    knee_angles_r = []
    trunk_leans = []
    valgus_angles_l = []
    valgus_angles_r = []
    stride_spreads = []
    ankle_y_diffs = []
    hip_y_positions = []
    trajectory_points = []
    person_detected_frames = 0
    athletic_pose_frames = 0

    model = get_pose_model()

    BONES = [
        # Torso & Spine (Electric Cyan)
        (5, 6, (255, 220, 0)),
        (5, 11, (255, 220, 0)),
        (6, 12, (255, 220, 0)),
        (11, 12, (255, 220, 0)),
        # Left Arm (Magenta)
        (5, 7, (220, 0, 255)),
        (7, 9, (220, 0, 255)),
        # Right Arm (Magenta)
        (6, 8, (220, 0, 255)),
        (8, 10, (220, 0, 255)),
        # Left Leg (Neon Lime Green)
        (11, 13, (0, 255, 100)),
        (13, 15, (0, 255, 100)),
        # Right Leg (Electric Royal Blue)
        (12, 14, (255, 130, 0)),
        (14, 16, (255, 130, 0)),
    ]

    KEY_JOINTS = [5, 6, 11, 12, 13, 14, 15, 16]

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Resize to target HD dimensions
        if (frame.shape[1], frame.shape[0]) != (target_w, target_h):
            frame = cv2.resize(frame, (target_w, target_h))

        curr_trunk_lean = 0.0
        curr_valgus = 0.0
        ang_l_knee = None
        ang_r_knee = None
        has_athletic_joints = False

        if model is not None:
            results = model(frame, imgsz=640, verbose=False)
            if results and len(results[0].keypoints.data) > 0:
                kpts = results[0].keypoints.data[0].cpu().numpy()
                person_detected_frames += 1

                # Check if hips and lower kinetic chain are visible
                has_hips = (kpts[11][2] > 0.35 or kpts[12][2] > 0.35)
                has_legs = (kpts[13][2] > 0.3 or kpts[14][2] > 0.3 or kpts[15][2] > 0.3 or kpts[16][2] > 0.3)
                if has_hips and has_legs:
                    athletic_pose_frames += 1
                    has_athletic_joints = True

                # 1. Draw Skeleton Bones
                for p1, p2, color in BONES:
                    if kpts[p1][2] > 0.35 and kpts[p2][2] > 0.35:
                        pt1 = (int(kpts[p1][0]), int(kpts[p1][1]))
                        pt2 = (int(kpts[p2][0]), int(kpts[p2][1]))
                        cv2.line(frame, pt1, pt2, color, 4, cv2.LINE_AA)

                # 2. Draw Key Joints with Halo Glow
                for j in KEY_JOINTS:
                    if kpts[j][2] > 0.35:
                        pt = (int(kpts[j][0]), int(kpts[j][1]))
                        cv2.circle(frame, pt, 8, (0, 0, 255), -1, cv2.LINE_AA)
                        cv2.circle(frame, pt, 10, (255, 255, 255), 2, cv2.LINE_AA)

                # 3. Compute Biomechanical Angles
                try:
                    if has_hips:
                        mid_hip_y = (kpts[11][1] + kpts[12][1]) / 2
                        hip_y_positions.append(mid_hip_y)

                    if (kpts[11][2] > 0.3 and kpts[13][2] > 0.3 and kpts[15][2] > 0.3):
                        ang_l_knee = calculate_angle(kpts[11][:2], kpts[13][:2], kpts[15][:2])
                        knee_angles_l.append(ang_l_knee)
                        pt_lk = (int(kpts[13][0]) - 80, int(kpts[13][1]))
                        cv2.putText(frame, f"L:{int(ang_l_knee)}d", pt_lk, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2, cv2.LINE_AA)

                    if (kpts[12][2] > 0.3 and kpts[14][2] > 0.3 and kpts[16][2] > 0.3):
                        ang_r_knee = calculate_angle(kpts[12][:2], kpts[14][:2], kpts[16][:2])
                        knee_angles_r.append(ang_r_knee)
                        pt_rk = (int(kpts[14][0]) + 15, int(kpts[14][1]))
                        cv2.putText(frame, f"R:{int(ang_r_knee)}d", pt_rk, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 130, 0), 2, cv2.LINE_AA)

                    # Trunk lean
                    if (kpts[5][2] > 0.3 and kpts[6][2] > 0.3 and kpts[11][2] > 0.3 and kpts[12][2] > 0.3):
                        mid_shoulder = [(kpts[5][0] + kpts[6][0]) / 2, (kpts[5][1] + kpts[6][1]) / 2]
                        mid_hip = [(kpts[11][0] + kpts[12][0]) / 2, (kpts[11][1] + kpts[12][1]) / 2]
                        curr_trunk_lean = calculate_angle_vertical(mid_shoulder, mid_hip)
                        trunk_leans.append(curr_trunk_lean)

                    # Knee Valgus
                    if kpts[11][2] > 0.3 and kpts[13][2] > 0.3:
                        valg_l = calculate_angle_vertical(kpts[11][:2], kpts[13][:2])
                        valgus_angles_l.append(valg_l)
                        curr_valgus = max(curr_valgus, valg_l)
                    if kpts[12][2] > 0.3 and kpts[14][2] > 0.3:
                        valg_r = calculate_angle_vertical(kpts[12][:2], kpts[14][:2])
                        valgus_angles_r.append(valg_r)
                        curr_valgus = max(curr_valgus, valg_r)

                    # Stride metrics
                    if kpts[15][2] > 0.3 and kpts[16][2] > 0.3:
                        stride_spread = abs(kpts[15][0] - kpts[16][0]) / target_h
                        ankle_y_diff = abs(kpts[15][1] - kpts[16][1]) / target_h
                        stride_spreads.append(stride_spread)
                        ankle_y_diffs.append(ankle_y_diff)

                    # Active Foot Trajectory Tracking (Ankles)
                    lead_ankle = kpts[15] if kpts[15][2] > kpts[16][2] else kpts[16]
                    if lead_ankle[2] > 0.3:
                        trajectory_points.append((int(lead_ankle[0]), int(lead_ankle[1])))
                        if len(trajectory_points) > 30:
                            trajectory_points.pop(0)

                except Exception as e:
                    pass

        # 4. Draw Trajectory Ribbon Trail
        for i in range(1, len(trajectory_points)):
            thickness = max(1, int(i / 6))
            cv2.line(frame, trajectory_points[i-1], trajectory_points[i], (0, 230, 255), thickness, cv2.LINE_AA)

        # 5. Draw On-Screen Biomechanical HUD Panel
        hud_w = min(440, target_w - 40)
        overlay = frame.copy()
        cv2.rectangle(overlay, (20, 20), (20 + hud_w, 140), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (20, 20), (20 + hud_w, 140), (71, 85, 105), 1)

        cv2.putText(frame, "AI BIOMECHANICAL ANALYZER", (35, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)
        
        if has_athletic_joints:
            status_text = "OPTIMAL FORM" if curr_valgus <= 15 and curr_trunk_lean <= 30 else "RISK DETECTED"
            status_color = (0, 230, 115) if status_text == "OPTIMAL FORM" else (70, 70, 255)
            cv2.putText(frame, f"STATUS: {status_text}", (35, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Trunk: {curr_trunk_lean:.1f}d | Valgus: {curr_valgus:.1f}d", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (203, 213, 225), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "STATUS: NO ATHLETIC MOVEMENT", (35, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (148, 163, 184), 2, cv2.LINE_AA)
            cv2.putText(frame, "Full kinetic chain not in frame", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (203, 213, 225), 1, cv2.LINE_AA)

        lead_foot = f"Frame: {person_detected_frames} | Kinetic: {athletic_pose_frames}"
        cv2.putText(frame, lead_foot, (35, 126), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (148, 163, 184), 1, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()
    
    # 6. Transcode output video to web-standard H.264 (yuv420p) with faststart
    converted = False
    try:
        import subprocess
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe, "-y", "-i", temp_raw_path,
            "-vcodec", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(output_path):
            converted = True
            if os.path.exists(temp_raw_path):
                os.remove(temp_raw_path)
    except Exception as e:
        print(f"Video transcoding warning: {e}")

    if not converted:
        if os.path.exists(temp_raw_path):
            os.replace(temp_raw_path, output_path)

    # 7. Movement & Athletic Action Recognition Engine
    detected_activity = classify_activity(
        stride_spreads,
        ankle_y_diffs,
        knee_angles_l,
        knee_angles_r,
        hip_y_positions,
        target_h,
        athletic_pose_frames,
        person_detected_frames,
        activity
    )

    # If the video does not contain athletic movement (e.g. video resume, interview, bust shot, talking head)
    if detected_activity == "Non-Sports / No Athletic Movement Detected":
        return {
            "filename": filename,
            "analytics": {
                "activity_analyzed": "Non-Sports / No Athletic Movement Detected",
                "risk_score": 0,
                "risk_level": "N/A",
                "risk_flags": ["No athletic movement, exercise, or sports action detected in the video."],
                "corrective_recommendation": "Please upload a video containing athletic sports movements (such as running, sprinting, squatting, or jumping) with the athlete's full body visible.",
                "anomaly_detected": False,
                "injury_probabilities": {
                    "ACL Injury": 0,
                    "Hamstring Injury": 0,
                    "Ankle Sprain": 0,
                    "Shoulder Injury": 0,
                    "Lower Back Injury": 0,
                    "Overuse Injury": 0
                },
                "surface_type": surface_type,
                "footwear": footwear,
                "rpe": rpe,
                "sleep_quality": sleep_quality,
                "biomechanics": {
                    "max_trunk_lean": 0,
                    "movement_asymmetry": 0,
                    "max_knee_valgus": 0
                },
                "fps": fps,
                "frame_count": frame_count
            }
        }

    # Process athletic biomechanics
    avg_trunk_lean = float(np.mean(trunk_leans)) if trunk_leans else 0.0
    max_trunk_lean = float(np.max(trunk_leans)) if trunk_leans else 0.0
    
    avg_knee_l = float(np.mean(knee_angles_l)) if knee_angles_l else 180.0
    avg_knee_r = float(np.mean(knee_angles_r)) if knee_angles_r else 180.0
    
    max_valgus = float(max(np.max(valgus_angles_l) if valgus_angles_l else 0.0, np.max(valgus_angles_r) if valgus_angles_r else 0.0))
    
    biomechanical_deviations = 0
    movement_asymmetry = abs(avg_knee_l - avg_knee_r)
    
    if max_valgus > 15:
        risk_flags.append("Significant Knee Valgus Detected (ACL Risk)")
        biomechanical_deviations += 40
    
    if max_trunk_lean > 30:
        risk_flags.append("Excessive Trunk Lean Detected (Lower Back Risk)")
        biomechanical_deviations += 30
        
    if movement_asymmetry > 15:
        risk_flags.append(f"High Movement Asymmetry ({round(movement_asymmetry)} degree diff)")
        movement_asymmetry_score = 40
    else:
        movement_asymmetry_score = movement_asymmetry * 2

    training_load_score = (rpe / 10) * 100
    fatigue_score = ((10 - sleep_quality) / 10) * 100
    if rpe > 8 and sleep_quality < 5:
        risk_flags.append("Severe Fatigue Indicators Detected")
        
    historical_injury_score = 20
    
    # 8. Weighted Risk Scoring Engine
    biomechanical_deviations = min(biomechanical_deviations, 100)
    
    final_risk_score = (
        (biomechanical_deviations * 0.35) +
        (historical_injury_score * 0.20) +
        (min(movement_asymmetry_score, 100) * 0.20) +
        (training_load_score * 0.15) +
        (fatigue_score * 0.10)
    )
    
    final_risk_score = min(round(final_risk_score), 100)
    if final_risk_score <= 25:
        risk_level = "Low Risk"
    elif final_risk_score <= 50:
        risk_level = "Moderate Risk"
    elif final_risk_score <= 75:
        risk_level = "High Risk"
    else:
        risk_level = "Critical Risk"
        
    # 9. Injury Probabilities
    injury_probs = {
        "ACL Injury": min(round(max_valgus * 3 + movement_asymmetry), 95),
        "Hamstring Injury": min(round(movement_asymmetry * 2 + fatigue_score * 0.5), 90),
        "Ankle Sprain": min(round(max_valgus * 1.5), 80),
        "Shoulder Injury": 10 if detected_activity not in ["Throwing", "Serving"] else min(round(40 + training_load_score * 0.3), 90),
        "Lower Back Injury": min(round(max_trunk_lean * 2 + fatigue_score * 0.3), 85),
        "Overuse Injury": min(round((training_load_score + fatigue_score) * 0.8), 95)
    }
    
    if not risk_flags:
        risk_flags.append("Optimal Movement Patterns Detected")

    # 10. Corrective Recommendations
    recommendations = []
    if max_valgus > 15:
        recommendations.append("Strengthen gluteus medius and incorporate neuromuscular control drills.")
    if max_trunk_lean > 30:
        recommendations.append("Focus on core stability and thoracic mobility exercises.")
    if movement_asymmetry > 15:
        recommendations.append("Implement unilateral strength training to correct imbalances.")
    if fatigue_score > 60:
        recommendations.append("Prioritize recovery, sleep optimization, and reduce training volume for 48h.")
        
    if not recommendations:
        recommendations.append("Maintain current balanced training and recovery program.")
        
    return {
        "filename": filename,
        "analytics": {
            "activity_analyzed": detected_activity,
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "risk_flags": risk_flags,
            "corrective_recommendation": " | ".join(recommendations),
            "anomaly_detected": len(risk_flags) > 0 and risk_flags[0] != "Optimal Movement Patterns Detected",
            "injury_probabilities": injury_probs,
            "surface_type": surface_type,
            "footwear": footwear,
            "rpe": rpe,
            "sleep_quality": sleep_quality,
            "biomechanics": {
                "max_trunk_lean": round(max_trunk_lean, 2),
                "movement_asymmetry": round(movement_asymmetry, 2),
                "max_knee_valgus": round(max_valgus, 2)
            },
            "fps": fps,
            "frame_count": frame_count
        }
    }
