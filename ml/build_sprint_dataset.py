"""
Sprint Activity Recognition Dataset Builder & Feature Extraction Pipeline
Extracts 95-dimensional kinematic pose sequences across 32 frames using YOLO pose.
Constructs binary dataset:
- Class 1: SPRINTING (UCF Sports Run-Side + Athletics Sprints)
- Class 2: NOT SPRINTING (UCF Sports Walking, Kicking, Lifting, Golf, Diving, Jumping, Squatting, Cutting)
"""

import os
import sys
import glob
import time
import cv2
import numpy as np
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UCF_SPORTS = r"C:\Users\User\Downloads\Sprinting training\ucf_sports_actions\ucf action"
SPORTS_DATASET = os.path.join(BASE_DIR, "ml", "sports_dataset")
OUTPUT_NPZ = os.path.join(BASE_DIR, "ml", "sprint_features.npz")

print("=" * 70)
print("BUILDING SPRINTING vs NOT SPRINTING DATASET")
print("=" * 70)

# Initialize YOLO pose model
print("Loading YOLOv8n-pose model...")
pose_model = YOLO("yolov8n-pose.pt")

# Collect Video Paths
sprinting_videos = []
# 1. UCF Sports Run-Side
run_side_path = os.path.join(UCF_SPORTS, "Run-Side")
if os.path.exists(run_side_path):
    sprinting_videos.extend(glob.glob(os.path.join(run_side_path, "**", "*.avi"), recursive=True))

# 2. Sports dataset sprinting
sprint_dataset_path = os.path.join(SPORTS_DATASET, "sprinting")
if os.path.exists(sprint_dataset_path):
    sprinting_videos.extend(glob.glob(os.path.join(sprint_dataset_path, "*.avi")))
    sprinting_videos.extend(glob.glob(os.path.join(sprint_dataset_path, "*.mp4")))

print(f"Total SPRINTING video candidates: {len(sprinting_videos)}")

not_sprinting_videos = []
# 1. UCF Sports Walk-Front
walk_path = os.path.join(UCF_SPORTS, "Walk-Front")
if os.path.exists(walk_path):
    not_sprinting_videos.extend(glob.glob(os.path.join(walk_path, "**", "*.avi"), recursive=True))

# 2. UCF Sports Other Activities (Lifting, Kicking, Golf, Diving, Swing)
for cat in ["Lifting", "Kicking-Front", "Kicking-Side", "Golf-Swing-Side", "Diving-Side", "Swing-Bench", "SkateBoarding-Front"]:
    p = os.path.join(UCF_SPORTS, cat)
    if os.path.exists(p):
        not_sprinting_videos.extend(glob.glob(os.path.join(p, "**", "*.avi"), recursive=True))

# 3. Diverse Non-Sprinting Activities from sports_dataset
for cat in ["jumping", "squatting", "throwing", "cutting_movements"]:
    p = os.path.join(SPORTS_DATASET, cat)
    if os.path.exists(p):
        vids = glob.glob(os.path.join(p, "*.avi")) + glob.glob(os.path.join(p, "*.mp4"))
        not_sprinting_videos.extend(vids[:25])  # Take 25 from each to balance classes

print(f"Total NOT SPRINTING video candidates: {len(not_sprinting_videos)}")

def calculate_angle(a, b, c):
    """Calculates 2D angle (deg) between three keypoints ABC at joint B."""
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba < 1e-4 or norm_bc < 1e-4:
        return 0.0
    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return float(angle)

def extract_video_features(video_path, n_frames=32):
    """
    Extracts 95-dimensional spatial-temporal kinematic feature sequence across 32 frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames < 8:
        cap.release()
        return None
        
    frame_indices = np.linspace(0, total_frames - 1, n_frames, dtype=int)
    frames = []
    
    current_idx = 0
    read_success = True
    while read_success and current_idx <= frame_indices[-1]:
        ret, frame = cap.read()
        if not ret:
            break
        if current_idx in frame_indices:
            frames.append(frame)
        current_idx += 1
    cap.release()
    
    if len(frames) < 8:
        return None
        
    # Pad to n_frames if short
    while len(frames) < n_frames:
        frames.append(frames[-1])
        
    # Process frames with YOLO pose
    feature_seq = np.zeros((n_frames, 95), dtype=np.float32)
    prev_kpts = None
    
    for i, frame in enumerate(frames):
        h, w = frame.shape[:2]
        results = pose_model(frame, imgsz=320, verbose=False)
        
        kpts = np.zeros((17, 3), dtype=np.float32)
        if results and len(results[0].keypoints.data) > 0:
            kpts_all = results[0].keypoints.data.cpu().numpy()
            # Pick person with highest mean confidence
            conf_means = [np.mean(k[:, 2]) for k in kpts_all]
            best_person = int(np.argmax(conf_means))
            kpts = kpts_all[best_person]
            
        coords = kpts[:, :2].copy()
        confs = kpts[:, 2].copy()
        
        # Normalize by torso size (distance between shoulders and hips)
        mid_shoulder = (coords[5] + coords[6]) / 2.0
        mid_hip = (coords[11] + coords[12]) / 2.0
        torso_len = np.linalg.norm(mid_shoulder - mid_hip)
        if torso_len < 10.0:
            torso_len = max(w, h) * 0.25
            
        # Center coordinates on mid-hip and normalize by torso length
        norm_coords = (coords - mid_hip) / torso_len
        
        # Velocities
        if prev_kpts is not None:
            vels = (norm_coords - prev_kpts)
        else:
            vels = np.zeros_like(norm_coords)
        prev_kpts = norm_coords.copy()
        
        # Kinematic angles:
        knee_l = calculate_angle(coords[11], coords[13], coords[15]) / 180.0
        knee_r = calculate_angle(coords[12], coords[14], coords[16]) / 180.0
        hip_l = calculate_angle(coords[5], coords[11], coords[13]) / 180.0
        hip_r = calculate_angle(coords[6], coords[12], coords[14]) / 180.0
        elbow_l = calculate_angle(coords[5], coords[7], coords[9]) / 180.0
        elbow_r = calculate_angle(coords[6], coords[8], coords[10]) / 180.0
        
        # Torso inclination angle relative to vertical
        torso_vec = mid_shoulder - mid_hip
        torso_incline = np.arctan2(abs(torso_vec[0]), abs(torso_vec[1]) + 1e-4) / (np.pi / 2.0)
        
        # Stride & Kinetic characteristics
        stride_spread = abs(norm_coords[16, 0] - norm_coords[15, 0])
        vertical_ankle_sep = abs(norm_coords[16, 1] - norm_coords[15, 1])
        pelvis_disp = np.linalg.norm(vels[11:13])
        
        # 34 normalized coords + 17 confs + 34 velocities + 7 angles + 3 stride/kinetic = 95 features
        feature_vec = np.concatenate([
            norm_coords.flatten(),             # 34
            confs,                              # 17
            vels.flatten(),                     # 34
            [knee_l, knee_r, hip_l, hip_r, elbow_l, elbow_r, torso_incline],  # 7
            [stride_spread, vertical_ankle_sep, pelvis_disp]                   # 3
        ]).astype(np.float32)
        
        feature_seq[i] = feature_vec
        
    return feature_seq

# Extract all features
all_features = []
all_labels = []
all_video_ids = []

print("\nExtracting features from SPRINTING videos...")
for idx, v_path in enumerate(sprinting_videos):
    feat = extract_video_features(v_path)
    if feat is not None:
        all_features.append(feat)
        all_labels.append(1)  # Class 1: SPRINTING
        all_video_ids.append(f"sprint_{idx}")
    if (idx + 1) % 25 == 0 or (idx + 1) == len(sprinting_videos):
        print(f"  Processed {idx + 1}/{len(sprinting_videos)} sprinting videos (Valid: {len(all_labels)})")

n_sprint = len(all_labels)
print(f"\nExtracted {n_sprint} valid SPRINTING sequences.")

print("\nExtracting features from NOT SPRINTING videos...")
for idx, v_path in enumerate(not_sprinting_videos):
    feat = extract_video_features(v_path)
    if feat is not None:
        all_features.append(feat)
        all_labels.append(0)  # Class 0: NOT SPRINTING
        all_video_ids.append(f"not_sprint_{idx}")
    if (idx + 1) % 25 == 0 or (idx + 1) == len(not_sprinting_videos):
        print(f"  Processed {idx + 1}/{len(not_sprinting_videos)} not-sprinting videos (Valid: {len(all_labels) - n_sprint})")

X = np.array(all_features, dtype=np.float32)
y = np.array(all_labels, dtype=np.int64)
v_ids = np.array(all_video_ids)

print("\n" + "=" * 70)
print("SPRINT DATASET SUMMARY:")
print(f"Total video samples: {len(X)}")
print(f"Feature tensor shape: {X.shape} (N_samples, 32 frames, 95 features)")
print(f"Class 1 (SPRINTING):     {np.sum(y == 1)}")
print(f"Class 0 (NOT SPRINTING): {np.sum(y == 0)}")
print("=" * 70)

# Save to NPZ
np.savez_compressed(OUTPUT_NPZ, features=X, labels=y, video_ids=v_ids)
print(f"Successfully saved dataset to: {OUTPUT_NPZ}")

