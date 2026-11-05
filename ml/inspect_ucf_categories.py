import os
import glob

base = r"C:\Users\User\Downloads\Sprinting training\ucf_sports_actions\ucf action"
print("=== UCF Sports Action Categories ===")
total_vids = 0
for d in sorted(os.listdir(base)):
    p = os.path.join(base, d)
    if os.path.isdir(p):
        vids = glob.glob(os.path.join(p, "**", "*.avi"), recursive=True)
        total_vids += len(vids)
        print(f"  {d:25s}: {len(vids):3d} videos")
print(f"Total videos: {total_vids}")

