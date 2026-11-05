import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from backend.video_processing import process_video_with_mediapipe

test_vid = "ml/sports_dataset/sprinting/hmdb_20060723sfjffangelina_run_f_cm_np2_fr_med_3.avi"
out_dir = "backend/test_output"
os.makedirs(out_dir, exist_ok=True)

res = process_video_with_mediapipe(test_vid, out_dir, "Sprinting")
ana = res["analytics"]

print("=== INFERENCE RESULT ===")
print("Primary Action:", ana["primary_action"])
print("Performed Actions:", ana["performed_actions"])
print("\n--- Actions Breakdown ---")
for item in ana["actions_breakdown"]:
    print(f"  {item['action']:<25}: Performed={str(item['performed']):<5} Conf={item['confidence']}% | {item['key_metric']}")

print("\n--- Sprint Analysis ---")
print(json.dumps(ana.get("sprint_analysis"), indent=2))

print("\n--- ACL Biomechanical Model ---")
print(json.dumps(ana.get("acl_biomechanical_risk"), indent=2))
