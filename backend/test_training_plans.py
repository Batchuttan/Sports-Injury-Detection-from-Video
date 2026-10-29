import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Testing Authentication...")
    login_res = requests.post(f"{BASE_URL}/token", data={"username": "demo@sportsai.com", "password": "password123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.status_code} {login_res.text}")
        sys.exit(1)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully.")

    # 1. Test recommendations for Throwing
    print("\n--- 1. Recommendations for Throwing ---")
    rec_throw = requests.get(f"{BASE_URL}/recommendations/Throwing", headers=headers).json()
    assert rec_throw["training_plan_ref"] == "throwing-scapular-stability", f"Expected throwing-scapular-stability, got {rec_throw['training_plan_ref']}"
    ex_names = [e["name"] for e in rec_throw["prescribed_exercises"]]
    print(f"Throwing plan ref: {rec_throw['training_plan_ref']}")
    print(f"Prescribed exercises: {ex_names}")
    assert "Prone Y-T-W Scapular Stabilizers" in ex_names, "Prone Y-T-W Scapular Stabilizers missing in throwing recommendations!"

    # 2. Test recommendations for Squatting
    print("\n--- 2. Recommendations for Squatting ---")
    rec_squat = requests.get(f"{BASE_URL}/recommendations/Squatting", headers=headers).json()
    assert rec_squat["training_plan_ref"] == "knee-valgus", f"Expected knee-valgus, got {rec_squat['training_plan_ref']}"
    ex_names_squat = [e["name"] for e in rec_squat["prescribed_exercises"]]
    print(f"Squatting plan ref: {rec_squat['training_plan_ref']}")
    print(f"Prescribed exercises: {ex_names_squat}")
    assert "Banded Monster Walks & Side Steps" in ex_names_squat

    # 3. Test recommendations for Sprinting
    print("\n--- 3. Recommendations for Sprinting ---")
    rec_sprint = requests.get(f"{BASE_URL}/recommendations/Sprinting", headers=headers).json()
    assert rec_sprint["training_plan_ref"] == "sprint-hamstring-resilience"
    print(f"Sprinting plan ref: {rec_sprint['training_plan_ref']}")

    # 4. Test recommendations for Running (consolidated into Sprinting)
    print("\n--- 4. Recommendations for Running (Maps to Sprinting) ---")
    rec_run = requests.get(f"{BASE_URL}/recommendations/Running", headers=headers).json()
    assert rec_run["training_plan_ref"] == "sprint-hamstring-resilience"
    print(f"Running mapped plan ref: {rec_run['training_plan_ref']}")

    # 5. Test recommendations for Jumping
    print("\n--- 5. Recommendations for Jumping ---")
    rec_jump = requests.get(f"{BASE_URL}/recommendations/Jumping", headers=headers).json()
    assert rec_jump["training_plan_ref"] == "landing-shock-absorption"
    print(f"Jumping plan ref: {rec_jump['training_plan_ref']}")

    # 6. Test recommendations for Cutting Movements
    print("\n--- 6. Recommendations for Cutting Movements ---")
    rec_cut = requests.get(f"{BASE_URL}/recommendations/Cutting%20Movements", headers=headers).json()
    assert rec_cut["training_plan_ref"] == "cutting-acl-protection"
    print(f"Cutting plan ref: {rec_cut['training_plan_ref']}")

    # 7. Test training plans list (all)
    print("\n--- 7. Training plans list (all) ---")
    all_plans_res = requests.get(f"{BASE_URL}/training/plans?include_completed=true", headers=headers).json()
    plan_ids = [p["plan_id"] for p in all_plans_res]
    print(f"Found {len(all_plans_res)} total plans: {plan_ids}")
    assert "throwing-scapular-stability" in plan_ids
    assert "knee-valgus" in plan_ids
    assert "sprint-hamstring-resilience" in plan_ids
    assert "running-impact-attenuation" not in plan_ids
    assert "landing-shock-absorption" in plan_ids
    assert "cutting-acl-protection" in plan_ids
    assert "core-stability" in plan_ids
    assert "post-match-recovery" in plan_ids

    # 8. Test throwing-scapular-stability plan detail
    print("\n--- 8. Detail for throwing-scapular-stability ---")
    detail_res = requests.get(f"{BASE_URL}/training/plans/throwing-scapular-stability", headers=headers).json()
    print(f"Title: {detail_res['title']}")
    print(f"Focus: {detail_res['focus']}")
    detail_exs = detail_res["exercises_detail"]
    print(f"Number of detailed exercises: {len(detail_exs)}")
    y_t_w = next((e for e in detail_exs if "Prone Y-T-W" in e["name"]), None)
    assert y_t_w is not None, "Prone Y-T-W Scapular Stabilizers is not in exercises_detail!"
    print(f"Verified exercise details for: {y_t_w['name']}, sets={y_t_w['sets']}, reps={y_t_w['reps']}, tempo={y_t_w['tempo']}")

    # 9. Toggle all exercises to complete -> verify auto-completion
    print("\n--- 9. Complete all exercises to test auto-removal ---")
    for ex in detail_exs:
        t_res = requests.post(
            f"{BASE_URL}/training/plans/throwing-scapular-stability/toggle-task",
            headers=headers,
            json={"exercise_name": ex["name"], "completed": True}
        ).json()
        print(f"Toggled {ex['name']} -> progress={t_res['progress_percent']}%, status={t_res['status']}")

    assert t_res["progress_percent"] == 100, f"Expected 100%, got {t_res['progress_percent']}"
    assert t_res["status"] == "Completed", f"Expected Completed status, got {t_res['status']}"

    # 10. Check active plans: throwing-scapular-stability must be REMOVED from active!
    print("\n--- 10. Check Active Plans (completed must be excluded) ---")
    active_plans = requests.get(f"{BASE_URL}/training/plans?status_filter=active", headers=headers).json()
    active_ids = [p["plan_id"] for p in active_plans]
    print(f"Active plans count: {len(active_ids)}")
    assert "throwing-scapular-stability" not in active_ids, "Completed plan should NOT be in active list!"
    print("Verified: Completed plan is automatically removed from active list!")

    # 11. Check completed plans: throwing-scapular-stability must be in completed list!
    print("\n--- 11. Check Completed Plans filter ---")
    completed_plans = requests.get(f"{BASE_URL}/training/plans?status_filter=completed", headers=headers).json()
    completed_ids = [p["plan_id"] for p in completed_plans]
    print(f"Completed plans count: {len(completed_ids)}")
    assert "throwing-scapular-stability" in completed_ids, "Completed plan should be in completed list!"
    print("Verified: Completed plan is correctly listed in completed plans!")

    # 12. Reactivate plan
    print("\n--- 12. Reactivate Plan ---")
    reactivate_res = requests.post(f"{BASE_URL}/training/plans/throwing-scapular-stability/reactivate", headers=headers).json()
    print(f"Reactivate result: {reactivate_res}")
    assert reactivate_res["progress_percent"] == 0
    assert reactivate_res["status"] == "Active"

    # 13. Verify it is back in active plans
    active_plans_after = requests.get(f"{BASE_URL}/training/plans?status_filter=active", headers=headers).json()
    active_ids_after = [p["plan_id"] for p in active_plans_after]
    assert "throwing-scapular-stability" in active_ids_after, "Reactivated plan should be back in active list!"
    print("Verified: Reactivated plan returned to active list at 0%!")

    print("\n==========================================")
    print("ALL 13 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
