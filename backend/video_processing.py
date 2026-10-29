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

def smooth(arr, window=5):
    if len(arr) < window:
        return np.array(arr)
    box = np.ones(window) / window
    return np.convolve(arr, box, mode='same')

def classify_all_actions(
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
    wrist_y_r=None,
    hip_x_positions=None,
    ankle_x_l=None,
    ankle_x_r=None,
    wrist_x_l=None,
    wrist_x_r=None,
    elbow_angles_l=None,
    elbow_angles_r=None,
    trunk_leans=None,
    head_tilts=None,
    fps=25.0
):
    """
    Evaluates footage across 7 specific athletic actions:
    1. Jumping
    2. Squatting
    3. Sprinting
    4. Landing
    5. Throwing
    6. Cutting Movements
    7. Sports Specific Drills
    Returns primary activity, performed list, and comprehensive per-action breakdown.
    """
    ACTION_NAMES = [
        "Jumping",
        "Squatting",
        "Sprinting",
        "Landing",
        "Throwing",
        "Cutting Movements",
        "Sports Specific Drills"
    ]

    dt = 1.0 / max(1.0, float(fps))

    # 0. Check for Non-Sports video (e.g. video resume, interview, bust shot)
    if athletic_pose_frames < 8 or person_detected_frames < 8 or not knee_angles_l or not knee_angles_r or len(knee_angles_l) < 5:
        breakdown = []
        for name in ACTION_NAMES:
            breakdown.append({
                "action": name,
                "performed": False,
                "confidence": 0.0,
                "status": "Not Detected",
                "biomechanical_evidence": "Full athletic kinetic chain not visible or no athletic movement in footage.",
                "key_metric": "Kinetic Chain: Not Visible"
            })
        return {
            "primary_action": "Non-Sports / No Athletic Movement Detected",
            "performed_actions": [],
            "breakdown": breakdown
        }

    athletic_ratio = athletic_pose_frames / max(1, person_detected_frames)
    if athletic_ratio < 0.20:
        breakdown = []
        for name in ACTION_NAMES:
            breakdown.append({
                "action": name,
                "performed": False,
                "confidence": 0.0,
                "status": "Not Detected",
                "biomechanical_evidence": "Kinetic lower-body joints insufficiently tracked across frames.",
                "key_metric": f"Tracking Ratio: {athletic_ratio*100:.0f}%"
            })
        return {
            "primary_action": "Non-Sports / No Athletic Movement Detected",
            "performed_actions": [],
            "breakdown": breakdown
        }

    # Signal arrays (normalized by target_h)
    norm_h = float(target_h)
    hip_y_arr = np.array(hip_y_positions) / norm_h if hip_y_positions else np.array([])
    hip_x_arr = np.array(hip_x_positions) / norm_h if hip_x_positions else np.array([])
    ank_l_y_arr = np.array(ankle_y_l) / norm_h if ankle_y_l else np.array([])
    ank_r_y_arr = np.array(ankle_y_r) / norm_h if ankle_y_r else np.array([])
    ank_l_x_arr = np.array(ankle_x_l) / norm_h if ankle_x_l else np.array([])
    ank_r_x_arr = np.array(ankle_x_r) / norm_h if ankle_x_r else np.array([])
    wrist_l_y_arr = np.array(wrist_y_l) / norm_h if wrist_y_l else np.array([])
    wrist_r_y_arr = np.array(wrist_r_y_l := wrist_y_r) / norm_h if wrist_y_r else np.array([])
    wrist_l_x_arr = np.array(wrist_x_l) / norm_h if wrist_x_l else np.array([])
    wrist_r_x_arr = np.array(wrist_x_r) / norm_h if wrist_x_r else np.array([])

    knee_l_arr = np.array(knee_angles_l) if knee_angles_l else np.array([])
    knee_r_arr = np.array(knee_angles_r) if knee_angles_r else np.array([])
    elbow_l_arr = np.array(elbow_angles_l) if elbow_angles_l else np.array([120.0])
    elbow_r_arr = np.array(elbow_angles_r) if elbow_angles_r else np.array([120.0])

    # 1. Ankle Velocities & Flight
    v_al = np.sqrt(np.diff(ank_l_x_arr)**2 + np.diff(ank_l_y_arr)**2) / dt if len(ank_l_x_arr) > 1 else np.array([0.0])
    v_ar = np.sqrt(np.diff(ank_r_x_arr)**2 + np.diff(ank_r_y_arr)**2) / dt if len(ank_r_x_arr) > 1 else np.array([0.0])
    peak_va = float(max(np.percentile(v_al, 95) if len(v_al) > 5 else 0.0, np.percentile(v_ar, 95) if len(v_ar) > 5 else 0.0))
    mean_va = float((np.mean(v_al) + np.mean(v_ar)) / 2.0) if (len(v_al) > 0 and len(v_ar) > 0) else 0.0

    # Bilateral flight clearance
    g_l = float(np.percentile(ank_l_y_arr, 85)) if len(ank_l_y_arr) > 5 else 1.0
    g_r = float(np.percentile(ank_r_y_arr, 85)) if len(ank_r_y_arr) > 5 else 1.0
    n_ank_y = min(len(ank_l_y_arr), len(ank_r_y_arr))
    if n_ank_y > 0:
        elev_l = np.maximum(0.0, g_l - ank_l_y_arr[:n_ank_y])
        elev_r = np.maximum(0.0, g_r - ank_r_y_arr[:n_ank_y])
        bilateral_elev = np.minimum(elev_l, elev_r)
        peak_bilat_flight = float(np.percentile(bilateral_elev, 95)) if len(bilateral_elev) > 5 else 0.0
        peak_single_flight = float(max(np.percentile(elev_l, 95), np.percentile(elev_r, 95)))
    else:
        peak_bilat_flight = 0.0
        peak_single_flight = 0.0

    # Stride spread & Gait alternations
    n_ank_x = min(len(ank_l_x_arr), len(ank_r_x_arr))
    if n_ank_x > 0:
        spreads = np.abs(ank_l_x_arr[:n_ank_x] - ank_r_x_arr[:n_ank_x])
        mean_stride = float(np.mean(spreads))
        max_stride = float(np.max(spreads))
        foot_diff = ank_l_x_arr[:n_ank_x] - ank_r_x_arr[:n_ank_x]
        sig_foot_diff = foot_diff[np.abs(foot_diff) > 0.06]
        gait_alternations = int(np.sum(np.diff(np.sign(sig_foot_diff)) != 0)) if len(sig_foot_diff) > 3 else 0
    else:
        mean_stride, max_stride, gait_alternations = 0.0, 0.0, 0

    # 2. Wrist Velocities & Upper Kinetic Chain
    v_wl = np.sqrt(np.diff(wrist_l_x_arr)**2 + np.diff(wrist_l_y_arr)**2) / dt if len(wrist_l_x_arr) > 1 else np.array([0.0])
    v_wr = np.sqrt(np.diff(wrist_r_x_arr)**2 + np.diff(wrist_r_y_arr)**2) / dt if len(wrist_r_x_arr) > 1 else np.array([0.0])
    peak_vw_l = float(np.percentile(v_wl, 95)) if len(v_wl) > 5 else float(np.max(v_wl)) if len(v_wl) > 0 else 0.0
    peak_vw_r = float(np.percentile(v_wr, 95)) if len(v_wr) > 5 else float(np.max(v_wr)) if len(v_wr) > 0 else 0.0
    peak_vw = max(peak_vw_l, peak_vw_r)
    wrist_v_asym = abs(peak_vw_l - peak_vw_r) / max(0.1, peak_vw)

    rom_wl = float(np.ptp(wrist_l_y_arr)) if len(wrist_l_y_arr) > 0 else 0.0
    rom_wr = float(np.ptp(wrist_r_y_arr)) if len(wrist_r_y_arr) > 0 else 0.0
    wrist_rom = max(rom_wl, rom_wr)

    n_w = min(len(wrist_l_y_arr), len(wrist_r_y_arr))
    wrist_corr = float(np.corrcoef(wrist_l_y_arr[:n_w], wrist_r_y_arr[:n_w])[0, 1]) if (n_w > 10 and np.std(wrist_l_y_arr[:n_w]) > 0.01 and np.std(wrist_r_y_arr[:n_w]) > 0.01) else 0.0

    elbow_rom = float(max(np.ptp(elbow_l_arr), np.ptp(elbow_r_arr))) if (len(elbow_l_arr) > 0 and len(elbow_r_arr) > 0) else 0.0

    # 3. Knee Kinematics
    n_k = min(len(knee_l_arr), len(knee_r_arr))
    min_k = float(min(np.min(knee_l_arr[:n_k]), np.min(knee_r_arr[:n_k]))) if n_k > 0 else 180.0
    rom_k = float(max(np.ptp(knee_l_arr[:n_k]), np.ptp(knee_r_arr[:n_k]))) if n_k > 0 else 0.0
    knee_corr = float(np.corrcoef(knee_l_arr[:n_k], knee_r_arr[:n_k])[0, 1]) if (n_k > 10 and np.std(knee_l_arr[:n_k]) > 1 and np.std(knee_r_arr[:n_k]) > 1) else 0.0
    mean_knee_diff = float(np.mean(np.abs(knee_l_arr[:n_k] - knee_r_arr[:n_k]))) if n_k > 0 else 0.0

    # 4. Hip Vertical & Lateral Displacements
    v_hy = np.diff(hip_y_arr) / dt if len(hip_y_arr) > 1 else np.array([0.0])
    up_v = float(-np.min(v_hy)) if len(v_hy) > 0 else 0.0
    down_v = float(np.max(v_hy)) if len(v_hy) > 0 else 0.0
    hip_vert_rom = float(np.ptp(hip_y_arr)) if len(hip_y_arr) > 0 else 0.0

    v_hx = np.diff(hip_x_arr) / dt if len(hip_x_arr) > 1 else np.array([0.0])
    a_hx = np.diff(v_hx) / dt if len(v_hx) > 1 else np.array([0.0])
    max_lat_accel = float(np.percentile(np.abs(a_hx), 98)) if len(a_hx) > 5 else 0.0
    sig_vhx = v_hx[np.abs(v_hx) > 0.02]
    lat_reversals = int(np.sum(np.diff(np.sign(sig_vhx)) != 0)) if len(sig_vhx) > 3 else 0

    # Overall non-sports check
    if rom_k < 14.0 and mean_stride < 0.06 and hip_vert_rom < 0.04 and peak_bilat_flight < 0.025 and peak_vw < 1.4:
        breakdown = []
        for name in ACTION_NAMES:
            breakdown.append({
                "action": name,
                "performed": False,
                "confidence": 0.0,
                "status": "Not Detected",
                "biomechanical_evidence": "Kinetic range of motion is negligible; no athletic sports movement pattern.",
                "key_metric": "Kinetic ROM: Negligible"
            })
        return {
            "primary_action": "Non-Sports / No Athletic Movement Detected",
            "performed_actions": [],
            "breakdown": breakdown
        }

    # ================= 7 SPECIFIC ACTIONS EVALUATION =================

    # Gait & Locomotion Characterization
    # Running/sprinting involves alternating swing/stance phases, high knee asymmetry (one leg flexed while other extended),
    # cyclical ankle velocity, and stride spread.
    req_act = (requested_activity or "").lower()
    is_alternating_gait = bool(
        (mean_knee_diff > 7.0 and (gait_alternations >= 1 or max_stride > 0.08 or mean_stride > 0.04)) or
        (gait_alternations >= 1) or
        (mean_knee_diff > 10.0) or
        (peak_va > 1.2 and (mean_stride > 0.04 or max_stride > 0.08)) or
        (peak_va > 1.4)
    )

    # 1. SPRINTING (High-Velocity / Locomotion / Running)
    sprint_perf = bool(
        # Alternating locomotion with moderate-to-high velocity or running flight
        (is_alternating_gait and (peak_va > 1.0 or peak_bilat_flight > 0.02 or mean_stride > 0.04 or rom_k > 25.0)) or
        (peak_va > 1.5 and (gait_alternations >= 1 or mean_knee_diff > 5.0 or mean_stride > 0.04)) or
        (peak_bilat_flight > 0.02 and is_alternating_gait) or
        (peak_va > 2.5) or
        # Requested activity confirmation with athletic locomotion telemetry
        (("sprint" in req_act or "run" in req_act) and (peak_va > 0.9 or is_alternating_gait or mean_stride > 0.04))
    )
    if sprint_perf:
        sprint_conf = round(min(99.5, max(75.0, (peak_va / 10.0) * 55 + (rom_k / 90.0) * 25 + 20)), 1)
        sprint_ev = f"High-velocity explosive sprint cadence confirmed (Peak swing velocity: {peak_va:.2f} H/s, Knee drive ROM: {rom_k:.0f}°, Stride gait: {mean_stride:.2f})."
    else:
        sprint_conf = round(min(45.0, (peak_va / 4.0) * 35.0), 1)
        sprint_ev = f"Cadence or stride velocity below maximal sprinting threshold (Peak swing velocity: {peak_va:.2f} H/s)."

    # 2. SQUATTING
    squat_perf = bool(peak_va < 1.2 and min_k < 100.0 and rom_k > 50.0 and peak_bilat_flight < 0.08 and peak_vw < 1.8 and not sprint_perf and not is_alternating_gait)
    if squat_perf:
        depth_score = max(0.0, (100.0 - min_k) / 40.0) * 45.0
        squat_conf = round(min(99.0, max(70.0, 40.0 + depth_score + (rom_k / 110.0) * 25.0)), 1)
        squat_ev = f"Planted-foot bilateral synchronous knee flexion confirmed (Squat depth: {min_k:.0f}°, Knee excursion ROM: {rom_k:.0f}°, zero flight)."
    else:
        squat_conf = round(min(40.0, (rom_k / 60.0) * 30.0 if (peak_va < 1.2 and not sprint_perf) else 5.0), 1)
        squat_ev = f"Incomplete squat depth or athlete engaged in ambulatory/flight motion (Min knee: {min_k:.0f}°, Knee ROM: {rom_k:.0f}°)."

    # 3. THROWING
    throw_perf = bool(
        (peak_vw > 2.0 and elbow_rom > 45.0 and peak_va > 1.1 and not sprint_perf and not squat_perf and not is_alternating_gait) or
        (peak_vw > 3.0 and elbow_rom > 55.0 and not sprint_perf and not squat_perf and wrist_corr < 0.45)
    )
    if throw_perf:
        throw_conf = round(min(98.5, max(70.0, (peak_vw / 4.0) * 50 + (elbow_rom / 150.0) * 30 + 20)), 1)
        throw_ev = f"Ballistic upper kinetic chain strike & arm extension confirmed (Peak wrist velocity: {peak_vw:.2f} H/s, Elbow ROM: {elbow_rom:.0f}°)."
    else:
        throw_conf = round(min(45.0, (peak_vw / 2.0) * 30.0 if not sprint_perf else 10.0), 1)
        throw_ev = f"Wrist velocity or arm extension below ballistic throwing threshold (Peak wrist velocity: {peak_vw:.2f} H/s)."

    # 4. JUMPING
    # A genuine jump features bilateral vertical impulse takeoff and synchronous leg action.
    # Alternating leg locomotion / running flight phases MUST NOT be classified as jumping.
    jump_perf = bool(
        (peak_bilat_flight > 0.09 or (peak_bilat_flight > 0.05 and up_v > 0.45 and (wrist_corr > 0.35 or knee_corr > 0.15)))
        and not is_alternating_gait
        and not sprint_perf
        and not squat_perf
        and not throw_perf
        and mean_knee_diff <= 8.0
        and max_stride <= 0.12
    )
    if jump_perf:
        jump_conf = round(min(99.0, max(70.0, (peak_bilat_flight / 0.18) * 50 + (up_v / 1.5) * 30 + 20)), 1)
        jump_ev = f"Bilateral airborne flight & vertical impulse takeoff confirmed (Flight clearance: {peak_bilat_flight*100:.1f}%, Upward takeoff velocity: {up_v:.2f} H/s)."
    else:
        jump_conf = round(min(45.0, (peak_bilat_flight / 0.10) * 35.0 if not sprint_perf else 8.0), 1)
        jump_ev = f"Insufficient bilateral airborne clearance ({peak_bilat_flight*100:.1f}%) and lack of vertical impulse takeoff."

    # 5. LANDING
    land_perf = bool(
        (jump_perf or (peak_bilat_flight > 0.06 and not is_alternating_gait) or (hip_vert_rom > 0.12 and mean_stride < 0.10 and not is_alternating_gait))
        and down_v > 0.55 and min_k < 142.0 and rom_k > 20.0 and not sprint_perf
    )
    if land_perf:
        land_conf = round(min(98.5, max(68.0, (down_v / 1.5) * 45 + (peak_bilat_flight / 0.15) * 35 + 20)), 1)
        land_ev = f"Ground touchdown impact absorption & knee deceleration confirmed (Descent velocity: {down_v:.2f} H/s, Absorption flexion: {min_k:.0f}°)."
    else:
        land_conf = round(min(40.0, (down_v / 0.55) * 25.0 if jump_perf else 8.0), 1)
        land_ev = "No vertical impact landing or knee ground deceleration phase observed."

    # 6. CUTTING MOVEMENTS
    cut_perf = bool((lat_reversals >= 1) and (max_lat_accel > 28.0) and (max_stride > 0.14) and not squat_perf and not throw_perf)
    if cut_perf:
        cut_conf = round(min(98.0, max(65.0, (max_lat_accel / 50.0) * 50 + (max_stride / 0.28) * 30 + 20)), 1)
        cut_ev = f"Sharp lateral plant-and-cut redirection observed (Peak lateral deceleration: {max_lat_accel:.1f} W/s², Reversals: {lat_reversals})."
    else:
        cut_conf = round(min(45.0, (max_lat_accel / 28.0) * 25.0 if lat_reversals >= 1 else 10.0), 1)
        cut_ev = "No abrupt lateral deceleration plant step or change of direction detected."

    # 7. SPORTS SPECIFIC DRILLS
    drill_perf = bool((lat_reversals >= 3 and max_lat_accel > 22.0 and rom_k > 30.0) and not squat_perf and not throw_perf)
    if drill_perf:
        drill_conf = round(min(97.0, max(65.0, (max_lat_accel / 50.0) * 40 + (mean_stride / 0.16) * 35 + (rom_k / 75.0) * 25)), 1)
        drill_ev = f"Agility drill footwork & dynamic multi-directional movement detected (Lateral agility index: {max_lat_accel:.1f}, Reversals: {lat_reversals})."
    else:
        drill_conf = round(min(40.0, (lat_reversals / 3.0) * 25.0 if lat_reversals > 0 else 10.0), 1)
        drill_ev = "Continuous agile foot turnover or multi-directional drill sequencing not detected."

    results = {
        "Jumping": {
            "performed": jump_perf,
            "confidence": jump_conf,
            "evidence": jump_ev,
            "key_metric": f"Flight Clearance: {peak_bilat_flight*100:.1f}%"
        },
        "Squatting": {
            "performed": squat_perf,
            "confidence": squat_conf,
            "evidence": squat_ev,
            "key_metric": f"Squat Depth: {min_k:.0f}°"
        },
        "Sprinting": {
            "performed": sprint_perf,
            "confidence": sprint_conf,
            "evidence": sprint_ev,
            "key_metric": f"Peak Sprint V: {peak_va:.2f} H/s"
        },
        "Landing": {
            "performed": land_perf,
            "confidence": land_conf,
            "evidence": land_ev,
            "key_metric": f"Touchdown Descent: {down_v:.2f} H/s"
        },
        "Throwing": {
            "performed": throw_perf,
            "confidence": throw_conf,
            "evidence": throw_ev,
            "key_metric": f"Wrist Velocity: {peak_vw:.2f} H/s"
        },
        "Cutting Movements": {
            "performed": cut_perf,
            "confidence": cut_conf,
            "evidence": cut_ev,
            "key_metric": f"Lateral Decel: {max_lat_accel:.1f} W/s²"
        },
        "Sports Specific Drills": {
            "performed": drill_perf,
            "confidence": drill_conf,
            "evidence": drill_ev,
            "key_metric": f"Agility Index: {max_lat_accel:.1f}"
        }
    }

    performed_list = [name for name, data in results.items() if data["performed"]]

    # Dominant Action Selection Hierarchy
    if squat_perf:
        primary_action = "Squatting"
    elif throw_perf:
        primary_action = "Throwing"
    elif sprint_perf:
        primary_action = "Sprinting"
    elif jump_perf and not is_alternating_gait:
        primary_action = "Jumping"
    elif land_perf and not is_alternating_gait:
        primary_action = "Landing"
    elif cut_perf:
        primary_action = "Cutting Movements"
    elif drill_perf:
        primary_action = "Sports Specific Drills"
    elif performed_list:
        primary_action = max(performed_list, key=lambda k: results[k]["confidence"])
    else:
        primary_action = "Athletic Movement"

    breakdown = []
    for name in ACTION_NAMES:
        item = results[name]
        breakdown.append({
            "action": name,
            "performed": item["performed"],
            "confidence": item["confidence"],
            "status": "Performed" if item["performed"] else "Not Detected",
            "biomechanical_evidence": item["evidence"],
            "key_metric": item["key_metric"]
        })

    return {
        "primary_action": primary_action,
        "performed_actions": performed_list,
        "breakdown": breakdown
    }

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
    """Backwards-compatible wrapper that returns the primary action string."""
    res = classify_all_actions(
        stride_spreads=stride_spreads,
        ankle_y_diffs=ankle_y_diffs,
        knee_angles_l=knee_angles_l,
        knee_angles_r=knee_angles_r,
        hip_y_positions=hip_y_positions,
        target_h=target_h,
        athletic_pose_frames=athletic_pose_frames,
        person_detected_frames=person_detected_frames,
        requested_activity=requested_activity,
        ankle_y_l=ankle_y_l,
        ankle_y_r=ankle_y_r,
        wrist_y_l=wrist_y_l,
        wrist_y_r=wrist_y_r
    )
    return res["primary_action"]

def process_video_with_mediapipe(
    video_path: str,
    arg2: str = "processed",
    arg3: str = "Auto-Detect",
    surface_type: str = "Unknown",
    footwear: str = "Unknown",
    rpe: int = 5,
    sleep_quality: int = 5
) -> dict:
    """
    Processes video using YOLOv8-pose with single/multi-person athlete tracking,
    extracts comprehensive kinetic angles, evaluates 8 specific actions, and renders
    a high-contrast kinetic HUD video with Web-compatible H.264 playback.
    """
    # Robustly handle either (video_path, "processed", activity) OR (video_path, activity, "processed")
    if str(arg2).lower() in ["processed", "scratch", "test_output", "output"] or os.path.isdir(str(arg2)):
        output_dir = str(arg2)
        activity = str(arg3)
    elif str(arg3).lower() in ["processed", "scratch", "test_output", "output"] or os.path.isdir(str(arg3)):
        activity = str(arg2)
        output_dir = str(arg3)
    else:
        output_dir = "processed"
        activity = str(arg2)

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video file: {video_path}")

    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if orig_width < 320 or orig_height < 240:
        cap.release()
        raise Exception(f"Video resolution too low: {orig_width}x{orig_height}. Minimum required is 320x240.")

    max_dim = max(orig_width, orig_height)
    target_max = 960
    if max_dim > target_max:
        scale = float(target_max) / float(max_dim)
        target_w = int(orig_width * scale)
        target_h = int(orig_height * scale)
    else:
        target_w = orig_width
        target_h = orig_height
        
    target_w = target_w - (target_w % 2)
    target_h = target_h - (target_h % 2)

    raw_fps = float(fps)
    if raw_fps <= 0 or raw_fps > 120:
        raw_fps = 25.0

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
    lateral_sways = []
    head_tilts = []
    pelvic_tilts = []
    shoulder_tilts = []
    elbow_angles_l = []
    elbow_angles_r = []
    shoulder_abductions_l = []
    shoulder_abductions_r = []

    valgus_angles_l = []
    valgus_angles_r = []
    hip_flexions_l = []
    hip_flexions_r = []
    core_torsions = []
    stride_spreads = []
    ankle_y_diffs = []
    hip_y_positions = []
    hip_x_positions = []
    ankle_y_positions_l = []
    ankle_y_positions_r = []
    ankle_x_positions_l = []
    ankle_x_positions_r = []
    wrist_y_positions_l = []
    wrist_y_positions_r = []
    wrist_x_positions_l = []
    wrist_x_positions_r = []
    trajectory_points = []
    person_detected_frames = 0
    athletic_pose_frames = 0

    model = get_pose_model()
    prev_athlete_center = None

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

        if (frame.shape[1], frame.shape[0]) != (target_w, target_h):
            frame = cv2.resize(frame, (target_w, target_h))

        curr_trunk_lean = 0.0
        curr_valgus = 0.0
        ang_l_knee = None
        ang_r_knee = None
        has_athletic_joints = False
        mid_hip_y = None

        if model is not None:
            results = model(frame, imgsz=640, verbose=False)
            if results and len(results[0].keypoints.data) > 0:
                kpts_list = results[0].keypoints.data.cpu().numpy()
                boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []
                
                # Robust Primary Athlete Tracker (Multi-person support)
                best_idx = 0
                if prev_athlete_center is None:
                    if len(boxes) > 0:
                        areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
                        best_idx = int(np.argmax(areas))
                else:
                    dists = [np.linalg.norm(((k[11][:2] + k[12][:2]) / 2.0) - prev_athlete_center) for k in kpts_list]
                    best_idx = int(np.argmin(dists))

                kpts = kpts_list[best_idx]
                person_detected_frames += 1

                has_hips = (kpts[11][2] > 0.35 or kpts[12][2] > 0.35)
                has_legs = (kpts[13][2] > 0.3 or kpts[14][2] > 0.3 or kpts[15][2] > 0.3 or kpts[16][2] > 0.3)
                if has_hips and has_legs:
                    athletic_pose_frames += 1
                    has_athletic_joints = True

                # Draw Skeleton Bones
                for p1, p2, color in BONES:
                    if kpts[p1][2] > 0.35 and kpts[p2][2] > 0.35:
                        pt1 = (int(kpts[p1][0]), int(kpts[p1][1]))
                        pt2 = (int(kpts[p2][0]), int(kpts[p2][1]))
                        cv2.line(frame, pt1, pt2, color, 4, cv2.LINE_AA)

                # Draw Key Joints
                for j in KEY_JOINTS:
                    if kpts[j][2] > 0.35:
                        pt = (int(kpts[j][0]), int(kpts[j][1]))
                        cv2.circle(frame, pt, 8, (0, 0, 255), -1, cv2.LINE_AA)
                        cv2.circle(frame, pt, 10, (255, 255, 255), 2, cv2.LINE_AA)

                # Compute Kinetic Angles & Metrics
                try:
                    if has_hips:
                        mid_hip_y = (kpts[11][1] + kpts[12][1]) / 2.0
                        mid_hip_x = (kpts[11][0] + kpts[12][0]) / 2.0
                        prev_athlete_center = np.array([mid_hip_x, mid_hip_y])
                        hip_y_positions.append(float(mid_hip_y))
                        hip_x_positions.append(float(mid_hip_x))

                        # Pelvic tilt (degrees from horizontal plane)
                        p_dx = abs(kpts[12][0] - kpts[11][0])
                        p_dy = abs(kpts[12][1] - kpts[11][1])
                        pelvic_tilt_deg = abs(float(np.degrees(np.arctan2(p_dy, max(1e-4, p_dx)))))
                        pelvic_tilts.append(pelvic_tilt_deg)

                    # Shoulder tilt (degrees from horizontal plane)
                    if kpts[5][2] > 0.3 and kpts[6][2] > 0.3:
                        s_dx = abs(kpts[6][0] - kpts[5][0])
                        s_dy = abs(kpts[6][1] - kpts[5][1])
                        shoulder_tilt_deg = abs(float(np.degrees(np.arctan2(s_dy, max(1e-4, s_dx)))))
                        shoulder_tilts.append(shoulder_tilt_deg)
                        if has_hips and len(pelvic_tilts) > 0:
                            core_torsions.append(abs(shoulder_tilt_deg - pelvic_tilts[-1]))

                    # Knee Angles
                    if kpts[11][2] > 0.3 and kpts[13][2] > 0.3 and kpts[15][2] > 0.3:
                        ang_l_knee = calculate_angle(kpts[11][:2], kpts[13][:2], kpts[15][:2])
                        knee_angles_l.append(ang_l_knee)
                        pt_lk = (int(kpts[13][0]) - 80, int(kpts[13][1]))
                        cv2.putText(frame, f"L:{int(ang_l_knee)}d", pt_lk, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2, cv2.LINE_AA)

                    if kpts[12][2] > 0.3 and kpts[14][2] > 0.3 and kpts[16][2] > 0.3:
                        ang_r_knee = calculate_angle(kpts[12][:2], kpts[14][:2], kpts[16][:2])
                        knee_angles_r.append(ang_r_knee)
                        pt_rk = (int(kpts[14][0]) + 15, int(kpts[14][1]))
                        cv2.putText(frame, f"R:{int(ang_r_knee)}d", pt_rk, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 130, 0), 2, cv2.LINE_AA)

                    # Hip Flexions (Shoulder-Hip-Knee)
                    if kpts[5][2] > 0.3 and kpts[11][2] > 0.3 and kpts[13][2] > 0.3:
                        hip_flexions_l.append(calculate_angle(kpts[5][:2], kpts[11][:2], kpts[13][:2]))
                    if kpts[6][2] > 0.3 and kpts[12][2] > 0.3 and kpts[14][2] > 0.3:
                        hip_flexions_r.append(calculate_angle(kpts[6][:2], kpts[12][:2], kpts[14][:2]))

                    # Elbow Angles
                    if kpts[5][2] > 0.3 and kpts[7][2] > 0.3 and kpts[9][2] > 0.3:
                        ang_el = calculate_angle(kpts[5][:2], kpts[7][:2], kpts[9][:2])
                        elbow_angles_l.append(ang_el)
                    if kpts[6][2] > 0.3 and kpts[8][2] > 0.3 and kpts[10][2] > 0.3:
                        ang_er = calculate_angle(kpts[6][:2], kpts[8][:2], kpts[10][:2])
                        elbow_angles_r.append(ang_er)

                    # Shoulder Abductions (Hip-Shoulder-Elbow)
                    if kpts[11][2] > 0.3 and kpts[5][2] > 0.3 and kpts[7][2] > 0.3:
                        shoulder_abductions_l.append(calculate_angle(kpts[11][:2], kpts[5][:2], kpts[7][:2]))
                    if kpts[12][2] > 0.3 and kpts[6][2] > 0.3 and kpts[8][2] > 0.3:
                        shoulder_abductions_r.append(calculate_angle(kpts[12][:2], kpts[6][:2], kpts[8][:2]))

                    # Trunk Lean & Lateral Sway
                    if kpts[5][2] > 0.3 and kpts[6][2] > 0.3 and has_hips:
                        mid_shoulder = [(kpts[5][0] + kpts[6][0]) / 2.0, (kpts[5][1] + kpts[6][1]) / 2.0]
                        mid_hip = [(kpts[11][0] + kpts[12][0]) / 2.0, (kpts[11][1] + kpts[12][1]) / 2.0]
                        t_dx = abs(mid_shoulder[0] - mid_hip[0])
                        t_dy = max(1e-4, abs(mid_hip[1] - mid_shoulder[1]))
                        curr_trunk_lean = abs(float(np.degrees(np.arctan2(t_dx, t_dy))))
                        trunk_leans.append(curr_trunk_lean)
                        lateral_sways.append(abs(mid_shoulder[0] - mid_hip[0]) / target_h * 100.0)

                        # Head & Neck Tilt (acute angle from vertical)
                        if kpts[0][2] > 0.3:
                            n_dx = abs(kpts[0][0] - mid_shoulder[0])
                            n_dy = max(1e-4, abs(mid_shoulder[1] - kpts[0][1]))
                            head_tilt_deg = abs(float(np.degrees(np.arctan2(n_dx, n_dy))))
                            head_tilts.append(head_tilt_deg)

                    # Dynamic Knee Valgus (Frontal Plane Projection Angle / FPPA)
                    mid_body_x = (kpts[11][0] + kpts[12][0]) / 2.0 if has_hips else (kpts[5][0] + kpts[6][0]) / 2.0
                    if kpts[11][2] > 0.3 and kpts[13][2] > 0.3:
                        x_hip_l, y_hip_l = kpts[11][0], kpts[11][1]
                        x_knee_l, y_knee_l = kpts[13][0], kpts[13][1]
                        if kpts[15][2] > 0.3:
                            x_ank_l, y_ank_l = kpts[15][0], kpts[15][1]
                            denom_l = max(1.0, abs(y_ank_l - y_hip_l))
                            t_l = np.clip((y_knee_l - y_hip_l) / denom_l, 0.0, 1.0)
                            x_neut_l = x_hip_l + t_l * (x_ank_l - x_hip_l)
                            med_dir_l = 1.0 if mid_body_x > x_hip_l else -1.0
                            d_med_l = (x_knee_l - x_neut_l) * med_dir_l
                            valg_l = float(np.degrees(np.arctan2(max(0.0, d_med_l), denom_l))) * 1.8
                        else:
                            med_dir_l = 1.0 if mid_body_x > x_hip_l else -1.0
                            d_med_l = (x_knee_l - x_hip_l) * med_dir_l
                            valg_l = float(np.degrees(np.arctan2(max(0.0, d_med_l), max(1.0, y_knee_l - y_hip_l))))
                        valg_l = min(35.0, max(0.0, valg_l))
                        valgus_angles_l.append(valg_l)
                        curr_valgus = max(curr_valgus, valg_l)

                    if kpts[12][2] > 0.3 and kpts[14][2] > 0.3:
                        x_hip_r, y_hip_r = kpts[12][0], kpts[12][1]
                        x_knee_r, y_knee_r = kpts[14][0], kpts[14][1]
                        if kpts[16][2] > 0.3:
                            x_ank_r, y_ank_r = kpts[16][0], kpts[16][1]
                            denom_r = max(1.0, abs(y_ank_r - y_hip_r))
                            t_r = np.clip((y_knee_r - y_hip_r) / denom_r, 0.0, 1.0)
                            x_neut_r = x_hip_r + t_r * (x_ank_r - x_hip_r)
                            med_dir_r = 1.0 if mid_body_x > x_hip_r else -1.0
                            d_med_r = (x_knee_r - x_neut_r) * med_dir_r
                            valg_r = float(np.degrees(np.arctan2(max(0.0, d_med_r), denom_r))) * 1.8
                        else:
                            med_dir_r = 1.0 if mid_body_x > x_hip_r else -1.0
                            d_med_r = (x_knee_r - x_hip_r) * med_dir_r
                            valg_r = float(np.degrees(np.arctan2(max(0.0, d_med_r), max(1.0, y_knee_r - y_hip_r))))
                        valg_r = min(35.0, max(0.0, valg_r))
                        valgus_angles_r.append(valg_r)
                        curr_valgus = max(curr_valgus, valg_r)

                    # Ankle Positions & Stride Spread
                    if kpts[15][2] > 0.3:
                        ankle_y_positions_l.append(float(kpts[15][1]))
                        ankle_x_positions_l.append(float(kpts[15][0]))
                    if kpts[16][2] > 0.3:
                        ankle_y_positions_r.append(float(kpts[16][1]))
                        ankle_x_positions_r.append(float(kpts[16][0]))

                    if kpts[15][2] > 0.3 and kpts[16][2] > 0.3:
                        stride_spread = abs(kpts[15][0] - kpts[16][0]) / target_h
                        ankle_y_diff = abs(kpts[15][1] - kpts[16][1]) / target_h
                        stride_spreads.append(stride_spread)
                        ankle_y_diffs.append(ankle_y_diff)

                    # Wrists
                    if kpts[9][2] > 0.3:
                        wrist_y_positions_l.append(float(kpts[9][1]))
                        wrist_x_positions_l.append(float(kpts[9][0]))
                    if kpts[10][2] > 0.3:
                        wrist_y_positions_r.append(float(kpts[10][1]))
                        wrist_x_positions_r.append(float(kpts[10][0]))

                    # Foot Trajectory
                    lead_ankle = kpts[15] if kpts[15][2] > kpts[16][2] else kpts[16]
                    if lead_ankle[2] > 0.3:
                        trajectory_points.append((int(lead_ankle[0]), int(lead_ankle[1])))
                        if len(trajectory_points) > 30:
                            trajectory_points.pop(0)

                except Exception as e:
                    pass

        # Draw Trajectory Trail
        for i in range(1, len(trajectory_points)):
            thickness = max(1, int(i / 6))
            cv2.line(frame, trajectory_points[i-1], trajectory_points[i], (0, 230, 255), thickness, cv2.LINE_AA)

        # Draw On-Screen Biomechanical HUD Panel
        hud_w = min(470, target_w - 40)
        overlay = frame.copy()
        cv2.rectangle(overlay, (20, 20), (20 + hud_w, 155), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
        cv2.rectangle(frame, (20, 20), (20 + hud_w, 155), (71, 85, 105), 1)

        cv2.putText(frame, "AI BIOMECHANICAL & ACTION ENGINE", (35, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)
        
        if has_athletic_joints:
            if ang_l_knee and ang_r_knee and min(ang_l_knee, ang_r_knee) < 95 and curr_valgus < 18:
                action_hud = "SQUATTING [DEEP FLEXION]"
            elif len(wrist_y_positions_l) > 2 and len(wrist_y_positions_r) > 2:
                action_hud = "ATHLETIC KINETIC CHAIN"
            else:
                action_hud = "ATHLETIC READY STANCE"

            status_text = "OPTIMAL FORM" if curr_valgus <= 15 and curr_trunk_lean <= 30 else "RISK DETECTED"
            status_color = (0, 230, 115) if status_text == "OPTIMAL FORM" else (70, 70, 255)
            cv2.putText(frame, f"STATUS: {status_text}", (35, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"ACTION: {action_hud}", (35, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (56, 189, 248), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Trunk: {curr_trunk_lean:.1f}d | Valgus: {curr_valgus:.1f}d", (35, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (203, 213, 225), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "STATUS: NO ATHLETIC MOVEMENT", (35, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (148, 163, 184), 2, cv2.LINE_AA)
            cv2.putText(frame, "Full kinetic chain not in frame", (35, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (203, 213, 225), 1, cv2.LINE_AA)

        lead_foot = f"Frame: {person_detected_frames} | Kinetic: {athletic_pose_frames} | 8-Action AI"
        cv2.putText(frame, lead_foot, (35, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (148, 163, 184), 1, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()

    # Convert to standard Web-playable H.264 MP4
    converted = False
    try:
        import subprocess
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_raw_path,
            "-vcodec", "libx264",
            "-preset", "fast",
            "-crf", "28",
            "-maxrate", "1800k",
            "-bufsize", "3600k",
            "-pix_fmt", "yuv420p",
            "-profile:v", "baseline",
            "-level", "3.1",
            "-movflags", "+faststart",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            converted = True
            if os.path.exists(temp_raw_path):
                os.remove(temp_raw_path)
    except Exception as e:
        converted = False

    if not converted:
        if os.path.exists(temp_raw_path):
            os.replace(temp_raw_path, output_path)

    # 7. Multi-Action Recognition Engine Execution
    actions_result = classify_all_actions(
        stride_spreads=stride_spreads,
        ankle_y_diffs=ankle_y_diffs,
        knee_angles_l=knee_angles_l,
        knee_angles_r=knee_angles_r,
        hip_y_positions=hip_y_positions,
        target_h=target_h,
        athletic_pose_frames=athletic_pose_frames,
        person_detected_frames=person_detected_frames,
        requested_activity=activity,
        ankle_y_l=ankle_y_positions_l,
        ankle_y_r=ankle_y_positions_r,
        wrist_y_l=wrist_y_positions_l,
        wrist_y_r=wrist_y_positions_r,
        hip_x_positions=hip_x_positions,
        ankle_x_l=ankle_x_positions_l,
        ankle_x_r=ankle_x_positions_r,
        wrist_x_l=wrist_x_positions_l,
        wrist_x_r=wrist_x_positions_r,
        elbow_angles_l=elbow_angles_l,
        elbow_angles_r=elbow_angles_r,
        trunk_leans=trunk_leans,
        head_tilts=head_tilts,
        fps=effective_fps
    )
    detected_activity = actions_result["primary_action"]

    # Non-sports handler
    if detected_activity == "Non-Sports / No Athletic Movement Detected":
        return {
            "filename": filename,
            "analytics": {
                "activity_analyzed": "Non-Sports / No Athletic Movement Detected",
                "primary_action": "Non-Sports / No Athletic Movement Detected",
                "performed_actions": [],
                "actions_breakdown": actions_result["breakdown"],
                "actions_summary": "No athletic movement detected across the 8 standard sports actions.",
                "risk_score": 0,
                "risk_level": "N/A",
                "risk_flags": ["No athletic movement, exercise, or sports action detected in the video."],
                "corrective_recommendation": "Please upload a video containing athletic sports movements (such as jumping, squatting, sprinting, landing, throwing, cutting movements, or sports specific drills) with the athlete's full body visible.",
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
                "kinematics": {},
                "fps": fps,
                "frame_count": frame_count
            }
        }

    # Process athletic biomechanics
    avg_trunk_lean = float(np.mean(trunk_leans)) if trunk_leans else 0.0
    max_trunk_lean = float(np.max(trunk_leans)) if trunk_leans else 0.0
    
    avg_knee_l = float(np.mean(knee_angles_l)) if knee_angles_l else 180.0
    avg_knee_r = float(np.mean(knee_angles_r)) if knee_angles_r else 180.0
    min_knee_l = float(np.min(knee_angles_l)) if knee_angles_l else 180.0
    min_knee_r = float(np.min(knee_angles_r)) if knee_angles_r else 180.0
    
    max_valgus_l = float(np.max(valgus_angles_l)) if valgus_angles_l else 0.0
    max_valgus_r = float(np.max(valgus_angles_r)) if valgus_angles_r else 0.0
    max_valgus = max(max_valgus_l, max_valgus_r)
    
    biomechanical_deviations = 0
    movement_asymmetry = abs(avg_knee_l - avg_knee_r)
    
    if max_valgus > 15:
        risk_flags.append(f"High Knee Valgus Detected ({round(max_valgus, 1)} deg)")
        biomechanical_deviations += (max_valgus - 15) * 4
    if max_trunk_lean > 30:
        risk_flags.append(f"Excessive Trunk Lean ({round(max_trunk_lean, 1)} deg)")
        biomechanical_deviations += (max_trunk_lean - 30) * 2

    if movement_asymmetry > 15:
        risk_flags.append(f"High Movement Asymmetry ({round(movement_asymmetry, 1)} deg diff)")
        movement_asymmetry_score = 40
    else:
        movement_asymmetry_score = movement_asymmetry * 2

    training_load_score = (rpe / 10) * 100
    fatigue_score = ((10 - sleep_quality) / 10) * 100
    if rpe > 8 and sleep_quality < 5:
        risk_flags.append("Severe Fatigue Indicators Detected")
        
    historical_injury_score = 20
    
    # Weighted Risk Scoring Engine
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
        
    # Injury Probabilities
    injury_probs = {
        "ACL Injury": min(round(max_valgus * 3 + movement_asymmetry), 95),
        "Hamstring Injury": min(round(movement_asymmetry * 2 + fatigue_score * 0.5), 90),
        "Ankle Sprain": min(round(max_valgus * 1.5), 80),
        "Shoulder Injury": 10 if detected_activity not in ["Throwing"] else min(round(40 + training_load_score * 0.3), 90),
        "Lower Back Injury": min(round(max_trunk_lean * 2 + fatigue_score * 0.3), 85),
        "Overuse Injury": min(round((training_load_score + fatigue_score) * 0.8), 95)
    }
    
    if not risk_flags:
        risk_flags.append("Optimal Movement Patterns Detected")

    # Corrective Recommendations
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

    performed_str = ", ".join(actions_result["performed_actions"]) if actions_result["performed_actions"] else detected_activity
    actions_summary = f"Multi-Action Engine verified {len(actions_result['performed_actions'])} performed action(s): {performed_str}. Primary Action: {detected_activity}."

    # Comprehensive Kinematic Telemetry
    dt = 1.0 / max(1.0, float(effective_fps))
    v_al = np.sqrt(np.diff(ankle_x_positions_l)**2 + np.diff(ankle_y_positions_l)**2) / (dt * target_h) if len(ankle_x_positions_l) > 1 else np.array([0.0])
    v_ar = np.sqrt(np.diff(ankle_x_positions_r)**2 + np.diff(ankle_y_positions_r)**2) / (dt * target_h) if len(ankle_x_positions_r) > 1 else np.array([0.0])
    peak_ankle_v = round(float(max(np.percentile(v_al, 95) if len(v_al) > 5 else 0.0, np.percentile(v_ar, 95) if len(v_ar) > 5 else 0.0)), 2)

    v_wl = np.sqrt(np.diff(wrist_x_positions_l)**2 + np.diff(wrist_y_positions_l)**2) / (dt * target_h) if len(wrist_x_positions_l) > 1 else np.array([0.0])
    v_wr = np.sqrt(np.diff(wrist_x_positions_r)**2 + np.diff(wrist_y_positions_r)**2) / (dt * target_h) if len(wrist_x_positions_r) > 1 else np.array([0.0])
    peak_wrist_v = round(float(max(np.percentile(v_wl, 95) if len(v_wl) > 5 else 0.0, np.percentile(v_wr, 95) if len(v_wr) > 5 else 0.0)), 2)

    g_l = float(np.percentile(ankle_y_positions_l, 85)) if len(ankle_y_positions_l) > 5 else target_h
    g_r = float(np.percentile(ankle_y_positions_r, 85)) if len(ankle_y_positions_r) > 5 else target_h
    n_ank_y = min(len(ankle_y_positions_l), len(ankle_y_positions_r))
    if n_ank_y > 0:
        bilat_elev = np.minimum(np.maximum(0.0, g_l - np.array(ankle_y_positions_l[:n_ank_y])), np.maximum(0.0, g_r - np.array(ankle_y_positions_r[:n_ank_y]))) / target_h
        peak_flight = round(float(np.percentile(bilat_elev, 95)) * 100.0, 1)
    else:
        peak_flight = 0.0

    v_hy = np.diff(hip_y_positions) / (dt * target_h) if len(hip_y_positions) > 1 else np.array([0.0])
    max_up_v = round(float(-np.min(v_hy)), 2) if len(v_hy) > 0 else 0.0
    max_down_v = round(float(np.max(v_hy)), 2) if len(v_hy) > 0 else 0.0

    # Knee Angular Velocity (deg/s)
    knee_ang_v_l = np.abs(np.diff(knee_angles_l)) / dt if len(knee_angles_l) > 1 else np.array([0.0])
    knee_ang_v_r = np.abs(np.diff(knee_angles_r)) / dt if len(knee_angles_r) > 1 else np.array([0.0])
    peak_knee_ang_v = round(float(max(
        np.percentile(knee_ang_v_l, 95) if len(knee_ang_v_l) > 5 else 0.0,
        np.percentile(knee_ang_v_r, 95) if len(knee_ang_v_r) > 5 else 0.0
    )), 1)

    # Touchdown Impact Force (Estimated G-Force)
    estimated_impact_g = round(float(max(1.0, max_down_v * 9.81 / 3.2)), 2)

    # Movement Cadence (Steps per Minute)
    cadence_spm = round(float(len(ankle_y_diffs) / max(1.0, float(frame_count) * dt) * 60.0 / 2.0), 1) if frame_count > 10 else 0.0

    # Multi-component Bilateral Symmetry Index
    sym_knee = max(0.0, 100.0 - (abs(avg_knee_l - avg_knee_r) / 180.0) * 100.0)
    sym_valgus = max(0.0, 100.0 - abs(max_valgus_l - max_valgus_r) * 2.5)
    sym_ankle_v = 100.0
    if len(v_al) > 5 and len(v_ar) > 5:
        m_al = float(np.mean(v_al))
        m_ar = float(np.mean(v_ar))
        den = max(m_al, m_ar, 0.05)
        sym_ankle_v = max(0.0, 100.0 - (abs(m_al - m_ar) / den) * 50.0)
    bilat_sym = round(float(0.4 * sym_knee + 0.3 * sym_valgus + 0.3 * sym_ankle_v), 1)

    kinematics = {
        "head_tilt_mean": round(float(np.mean(head_tilts)), 1) if head_tilts else 0.0,
        "head_tilt_max": round(float(np.max(head_tilts)), 1) if head_tilts else 0.0,
        "trunk_lean_mean": round(avg_trunk_lean, 1),
        "trunk_lean_max": round(max_trunk_lean, 1),
        "lateral_sway_max": round(float(np.max(lateral_sways)), 1) if lateral_sways else 0.0,
        "pelvic_tilt_mean": round(float(np.mean(pelvic_tilts)), 1) if pelvic_tilts else 0.0,
        "shoulder_tilt_mean": round(float(np.mean(shoulder_tilts)), 1) if shoulder_tilts else 0.0,
        "core_torsion_mean": round(float(np.mean(core_torsions)), 1) if core_torsions else 0.0,
        "knee_flexion_l_mean": round(avg_knee_l, 1),
        "knee_flexion_l_min": round(min_knee_l, 1),
        "knee_flexion_r_mean": round(avg_knee_r, 1),
        "knee_flexion_r_min": round(min_knee_r, 1),
        "valgus_l_max": round(max_valgus_l, 1),
        "valgus_r_max": round(max_valgus_r, 1),
        "hip_flexion_l_mean": round(float(np.mean(hip_flexions_l)), 1) if hip_flexions_l else 0.0,
        "hip_flexion_r_mean": round(float(np.mean(hip_flexions_r)), 1) if hip_flexions_r else 0.0,
        "elbow_angle_l_mean": round(float(np.mean(elbow_angles_l)), 1) if elbow_angles_l else 0.0,
        "elbow_angle_r_mean": round(float(np.mean(elbow_angles_r)), 1) if elbow_angles_r else 0.0,
        "shoulder_abduction_l_mean": round(float(np.mean(shoulder_abductions_l)), 1) if shoulder_abductions_l else 0.0,
        "shoulder_abduction_r_mean": round(float(np.mean(shoulder_abductions_r)), 1) if shoulder_abductions_r else 0.0,
        "peak_wrist_velocity": peak_wrist_v,
        "peak_ankle_velocity": peak_ankle_v,
        "peak_knee_angular_velocity": peak_knee_ang_v,
        "flight_clearance_percent": peak_flight,
        "max_upward_velocity": max_up_v,
        "max_downward_velocity": max_down_v,
        "estimated_impact_g": estimated_impact_g,
        "cadence_spm": cadence_spm,
        "bilateral_symmetry_index": bilat_sym
    }

    return {
        "filename": filename,
        "analytics": {
            "activity_analyzed": detected_activity,
            "user_input_activity": activity,
            "action_auto_corrected": is_auto_corrected,
            "primary_action": detected_activity,
            "performed_actions": actions_result["performed_actions"],
            "actions_breakdown": actions_result["breakdown"],
            "actions_summary": actions_summary,
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
            "kinematics": kinematics,
            "fps": fps,
            "frame_count": frame_count
        }
    }


def compare_two_video_analyses(result_a: dict, result_b: dict) -> dict:
    """
    Compares two video analysis results and returns comprehensive comparative metrics,
    biomechanical diffs, cross-activity discrepancy detection, identical video advisory,
    and 8-action breakdown side-by-side matrices.
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

    frames_a = a_ana.get("frame_count", 0)
    frames_b = b_ana.get("frame_count", 0)
    fname_a = result_a.get("original_filename") or result_a.get("filename")
    fname_b = result_b.get("original_filename") or result_b.get("filename")

    # 1. Duplicate / Identical Video Detection
    is_identical_video = bool(
        (fname_a and fname_b and fname_a == fname_b and score_diff == 0) or
        (abs(frames_a - frames_b) <= 1 and abs(score_diff) == 0 and abs(valgus_diff) < 0.2 and abs(trunk_diff) < 0.2 and abs(asym_diff) < 0.2 and frames_a > 10)
    )
    identical_video_message = None
    if is_identical_video:
        identical_video_message = (
            "Notice: You have uploaded identical (or near-identical) video recordings for both Video 1 and Video 2. "
            "For meaningful biomechanical progress tracking, technique comparison, and risk progression, "
            "please upload two distinct videos—such as a baseline trial and a follow-up trial—of the same activity."
        )

    # 2. Cross-Activity Discrepancy Detection
    act_a = a_ana.get("activity_analyzed") or a_ana.get("primary_action", "Unknown")
    act_b = b_ana.get("activity_analyzed") or b_ana.get("primary_action", "Unknown")
    is_cross_activity = bool(act_a != act_b and act_a not in ["Unknown", ""] and act_b not in ["Unknown", ""])
    cross_activity_message = None
    if is_cross_activity:
        cross_activity_message = (
            f"Activity Discrepancy: Video 1 was classified as '{act_a}' while Video 2 was classified as '{act_b}'. "
            "Kinematic parameters and joint loading patterns reflect fundamentally distinct athletic disciplines. "
            "Cross-activity comparison is provided below for general posture and load evaluation."
        )

    # 3. Injury Probabilities Comparison
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

    # 4. Multi-Action Recognition Comparison
    actions_a = {item["action"]: item for item in a_ana.get("actions_breakdown", [])}
    actions_b = {item["action"]: item for item in b_ana.get("actions_breakdown", [])}
    
    actions_comparison = []
    all_action_keys = [
        "Jumping", "Squatting", "Sprinting",
        "Landing", "Throwing", "Cutting Movements", "Sports Specific Drills"
    ]
    for act in all_action_keys:
        act_a_data = actions_a.get(act, {"performed": False, "confidence": 0.0, "key_metric": "N/A"})
        act_b_data = actions_b.get(act, {"performed": False, "confidence": 0.0, "key_metric": "N/A"})
        actions_comparison.append({
            "action": act,
            "video_a_performed": act_a_data.get("performed", False),
            "video_a_confidence": act_a_data.get("confidence", 0.0),
            "video_a_metric": act_a_data.get("key_metric", "N/A"),
            "video_b_performed": act_b_data.get("performed", False),
            "video_b_confidence": act_b_data.get("confidence", 0.0),
            "video_b_metric": act_b_data.get("key_metric", "N/A"),
            "match": act_a_data.get("performed", False) == act_b_data.get("performed", False)
        })

    # 5. Full Kinematics Comparison
    kin_a = a_ana.get("kinematics", {})
    kin_b = b_ana.get("kinematics", {})
    kinematics_comparison = {}
    kin_metrics = [
        ("head_tilt_mean", "Head & Neck Tilt (deg)"),
        ("trunk_lean_mean", "Mean Trunk Lean (deg)"),
        ("trunk_lean_max", "Peak Trunk Lean (deg)"),
        ("lateral_sway_max", "Lateral Trunk Sway (% H)"),
        ("knee_flexion_l_min", "Left Knee Flexion (deg)"),
        ("knee_flexion_r_min", "Right Knee Flexion (deg)"),
        ("valgus_l_max", "Left Knee Valgus (deg)"),
        ("valgus_r_max", "Right Knee Valgus (deg)"),
        ("hip_flexion_l_mean", "Left Hip Flexion (deg)"),
        ("hip_flexion_r_mean", "Right Hip Flexion (deg)"),
        ("elbow_angle_l_mean", "Left Elbow Angle (deg)"),
        ("elbow_angle_r_mean", "Right Elbow Angle (deg)"),
        ("pelvic_tilt_mean", "Pelvic Tilt (deg)"),
        ("shoulder_tilt_mean", "Shoulder Tilt (deg)"),
        ("core_torsion_mean", "Core Torsion Disconnect (deg)"),
        ("peak_wrist_velocity", "Peak Wrist Velocity (H/s)"),
        ("peak_ankle_velocity", "Peak Ankle Velocity (H/s)"),
        ("peak_knee_angular_velocity", "Knee Angular Velocity (deg/s)"),
        ("flight_clearance_percent", "Flight Clearance (%)"),
        ("max_upward_velocity", "Takeoff Upward V (H/s)"),
        ("max_downward_velocity", "Touchdown Descent V (H/s)"),
        ("estimated_impact_g", "Touchdown Impact (G-Force)"),
        ("cadence_spm", "Movement Cadence (SPM)"),
        ("bilateral_symmetry_index", "Bilateral Symmetry Index (%)")
    ]
    for key, label in kin_metrics:
        va = kin_a.get(key, 0.0)
        vb = kin_b.get(key, 0.0)
        kinematics_comparison[key] = {
            "label": label,
            "video_a": va,
            "video_b": vb,
            "diff": round(vb - va, 2)
        }

    # 6. Improvement Verdict & Insights
    if is_identical_video:
        overall_verdict = "Identical Video Uploaded"
        verdict_color = "slate"
        summary = "Both video inputs are identical recordings. No technique variation or risk differential could be established."
    elif score_diff < -5:
        overall_verdict = "Significant Improvement"
        verdict_color = "emerald"
        summary = f"Video 2 demonstrates a {abs(score_diff)} pt reduction in injury risk compared to Video 1. Kinetic stability and alignment improved."
    elif score_diff > 5:
        overall_verdict = "Elevated Risk / Degradation"
        verdict_color = "rose"
        summary = f"Video 2 exhibits an increase in risk score (+{score_diff} pts). Watch for heightened joint shear stress or fatigue indicators."
    else:
        overall_verdict = "Consistent Performance"
        verdict_color = "amber"
        summary = "Movement mechanics are closely matched between both videos with minor variation."

    # 6. Structured Comparative Biomechanical Delta Engine
    improvements = []
    deteriorations = []
    neutral_observations = []

    # Risk Score
    if score_diff < -2:
        improvements.append(f"Injury Risk Score reduced by {abs(score_diff)} pts (from {score_a} to {score_b}), indicating lower musculoskeletal vulnerability.")
    elif score_diff > 2:
        deteriorations.append(f"Injury Risk Score increased by +{score_diff} pts (from {score_a} to {score_b}), reflecting elevated joint shear loading or movement fatigue.")
    else:
        neutral_observations.append(f"Injury Risk Score remained consistent ({score_a} vs {score_b}, diff: {score_diff:+} pts).")

    # Knee Valgus FPPA
    if valgus_diff < -1.5:
        improvements.append(f"Dynamic Knee Valgus decreased by {abs(valgus_diff):.1f}° (from {valgus_a:.1f}° to {valgus_b:.1f}°), significantly reducing ACL and medial meniscus strain during ground contact.")
    elif valgus_diff > 1.5:
        deteriorations.append(f"Dynamic Knee Valgus increased by +{valgus_diff:.1f}° (from {valgus_a:.1f}° to {valgus_b:.1f}°), indicating medial knee collapse and heightened ACL rupture susceptibility.")
    else:
        neutral_observations.append(f"Dynamic Knee Valgus showed stable medial alignment ({valgus_a:.1f}° vs {valgus_b:.1f}°).")

    # Trunk Lean
    if trunk_diff < -2.5:
        improvements.append(f"Forward Trunk Lean reduced by {abs(trunk_diff):.1f}° (from {trunk_a:.1f}° to {trunk_b:.1f}°), demonstrating improved upright spinal posture and core bracing.")
    elif trunk_diff > 2.5:
        deteriorations.append(f"Forward Trunk Lean increased by +{trunk_diff:.1f}° (from {trunk_a:.1f}° to {trunk_b:.1f}°), suggesting quadriceps/core fatigue or compensatory upper-body pitching.")
    else:
        neutral_observations.append(f"Trunk lean posture remained stable within functional tolerances ({trunk_a:.1f}° vs {trunk_b:.1f}°).")

    # Limb Asymmetry
    if asym_diff < -1.5:
        improvements.append(f"Bilateral Limb Asymmetry improved by {abs(asym_diff):.1f}° (from {asym_a:.1f}° to {asym_b:.1f}°), balancing eccentric impact absorption evenly between both limbs.")
    elif asym_diff > 1.5:
        deteriorations.append(f"Bilateral Limb Asymmetry widened by +{asym_diff:.1f}° (from {asym_a:.1f}° to {asym_b:.1f}°), alerting to unilateral limb favoring or compensatory offloading of the vulnerable side.")
    else:
        neutral_observations.append(f"Bilateral limb symmetry maintained even distribution ({asym_a:.1f}° vs {asym_b:.1f}°).")

    # Symmetry Index
    sym_diff = kinematics_comparison.get("bilateral_symmetry_index", {}).get("diff", 0.0)
    if sym_diff > 2.0:
        improvements.append(f"Bilateral Symmetry Index improved by +{sym_diff:.1f}% ({kin_a.get('bilateral_symmetry_index', 0)}% → {kin_b.get('bilateral_symmetry_index', 0)}%), mitigating injury risk from asymmetric gait loading.")
    elif sym_diff < -2.0:
        deteriorations.append(f"Bilateral Symmetry Index dropped by {abs(sym_diff):.1f}% ({kin_a.get('bilateral_symmetry_index', 0)}% → {kin_b.get('bilateral_symmetry_index', 0)}%), warning of uneven ground force absorption.")

    # Landing Touchdown Impact (G-Force)
    impact_diff = kinematics_comparison.get("estimated_impact_g", {}).get("diff", 0.0)
    if impact_diff < -0.3:
        improvements.append(f"Touchdown impact deceleration softened by {abs(impact_diff):.2f} G ({kin_a.get('estimated_impact_g', 0)} G → {kin_b.get('estimated_impact_g', 0)} G), reducing patellar tendon and ankle shock loading.")
    elif impact_diff > 0.3:
        deteriorations.append(f"Touchdown impact deceleration escalated by +{impact_diff:.2f} G ({kin_a.get('estimated_impact_g', 0)} G → {kin_b.get('estimated_impact_g', 0)} G), reflecting stiff-legged impact with deficient knee flexion cushioning.")

    # Flight Clearance
    flight_diff = kinematics_comparison.get("flight_clearance_percent", {}).get("diff", 0.0)
    if flight_diff > 2.0:
        improvements.append(f"Vertical flight clearance increased by +{flight_diff:.1f}% ({kin_a.get('flight_clearance_percent', 0)}% → {kin_b.get('flight_clearance_percent', 0)}%), demonstrating superior vertical impulse and concentric force production.")
    elif flight_diff < -2.0:
        deteriorations.append(f"Vertical flight clearance decreased by {abs(flight_diff):.1f}% ({kin_a.get('flight_clearance_percent', 0)}% → {kin_b.get('flight_clearance_percent', 0)}%), indicating diminished explosive takeoff power or fatigue.")

    # Action Transition Analysis
    if is_cross_activity:
        action_transition_summary = (
            f"Cross-Discipline Transition: Video 1 (past baseline) captured primary action '{act_a}' whereas Video 2 (present trial) captured '{act_b}'. "
            f"The athletic demands shifted from {act_a} kinetic mechanics to {act_b} mechanics. "
            f"Joint loading vectors shifted accordingly between horizontal ground acceleration and vertical shock absorption."
        )
    else:
        action_transition_summary = (
            f"Direct Technique Evaluation: Both Video 1 (past baseline) and Video 2 (present trial) captured '{act_a}'. "
            f"Comparative telemetry evaluates direct technical maturation, biomechanical efficiency, and neuromuscular control across sessions."
        )

    # Detailed Coaching Verdict
    if len(improvements) > len(deteriorations):
        detailed_coaching_verdict = (
            f"Overall Positive Progression: Video 2 (present trial) shows clear biomechanical progress with {len(improvements)} verified improvements "
            f"over Video 1. Lower joint shear stress, superior limb alignment, and controlled eccentric absorption reflect effective training adaptation."
        )
    elif len(deteriorations) > len(improvements):
        detailed_coaching_verdict = (
            f"Targeted Corrective Action Required: Video 2 (present trial) exhibits {len(deteriorations)} technical regressions compared to Video 1. "
            f"Priority focus should be placed on correcting {', '.join([d.split(' ')[0] for d in deteriorations[:2]])} through targeted neuromuscular control."
        )
    else:
        detailed_coaching_verdict = (
            "Equilibrium Baseline: Movement metrics across Video 1 and Video 2 exhibit balanced kinetic characteristics with consistent movement mechanics."
        )

    insights = improvements + deteriorations
    if not insights:
        insights = ["Kinetic parameters remained stable across both movement sets."]

    return {
        "score_diff": score_diff,
        "overall_verdict": overall_verdict,
        "verdict_color": verdict_color,
        "summary": summary,
        "insights": insights,
        "improvements": improvements,
        "deteriorations": deteriorations,
        "neutral_observations": neutral_observations,
        "action_transition_summary": action_transition_summary,
        "detailed_coaching_verdict": detailed_coaching_verdict,
        "is_identical_video": is_identical_video,
        "identical_video_message": identical_video_message,
        "is_cross_activity": is_cross_activity,
        "cross_activity_message": cross_activity_message,
        "actions_comparison": actions_comparison,
        "kinematics_comparison": kinematics_comparison,
        "metrics_diff": {
            "risk_score": {"video_a": score_a, "video_b": score_b, "diff": score_diff},
            "trunk_lean": {"video_a": trunk_a, "video_b": trunk_b, "diff": trunk_diff},
            "knee_valgus": {"video_a": valgus_a, "video_b": valgus_b, "diff": valgus_diff},
            "asymmetry": {"video_a": asym_a, "video_b": asym_b, "diff": asym_diff},
        },
        "injury_probabilities_comparison": prob_diffs
    }
