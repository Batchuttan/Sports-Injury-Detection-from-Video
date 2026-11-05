"""
Inspection script for Sprinting Training Datasets:
1. UCF Sports Actions: C:\\Users\\User\\Downloads\\Sprinting training\\ucf_sports_actions
2. AthletePose3D: C:\\Users\\User\\Downloads\\Sprinting training\\AthletePose3D-main
"""

import os
import glob

DATASET_ROOT = r"C:\Users\User\Downloads\Sprinting training"
UCF_SPORTS = os.path.join(DATASET_ROOT, "ucf_sports_actions")
ATHLETE_POSE = os.path.join(DATASET_ROOT, "AthletePose3D-main")

print("=" * 70)
print("INSPECTING SPRINTING DATASETS")
print("=" * 70)

# 1. UCF Sports Actions
print("\n--- 1. UCF SPORTS ACTIONS ---")
if os.path.exists(UCF_SPORTS):
    categories = [d for d in os.listdir(UCF_SPORTS) if os.path.isdir(os.path.join(UCF_SPORTS, d))]
    print(f"Found {len(categories)} directories / action categories in UCF Sports:")
    total_videos = 0
    cat_summary = {}
    for cat in sorted(categories):
        cat_path = os.path.join(UCF_SPORTS, cat)
        vids = glob.glob(os.path.join(cat_path, "**", "*.avi"), recursive=True) + \
               glob.glob(os.path.join(cat_path, "**", "*.mp4"), recursive=True) + \
               glob.glob(os.path.join(cat_path, "**", "*.mov"), recursive=True)
        txts = glob.glob(os.path.join(cat_path, "**", "*.txt"), recursive=True)
        cat_summary[cat] = {"videos": len(vids), "annotations": len(txts), "files": vids[:2]}
        total_videos += len(vids)
        print(f"  - {cat:20s}: {len(vids):3d} videos, {len(txts):3d} annotation files")
        if vids:
            print(f"      Sample: {os.path.relpath(vids[0], UCF_SPORTS)}")
    print(f"Total UCF Sports videos: {total_videos}")
else:
    print(f"UCF Sports directory not found at: {UCF_SPORTS}")

# 2. AthletePose3D
print("\n--- 2. ATHLETEPOSE3D ---")
if os.path.exists(ATHLETE_POSE):
    files = os.listdir(ATHLETE_POSE)
    print("Top-level files/dirs in AthletePose3D-main:")
    for f in sorted(files):
        p = os.path.join(ATHLETE_POSE, f)
        if os.path.isdir(p):
            sub_count = len(os.listdir(p))
            print(f"  [DIR]  {f} ({sub_count} items)")
        else:
            sz = os.path.getsize(p)
            print(f"  [FILE] {f} ({sz} bytes)")
            
    # Check for README or doc files
    readme_candidates = [f for f in files if "readme" in f.lower()]
    for r in readme_candidates:
        print(f"\n--- Reading {r} ---")
        try:
            with open(os.path.join(ATHLETE_POSE, r), "r", encoding="utf-8", errors="ignore") as rf:
                content = rf.read()
                print(content[:1500])
        except Exception as e:
            print("Error reading readme:", e)
            
    # Check if dataset files (.npz, .pkl, .h5, .json, .csv, .mp4, etc.) are present
    print("\nScanning AthletePose3D for dataset / data files:")
    for ext in ["*.npz", "*.pkl", "*.h5", "*.json", "*.csv", "*.mp4", "*.avi", "*.mat"]:
        found = glob.glob(os.path.join(ATHLETE_POSE, "**", ext), recursive=True)
        if found:
            print(f"  Found {len(found)} files matching {ext} (Sample: {os.path.basename(found[0])})")
else:
    print(f"AthletePose3D directory not found at: {ATHLETE_POSE}")

