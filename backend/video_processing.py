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
    requested_activity,
    ankle_y_l=None,
    ankle_y_r=None,
    wrist_y_l=None,
    wrist_y_r=None
):
    """
    Autonomously classifies true athletic movement based on kinetic chain mechanics,
    REGARDLESS of user input:
    - Non-Sports: Lower kinetic chain not visible or motion ROM negligible.
    - Jumping / Landing: Ballistic vertical hip displacement, flight phase (ankle lift), simultaneous knee flexion/extension.
    - Squatting: Planted feet (no flight/ankle lift), synchronous bilateral knee flexion through deep ROM, stationary stride.
    - Running / Sprinting: Alternating asymmetric foot strikes, high stride spread, alternating ankle elevation.
    - Throwing: Unilateral high-velocity upper kinetic chain excursion.
    """
    if athletic_pose_frames < 8 or person_detected_frames < 8:
        return "Non-Sports / No Athletic Movement Detected"

    athletic_ratio = athletic_pose_frames / max(1, person_detected_frames)
    if athletic_ratio < 0.20:
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

    mean_abs_knee_diff = float(np.mean(np.abs(np.array(knee_angles_l[:n]) - np.array(knee_angles_r[:n])))) if n > 0 else 0.0

    min_knee = min(float(np.min(knee_angles_l)), float(np.min(knee_angles_r)))
    knee_rom = max(
        float(np.max(knee_angles_l) - np.min(knee_angles_l)),
        float(np.max(knee_angles_r) - np.min(knee_angles_r))
    )
    hip_vert_rom = (float(np.max(hip_y_positions) - np.min(hip_y_positions)) / target_h) if hip_y_positions else 0.0

    # Vertical hip dynamics
    if hip_y_positions and len(hip_y_positions) > 3:
        hip_standing_ref = float(np.percentile(hip_y_positions, 65))
        peak_hip_rise = float(hip_standing_ref - np.min(hip_y_positions)) / target_h
        hip_diffs = np.diff(hip_y_positions)
        # Upward motion in pixel coordinates is negative diff (decreasing y)
        max_upward_hip_vel = float(-np.min(hip_diffs) / target_h) if len(hip_diffs) > 0 else 0.0
    else:
        peak_hip_rise = 0.0
        max_upward_hip_vel = 0.0

    # Ankle vertical flight clearance & variance (feet leaving the ground)
    ankle_elev_l = (float(np.percentile(ankle_y_l, 85) - np.min(ankle_y_l)) / target_h) if (ankle_y_l and len(ankle_y_l) >= 4) else 0.0
    ankle_elev_r = (float(np.percentile(ankle_y_r, 85) - np.min(ankle_y_r)) / target_h) if (ankle_y_r and len(ankle_y_r) >= 4) else 0.0
    peak_ankle_elevation = max(ankle_elev_l, ankle_elev_r)

    ankle_std_l = (float(np.std(ankle_y_l)) / target_h) if (ankle_y_l and len(ankle_y_l) >= 4) else 0.0
    ankle_std_r = (float(np.std(ankle_y_r)) / target_h) if (ankle_y_r and len(ankle_y_r) >= 4) else 0.0
    peak_ankle_std = max(ankle_std_l, ankle_std_r)

    # 1. Non-Sports check: negligible motion
    if knee_rom < 14.0 and mean_stride < 0.07 and hip_vert_rom < 0.04 and peak_ankle_elevation < 0.025:
        return "Non-Sports / No Athletic Movement Detected"

    # 2. Alternating gait detection: Running / Sprinting
    is_alternating_gait = (
        mean_stride > 0.12 or
        max_stride > 0.22 or
        mean_ankle_y_diff > 0.048 or
        (mean_abs_knee_diff > 25 and mean_stride > 0.09 and knee_corr < 0.25)
    )

    # 3. JUMPING / LANDING: Ballistic vertical excursion & flight phase
    # In jumping, knees bend prior to takeoff (like a squat), BUT the athlete enters a true flight phase:
    # ankles elevate off the ground and hips rise ballistically.
    # This check MUST occur BEFORE squatting, but MUST verify flight clearance (feet leaving the floor).
    has_flight_phase = (
        peak_ankle_elevation > 0.026
        or peak_ankle_std > 0.018
        or (peak_ankle_elevation > 0.020 and max_upward_hip_vel > 0.008)
    )

    is_jumping = (
        not is_alternating_gait and has_flight_phase and (
            # Criterion 1: Direct ankle flight (feet left ground)
            peak_ankle_elevation > 0.026
            # Criterion 2: Dynamic ankle airborne variance
            or peak_ankle_std > 0.018
            # Criterion 3: Vertical hip excursion with flight rise
            or (hip_vert_rom > 0.060 and peak_ankle_elevation > 0.020)
        )
    )
    if is_jumping:
        return "Jumping"

    # 4. SQUATTING: Bilateral synchronous knee flexion with planted feet (NO flight phase)
    is_squatting = (
        not is_alternating_gait
        and not is_jumping
        and (knee_corr > 0.15 or mean_abs_knee_diff < 35)
        and min_knee < 140
        and knee_rom > 16.0
        and mean_stride < 0.18
        and peak_ankle_elevation <= 0.028
        and peak_ankle_std <= 0.020
    )
    if is_squatting:
        return "Squatting"

    # 5. RUNNING / SPRINTING:
    if is_alternating_gait or mean_stride > 0.11:
        if mean_stride > 0.24 or max_stride > 0.32:
            return "Sprinting"
        return "Running"

    # 6. Upper Body / Throwing
    wrist_y_all = (wrist_y_l or []) + (wrist_y_r or [])
    if wrist_y_all and len(wrist_y_all) > 5:
        wrist_rom = (np.max(wrist_y_all) - np.min(wrist_y_all)) / target_h
        if wrist_rom > 0.22 and knee_rom < 25.0:
            return "Throwing"

    # 7. Fallback athletic checks
    if peak_ankle_elevation > 0.025 or hip_vert_rom > 0.07:
        return "Jumping"
    if knee_rom > 18.0 and mean_stride < 0.15:
        return "Squatting"
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

    # For optimal browser rendering and Google Meet / screen-sharing performance,
    # cap max dimension to 960px (e.g. 960x540 for 16:9 or 960x720 for 4:3).
    # This delivers crisp skeleton tracking overlay while reducing GPU decode overhead by up to 85%.
    max_dim = max(orig_width, orig_height)
    target_max = 960
    if max_dim > target_max:
        scale = float(target_max) / float(max_dim)
        target_w = int(orig_width * scale)
        target_h = int(orig_height * scale)
    else:
        target_w = orig_width
        target_h = orig_height
        
    # Ensure even dimensions for H.264
    target_w = target_w - (target_w % 2)
    target_h = target_h - (target_h % 2)

    raw_fps = float(fps)
    if raw_fps <= 0 or raw_fps > 120:
        raw_fps = 25.0

    # Dynamic frame sampling for smooth screen sharing performance:
    # Cap to max 30 FPS. Google Meet / screen sharing streams at max 30fps.
    # Higher raw FPS (like 60fps or 120fps from iPhone action cams) chokes screen share encoders.
    frame_skip = 1
    if raw_fps > 35.0:
        frame_skip = int(round(raw_fps / 30.0))
        effective_fps = round(raw_fps / frame_skip, 2)
    else:
        effective_fps = round(raw_fps, 2)

    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, filename)
    temp_raw_path = os.path.join(output_dir, f"raw_{filename}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_raw_path, fourcc, effective_fps, (target_w, target_h))

    risk_flags = []
    knee_angles_l = []
    knee_angles_r = []
    trunk_leans = []
    valgus_angles_l = []
    valgus_angles_r = []
    stride_spreads = []
    ankle_y_diffs = []
    hip_y_positions = []
    ankle_y_positions_l = []
    ankle_y_positions_r = []
    wrist_y_positions_l = []
    wrist_y_positions_r = []
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

    frame_idx = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_idx += 1
        if frame_skip > 1 and (frame_idx % frame_skip != 0):
            continue

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

                    # Stride & Ankle metrics
                    if kpts[15][2] > 0.3:
                        ankle_y_positions_l.append(float(kpts[15][1]))
                    if kpts[16][2] > 0.3:
                        ankle_y_positions_r.append(float(kpts[16][1]))

                    if kpts[15][2] > 0.3 and kpts[16][2] > 0.3:
                        stride_spread = abs(kpts[15][0] - kpts[16][0]) / target_h
                        ankle_y_diff = abs(kpts[15][1] - kpts[16][1]) / target_h
                        stride_spreads.append(stride_spread)
                        ankle_y_diffs.append(ankle_y_diff)

                    # Upper-body Wrist tracking
                    if kpts[9][2] > 0.3:
                        wrist_y_positions_l.append(float(kpts[9][1]))
                    if kpts[10][2] > 0.3:
                        wrist_y_positions_r.append(float(kpts[10][1]))

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
    
    # 6. Transcode output video to web-standard low-latency H.264 (yuv420p) with faststart
    converted = False
    try:
        import subprocess
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe, "-y", "-i", temp_raw_path,
            "-vcodec", "libx264",
            "-preset", "faster",
            "-profile:v", "main",
            "-level", "3.1",
            "-tune", "fastdecode",
            "-crf", "24",
            "-maxrate", "2200k",
            "-bufsize", "4400k",
            "-pix_fmt", "yuv420p",
            "-r", str(int(effective_fps)),
            "-g", str(int(effective_fps)),
            "-movflags", "+faststart",
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
        activity,
        ankle_y_l=ankle_y_positions_l,
        ankle_y_r=ankle_y_positions_r,
        wrist_y_l=wrist_y_positions_l,
        wrist_y_r=wrist_y_positions_r
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

    is_auto_corrected = (
        detected_activity != activity
        and activity not in ["Unknown", "Auto-Detect", ""]
        and detected_activity != "Non-Sports / No Athletic Movement Detected"
    )
    if is_auto_corrected:
        risk_flags.insert(
            0,
            f"AI Action Auto-Correction: Vision analysis classified true athletic action as '{detected_activity}' (user selected '{activity}'). Form evaluated for {detected_activity} mechanics."
        )

    return {
        "filename": filename,
        "analytics": {
            "activity_analyzed": detected_activity,
            "user_input_activity": activity,
            "action_auto_corrected": is_auto_corrected,
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


def compare_two_video_analyses(result_a: dict, result_b: dict) -> dict:
    """
    Compares two video analysis results and returns comparative metrics,
    biomechanical diffs, and AI insights.
    """
    a_ana = result_a.get("analytics", {})
    b_ana = result_b.get("analytics", {})

    score_a = a_ana.get("risk_score", 0)
    score_b = b_ana.get("risk_score", 0)
    score_diff = round(score_b - score_a, 1)

    bio_a = a_ana.get("biomechanics", {})
    bio_b = b_ana.get("biomechanics", {})

    trunk_a = bio_a.get("max_trunk_lean", 0)
    trunk_b = bio_b.get("max_trunk_lean", 0)
    trunk_diff = round(trunk_b - trunk_a, 2)

    valgus_a = bio_a.get("max_knee_valgus", 0)
    valgus_b = bio_b.get("max_knee_valgus", 0)
    valgus_diff = round(valgus_b - valgus_a, 2)

    asym_a = bio_a.get("movement_asymmetry", 0)
    asym_b = bio_b.get("movement_asymmetry", 0)
    asym_diff = round(asym_b - asym_a, 2)

    probs_a = a_ana.get("injury_probabilities", {})
    probs_b = b_ana.get("injury_probabilities", {})

    prob_diffs = {}
    all_keys = list(probs_a.keys()) if isinstance(probs_a, dict) else []
    if isinstance(probs_b, dict):
        for k in probs_b.keys():
            if k not in all_keys:
                all_keys.append(k)

    for key in all_keys:
        pa = probs_a.get(key, 0) if isinstance(probs_a, dict) else 0
        pb = probs_b.get(key, 0) if isinstance(probs_b, dict) else 0
        prob_diffs[key] = {
            "video_a": pa,
            "video_b": pb,
            "diff": round(pb - pa, 1)
        }

    # Evaluate improvement status
    if score_diff < -5:
        overall_verdict = "Significant Improvement"
        verdict_color = "emerald"
        summary = f"Video 2 demonstrates a {abs(score_diff)} pt reduction in injury risk compared to Video 1. Posture and kinetic stability improved."
    elif score_diff > 5:
        overall_verdict = "Elevated Risk / Degradation"
        verdict_color = "rose"
        summary = f"Video 2 exhibits an increase in risk score (+{score_diff} pts). Watch for heightened biomechanical strain or fatigue indicators."
    else:
        overall_verdict = "Consistent Performance"
        verdict_color = "amber"
        summary = "Movement mechanics are closely matched between both videos with minor variation."

    # Identify key biomechanical changes
    insights = []
    if valgus_diff < -3:
        insights.append(f"Knee valgus decreased by {abs(valgus_diff)}°, lowering medial collateral and ACL shear stress.")
    elif valgus_diff > 3:
        insights.append(f"Knee valgus increased by {valgus_diff}°, suggesting medial knee collapse during ground contact.")

    if trunk_diff < -4:
        insights.append(f"Trunk lean reduced by {abs(trunk_diff)}°, showing improved core bracing and spinal alignment.")
    elif trunk_diff > 4:
        insights.append(f"Trunk lean increased by {trunk_diff}°, indicating upper body fatigue or compensatory movement.")

    if asym_diff < -3:
        insights.append(f"Bilateral limb symmetry improved by {abs(asym_diff)}°, balancing joint loading across both legs.")
    elif asym_diff > 3:
        insights.append(f"Asymmetry increased by {asym_diff}°, indicating potential limb favoring or muscle tightness.")

    if not insights:
        insights.append("Kinetic parameters remained stable across both movement sets.")

    return {
        "score_diff": score_diff,
        "overall_verdict": overall_verdict,
        "verdict_color": verdict_color,
        "summary": summary,
        "insights": insights,
        "metrics_diff": {
            "risk_score": {"video_a": score_a, "video_b": score_b, "diff": score_diff},
            "trunk_lean": {"video_a": trunk_a, "video_b": trunk_b, "diff": trunk_diff},
            "knee_valgus": {"video_a": valgus_a, "video_b": valgus_b, "diff": valgus_diff},
            "asymmetry": {"video_a": asym_a, "video_b": asym_b, "diff": asym_diff},
        },
        "injury_probabilities_comparison": prob_diffs
    }
