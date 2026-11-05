"""
Dataset Builder for 7-Class Sports Action Recognition
Builds clean, balanced dataset:
1. jumping
2. squatting
3. sprinting
4. landing
5. throwing
6. cutting_movements
7. sports_specific_drills
"""

import os
import glob
import shutil
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UCF_DIR = r"C:\Users\User\Downloads\UCF101\UCF-101"
HMDB_RUN_DIR = r"C:\Users\User\Downloads\HMDB51_cache\extracted_run"
HMDB_TURN_DIR = r"C:\Users\User\Downloads\HMDB51_cache\extracted_turn"
OUTPUT_DIR = os.path.join(BASE_DIR, "ml", "sports_dataset")

CLASSES = [
    "jumping",
    "squatting",
    "sprinting",
    "landing",
    "throwing",
    "cutting_movements",
    "sports_specific_drills"
]

def safe_link_or_copy(src, dst):
    if os.path.exists(dst):
        return
    try:
        os.link(src, dst)
    except Exception:
        shutil.copy2(src, dst)

def build_dataset():
    print(f"Building 7-class sports dataset in: {OUTPUT_DIR}")
    for c in CLASSES:
        os.makedirs(os.path.join(OUTPUT_DIR, c), exist_ok=True)

    counts = {c: 0 for c in CLASSES}

    # 1. SQUATTING
    # UCF101 BodyWeightSquats (112 clips)
    squat_vids = glob.glob(os.path.join(UCF_DIR, "BodyWeightSquats", "*.avi"))
    for v in squat_vids:
        dst = os.path.join(OUTPUT_DIR, "squatting", os.path.basename(v))
        safe_link_or_copy(v, dst)
        counts["squatting"] += 1
    # User's uploaded squat clips
    user_squat = [
        os.path.join(BASE_DIR, "backend", "uploads", "A person squatting.mp4"),
        os.path.join(BASE_DIR, "backend", "uploads", "A person squatting(2).mp4")
    ]
    for v in user_squat:
        if os.path.exists(v):
            dst = os.path.join(OUTPUT_DIR, "squatting", "user_" + os.path.basename(v))
            safe_link_or_copy(v, dst)
            counts["squatting"] += 1

    # 2. JUMPING
    # HighJump (123), LongJump (131), TrampolineJumping (119), JumpingJack (123)
    jump_sources = ["HighJump", "LongJump", "TrampolineJumping", "JumpingJack"]
    for cat in jump_sources:
        vids = sorted(glob.glob(os.path.join(UCF_DIR, cat, "*.avi")))
        # Take up to 80-90 per category for balance
        for v in vids[:85]:
            dst = os.path.join(OUTPUT_DIR, "jumping", os.path.basename(v))
            safe_link_or_copy(v, dst)
            counts["jumping"] += 1
    # User jumping clip
    u_jump = os.path.join(BASE_DIR, "backend", "uploads", "A person jumping.mp4")
    if os.path.exists(u_jump):
        dst = os.path.join(OUTPUT_DIR, "jumping", "user_jumping.mp4")
        safe_link_or_copy(u_jump, dst)
        counts["jumping"] += 1

    # 3. SPRINTING
    # HMDB51 run clips (132 clips)
    run_vids = glob.glob(os.path.join(HMDB_RUN_DIR, "*.avi"))
    for v in run_vids:
        dst = os.path.join(OUTPUT_DIR, "sprinting", "hmdb_" + os.path.basename(v))
        safe_link_or_copy(v, dst)
        counts["sprinting"] += 1
    # User running clips
    u_runs = glob.glob(os.path.join(BASE_DIR, "backend", "uploads", "A person running*.mp4"))
    for v in u_runs:
        dst = os.path.join(OUTPUT_DIR, "sprinting", "user_" + os.path.basename(v))
        safe_link_or_copy(v, dst)
        counts["sprinting"] += 1

    # 4. THROWING
    # BaseballPitch (150), Shotput (144), ThrowDiscus (130), JavelinThrow (117)
    throw_sources = ["BaseballPitch", "Shotput", "ThrowDiscus", "JavelinThrow"]
    for cat in throw_sources:
        vids = sorted(glob.glob(os.path.join(UCF_DIR, cat, "*.avi")))
        for v in vids[:85]:
            dst = os.path.join(OUTPUT_DIR, "throwing", os.path.basename(v))
            safe_link_or_copy(v, dst)
            counts["throwing"] += 1
    u_throw = os.path.join(BASE_DIR, "backend", "uploads", "A person throwing a shot put.mp4")
    if os.path.exists(u_throw):
        dst = os.path.join(OUTPUT_DIR, "throwing", "user_shotput.mp4")
        safe_link_or_copy(u_throw, dst)
        counts["throwing"] += 1

    # 5. SPORTS SPECIFIC DRILLS
    # SoccerJuggling (147), JumpRope (144), BoxingSpeedBag (134)
    drill_sources = ["SoccerJuggling", "JumpRope", "BoxingSpeedBag"]
    for cat in drill_sources:
        vids = sorted(glob.glob(os.path.join(UCF_DIR, cat, "*.avi")))
        for v in vids[:115]:
            dst = os.path.join(OUTPUT_DIR, "sports_specific_drills", os.path.basename(v))
            safe_link_or_copy(v, dst)
            counts["sports_specific_drills"] += 1

    # 6. CUTTING MOVEMENTS
    # HMDB51 turn clips (140 pivot / change of direction clips)
    turn_vids = glob.glob(os.path.join(HMDB_TURN_DIR, "*.avi"))
    for v in turn_vids:
        dst = os.path.join(OUTPUT_DIR, "cutting_movements", "hmdb_" + os.path.basename(v))
        safe_link_or_copy(v, dst)
        counts["cutting_movements"] += 1

    # 7. LANDING
    # Extract landing segments (descent + touchdown impact absorption) from HighJump and LongJump
    print("Extracting landing impact segments from jumping sequences...")
    hj_vids = sorted(glob.glob(os.path.join(UCF_DIR, "HighJump", "*.avi")))
    for v in hj_vids:
        base = os.path.basename(v)
        dst = os.path.join(OUTPUT_DIR, "landing", "land_" + base)
        if os.path.exists(dst):
            counts["landing"] += 1
            continue
        try:
            cap = cv2.VideoCapture(v)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frames = []
            while cap.isOpened():
                ret, f = cap.read()
                if not ret: break
                frames.append(f)
            cap.release()

            if len(frames) >= 30:
                # HighJump landing is in terminal 45% of frames
                start_f = int(0.55 * len(frames))
                end_f = int(0.95 * len(frames))
                land_frames = frames[start_f:end_f]
                if len(land_frames) >= 15:
                    fourcc = int(cv2.VideoWriter.fourcc(*'XVID')) if hasattr(cv2.VideoWriter, 'fourcc') else getattr(cv2, 'VideoWriter_fourcc')(*'XVID')
                    out = cv2.VideoWriter(dst, fourcc, fps, (w, h))
                    for f in land_frames:
                        out.write(f)
                    out.release()
                    counts["landing"] += 1
        except Exception as e:
            pass

    print("\nDataset Build Summary:")
    print("-" * 40)
    for c in CLASSES:
        print(f"  {c:24s}: {counts[c]:4d} video clips")
    print("-" * 40)
    print(f"  Total video clips: {sum(counts.values())}")

if __name__ == "__main__":
    build_dataset()

