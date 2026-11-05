"""
Feature Extractor for Spatial-Temporal Sports Activity Classification
Extracts 17-point kinematic pose sequences across 7 sports classes using YOLOv8-pose.
"""

import os
import sys
import glob
import re
from typing import Optional, List
import cv2
import numpy as np

# Ensure workspace root and ml directory are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
ML_DIR = os.path.dirname(os.path.abspath(__file__))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

DATASET_DIR = os.path.join(BASE_DIR, "ml", "sports_dataset")
OUTPUT_FILE = os.path.join(BASE_DIR, "ml", "dataset_features.npz")
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n-pose.pt")
if not os.path.exists(YOLO_MODEL_PATH):
    YOLO_MODEL_PATH = os.path.join(BASE_DIR, "backend", "yolov8n-pose.pt")

CLASSES = [
    "Jumping",
    "Squatting",
    "Sprinting",
    "Landing",
    "Throwing",
    "Cutting Movements",
    "Sports Specific Drills"
]

CLASS_TO_IDX = {c.lower().replace(" ", "_"): i for i, c in enumerate(CLASSES)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASSES)}

TARGET_SEQ_LEN = 32  # 32 temporal frames per sample

def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calculates angle between points a -> b -> c in degrees."""
    pt_a = np.asarray(a)
    pt_b = np.asarray(b)
    pt_c = np.asarray(c)
    radians = np.arctan2(pt_c[1] - pt_b[1], pt_c[0] - pt_b[0]) - np.arctan2(pt_a[1] - pt_b[1], pt_a[0] - pt_b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return float(angle)

def extract_group_id(filename: str) -> str:
    """Extract source group id (e.g. g01..g25) to prevent train/test data leakage."""
    m = re.search(r'_g(\d{2})_', filename)
    if m:
        return f"group_{m.group(1)}"
    m2 = re.search(r'hmdb_([a-zA-Z0-9]+)_', filename)
    if m2:
        return f"hmdb_{m2.group(1)}"
    return "group_other"

def process_single_video(video_path: str, yolo_model) -> Optional[np.ndarray]:
    """Extracts a (32, 95) kinematic feature sequence from a single video clip."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    dt = 1.0 / max(1.0, float(fps))
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames < 6:
        cap.release()
        return None

    if total_frames <= TARGET_SEQ_LEN:
        sample_indices = set(range(total_frames))
    else:
        sample_indices = set(np.linspace(0, total_frames - 1, TARGET_SEQ_LEN, dtype=int))

    sampled_frames: List[np.ndarray] = []
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx in sample_indices:
            h, w = frame.shape[:2]
            scale = 320.0 / max(h, w)
            frame_resized = cv2.resize(frame, (int(w * scale), int(h * scale)))
            sampled_frames.append(frame_resized)
        frame_idx += 1
    cap.release()

    if len(sampled_frames) < 6:
        return None

    results = yolo_model(sampled_frames, imgsz=320, verbose=False)
    
    seq_features: List[np.ndarray] = []
    prev_kpts = None
    
    for r in results:
        if len(r.keypoints.data) > 0:
            kpts = r.keypoints.data[0].cpu().numpy()  # (17, 3) [x, y, conf]
        else:
            kpts = np.zeros((17, 3), dtype=np.float32)

        h_box = float(r.orig_shape[0])
        norm_scale = max(1.0, h_box)
        
        xy_norm = kpts[:, :2] / norm_scale
        conf = kpts[:, 2:3]

        if prev_kpts is not None:
            vel = (xy_norm - (prev_kpts[:, :2] / norm_scale)) / dt
        else:
            vel = np.zeros_like(xy_norm)
        prev_kpts = kpts

        ang_lk = calculate_angle(kpts[11][:2], kpts[13][:2], kpts[15][:2]) / 180.0
        ang_rk = calculate_angle(kpts[12][:2], kpts[14][:2], kpts[16][:2]) / 180.0
        ang_lh = calculate_angle(kpts[5][:2], kpts[11][:2], kpts[13][:2]) / 180.0
        ang_rh = calculate_angle(kpts[6][:2], kpts[12][:2], kpts[14][:2]) / 180.0
        ang_le = calculate_angle(kpts[5][:2], kpts[7][:2], kpts[9][:2]) / 180.0
        ang_re = calculate_angle(kpts[6][:2], kpts[8][:2], kpts[10][:2]) / 180.0
        
        mid_sh = (kpts[5][:2] + kpts[6][:2]) / 2.0
        mid_hp = (kpts[11][:2] + kpts[12][:2]) / 2.0
        trunk_lean = abs(float(np.degrees(np.arctan2(abs(mid_sh[0] - mid_hp[0]), max(1e-4, abs(mid_hp[1] - mid_sh[1])))))) / 90.0

        ank_h_l = (h_box - kpts[15][1]) / norm_scale
        ank_h_r = (h_box - kpts[16][1]) / norm_scale
        flight_clearance = min(max(0.0, ank_h_l), max(0.0, ank_h_r))
        gait_spread = abs(kpts[15][0] - kpts[16][0]) / norm_scale
        hip_vert_v = float(vel[11, 1] + vel[12, 1]) / 2.0

        angles = np.array([ang_lk, ang_rk, ang_lh, ang_rh, ang_le, ang_re, trunk_lean], dtype=np.float32)
        kinetics = np.array([flight_clearance, gait_spread, hip_vert_v], dtype=np.float32)

        frame_feat = np.concatenate([xy_norm.flatten(), conf.flatten(), vel.flatten(), angles, kinetics])
        seq_features.append(frame_feat)

    seq_arr = np.array(seq_features, dtype=np.float32)
    
    if len(seq_arr) != TARGET_SEQ_LEN:
        indices = np.linspace(0, len(seq_arr) - 1, TARGET_SEQ_LEN)
        resampled = np.zeros((TARGET_SEQ_LEN, seq_arr.shape[1]), dtype=np.float32)
        for d in range(seq_arr.shape[1]):
            resampled[:, d] = np.interp(indices, np.arange(len(seq_arr)), seq_arr[:, d])
        seq_arr = resampled

    return seq_arr

def extract_all():
    from ultralytics import YOLO
    print(f"Loading YOLO model from: {YOLO_MODEL_PATH}")
    yolo_model = YOLO(YOLO_MODEL_PATH)
    
    all_features = []
    all_labels = []
    all_groups = []
    all_paths = []

    print("Beginning kinematic sequence extraction...")
    for class_folder in sorted(os.listdir(DATASET_DIR)):
        folder_path = os.path.join(DATASET_DIR, class_folder)
        if not os.path.isdir(folder_path):
            continue
        
        class_key = class_folder.lower()
        if class_key not in CLASS_TO_IDX:
            continue
        label_idx = CLASS_TO_IDX[class_key]
        class_name = IDX_TO_CLASS[label_idx]

        vids = glob.glob(os.path.join(folder_path, "*.*"))
        vids = [v for v in vids if v.lower().endswith(('.avi', '.mp4', '.mov', '.mkv'))]
        print(f"\nProcessing class: {class_name} ({len(vids)} clips)...")

        extracted_count = 0
        for i, vid in enumerate(vids):
            feat = process_single_video(vid, yolo_model)
            if feat is not None:
                all_features.append(feat)
                all_labels.append(label_idx)
                all_groups.append(extract_group_id(os.path.basename(vid)))
                all_paths.append(vid)
                extracted_count += 1
            if (i + 1) % 50 == 0 or (i + 1) == len(vids):
                print(f"  Processed {i+1}/{len(vids)} clips (extracted: {extracted_count})...")

    features_arr = np.array(all_features, dtype=np.float32)
    labels_arr = np.array(all_labels, dtype=np.int64)
    groups_arr = np.array(all_groups)
    paths_arr = np.array(all_paths)

    print("\nFeature Extraction Complete:")
    print("-" * 50)
    print(f"Features shape: {features_arr.shape}  [Samples, Frames, Features]")
    print(f"Labels shape:   {labels_arr.shape}")
    print(f"Unique groups:  {len(np.unique(groups_arr))}")
    for idx, cname in IDX_TO_CLASS.items():
        cnt = int(np.sum(labels_arr == idx))
        print(f"  {cname:24s}: {cnt} samples")
    print("-" * 50)

    np.savez_compressed(
        OUTPUT_FILE,
        features=features_arr,
        labels=labels_arr,
        groups=groups_arr,
        paths=paths_arr,
        classes=CLASSES
    )
    print(f"Saved dataset features to: {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_all()
