import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.video_processing import process_video_with_mediapipe

test_suite = [
    ('SPRINTING TEST', 'ml/sports_dataset/sprinting/hmdb_20060723sfjffangelina_run_f_cm_np2_fr_med_3.avi'),
    ('JUMPING TEST', 'ml/sports_dataset/jumping/user_jumping.mp4'),
    ('SQUATTING TEST', 'ml/sports_dataset/squatting/user_A person squatting.mp4'),
    ('THROWING TEST', 'ml/sports_dataset/throwing/v_BaseballPitch_g01_c01.avi'),
]

out_dir = 'backend/test_output'
os.makedirs(out_dir, exist_ok=True)

for label, vid_path in test_suite:
    print(f"\n==================== {label} ====================")
    if not os.path.exists(vid_path):
        print(f"File not found: {vid_path}")
        continue
    res = process_video_with_mediapipe(vid_path, out_dir, 'Unknown')
    ana = res['analytics']
    print('Primary Action:', ana['primary_action'])
    print('Performed Actions:', ana['performed_actions'])
    for item in ana['actions_breakdown']:
        print(f"  {item['action']:<25}: perf={str(item['performed']):<5} conf={item['confidence']}%, status={item['status']}")
    if 'actions_debug' in ana:
        print('Debug metrics:', ana['actions_debug'])
