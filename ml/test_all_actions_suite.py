import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.video_processing import process_video_with_mediapipe

test_suite = [
    ('SPRINTING TEST (HMDB)', 'ml/sports_dataset/sprinting/hmdb_20060723sfjffangelina_run_f_cm_np2_fr_med_3.avi'),
    ('JUMPING TEST (USER)', 'backend/uploads/A person jumping(2).mp4'),
    ('SQUATTING TEST (USER)', 'backend/uploads/A person squatting(3).mp4'),
    ('SPRINTING TEST (USER)', 'backend/uploads/A person running(3).mp4'),
    ('THROWING TEST (USER SHOT PUT)', 'backend/uploads/A person throwing a shot put(2).mp4'),
    ('THROWING TEST (BASEBALL PITCH)', 'ml/sports_dataset/throwing/v_BaseballPitch_g01_c01.avi'),
]

out_dir = 'backend/test_output'
os.makedirs(out_dir, exist_ok=True)

all_passed = True
for label, vid_path in test_suite:
    print(f"\n==================== {label} ====================")
    if not os.path.exists(vid_path):
        print(f"File not found: {vid_path}")
        continue
    res = process_video_with_mediapipe(vid_path, out_dir, 'Unknown')
    ana = res['analytics']
    primary = ana['primary_action']
    performed = ana['performed_actions']
    print(f"Primary Action: {primary}")
    print(f"Performed Actions: {performed}")
    for item in ana['actions_breakdown']:
        print(f"  {item['action']:<25}: perf={str(item['performed']):<5} conf={item['confidence']}%, status={item['status']}")
    
    # Check expected
    expected = label.split()[0]
    if expected.lower() not in primary.lower():
        print(f"FAILED: Expected {expected}, got {primary}")
        all_passed = False
    else:
        print(f"PASSED: {primary}")

print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
