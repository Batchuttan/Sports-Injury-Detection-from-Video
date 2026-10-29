import requests

BASE_URL = "http://127.0.0.1:8000"

def test_all():
    # Login as demo user
    res = requests.post(f"{BASE_URL}/token", data={"username": "demo@sportsai.com", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test settings
    s_res = requests.get(f"{BASE_URL}/user/settings", headers=headers)
    print("Settings GET:", s_res.status_code, s_res.json())
    assert s_res.status_code == 200

    u_res = requests.put(f"{BASE_URL}/user/settings", headers=headers, json={"email_alerts": False, "sound_effects": True})
    print("Settings PUT:", u_res.status_code, u_res.json())
    assert u_res.status_code == 200

    # 2. Test profile
    p_res = requests.get(f"{BASE_URL}/athlete/profile", headers=headers)
    print("Profile GET:", p_res.status_code, p_res.json())
    assert p_res.status_code == 200

    # 3. Test training plans
    tp_res = requests.get(f"{BASE_URL}/training/plans", headers=headers)
    print("Training Plans GET:", tp_res.status_code, len(tp_res.json()), "plans found")
    assert tp_res.status_code == 200
    assert len(tp_res.json()) >= 3

    # Test single plan detail
    tpd_res = requests.get(f"{BASE_URL}/training/plans/knee-valgus", headers=headers)
    print("Knee Valgus Detail GET:", tpd_res.status_code, tpd_res.json()["title"], "Progress:", tpd_res.json()["progress_percent"])
    assert tpd_res.status_code == 200

    # Test toggle task
    tt_res = requests.post(f"{BASE_URL}/training/plans/knee-valgus/toggle-task", headers=headers, json={"exercise_name": "Banded Side Steps", "completed": True})
    print("Toggle task POST:", tt_res.status_code, tt_res.json())
    assert tt_res.status_code == 200

    # 4. Test physical assessments
    pa_res = requests.get(f"{BASE_URL}/athlete/assessments", headers=headers)
    print("Physical assessments GET:", pa_res.status_code, len(pa_res.json()), "records found")
    assert pa_res.status_code == 200
    assert len(pa_res.json()) >= 4

    # 5. Test performance records
    pr_res = requests.get(f"{BASE_URL}/athlete/performance", headers=headers)
    print("Performance records GET:", pr_res.status_code, len(pr_res.json()), "records found")
    assert pr_res.status_code == 200
    assert len(pr_res.json()) >= 5

    # 6. Test historical analyses and detailed kinematics
    an_res = requests.get(f"{BASE_URL}/athlete/analyses", headers=headers)
    print("Analyses GET:", an_res.status_code, len(an_res.json()), "records found")
    assert an_res.status_code == 200
    assert len(an_res.json()) >= 1
    first_analysis = an_res.json()[0]
    first_id = first_analysis["id"]

    det_res = requests.get(f"{BASE_URL}/athlete/analyses/{first_id}", headers=headers)
    print("Analysis detail GET:", det_res.status_code, "Activity:", det_res.json()["activity"])
    assert det_res.status_code == 200
    kinematics = det_res.json()["kinematics"]
    print("Kinematics keys count:", len(kinematics))
    assert "knee_flexion_l_min" in kinematics
    assert "knee_flexion_r_min" in kinematics
    assert "valgus_l_max" in kinematics
    assert "valgus_r_max" in kinematics
    assert "peak_ankle_velocity" in kinematics
    assert "flight_clearance_percent" in kinematics
    assert "peak_wrist_velocity" in kinematics
    assert "head_tilt_mean" in kinematics
    assert "trunk_lean_mean" in kinematics
    assert "elbow_angle_l_mean" in kinematics
    assert "shoulder_abduction_l_mean" in kinematics
    assert "hip_flexion_l_mean" in kinematics
    assert "core_torsion_mean" in kinematics
    assert "peak_knee_angular_velocity" in kinematics
    assert "estimated_impact_g" in kinematics
    assert "cadence_spm" in kinematics
    print("Kinematics check passed! All minute angles & telemetry present.")

    # 7. Test Dual Video Comparison (existing analyses)
    if len(an_res.json()) >= 2:
        id_a = an_res.json()[0]["id"]
        id_b = an_res.json()[1]["id"]
        cmp_res = requests.post(
            f"{BASE_URL}/video/compare-existing",
            headers=headers,
            json={"analysis_id_a": id_a, "analysis_id_b": id_b}
        )
        print("Compare existing POST:", cmp_res.status_code)
        assert cmp_res.status_code == 200
        cmp_json = cmp_res.json()
        assert "comparison" in cmp_json
        assert "kinematics_comparison" in cmp_json["comparison"]
        assert len(cmp_json["comparison"]["kinematics_comparison"]) >= 20
        cmp_data = cmp_json["comparison"]
        assert "improvements" in cmp_data
        assert "deteriorations" in cmp_data
        assert "neutral_observations" in cmp_data
        assert "action_transition_summary" in cmp_data
        assert "detailed_coaching_verdict" in cmp_data
        print("Comparison verified with", len(cmp_data["kinematics_comparison"]), "telemetry pairs!")
        print("Progression Report verified -> Improvements:", len(cmp_data["improvements"]), "| Deteriorations:", len(cmp_data["deteriorations"]), "| Neutral:", len(cmp_data["neutral_observations"]))

    # 8. Test Single Report PDF & CSV export
    pdf_res = requests.get(f"{BASE_URL}/athlete/analyses/{first_id}/export/pdf", headers=headers)
    print("Export Single PDF GET:", pdf_res.status_code, "Bytes:", len(pdf_res.content))
    assert pdf_res.status_code == 200
    assert len(pdf_res.content) > 1000

    csv_res = requests.get(f"{BASE_URL}/athlete/analyses/{first_id}/export/csv", headers=headers)
    print("Export Single CSV GET:", csv_res.status_code, "Bytes:", len(csv_res.content))
    assert csv_res.status_code == 200
    assert "Clinical Interpretation & Actionable Recommendation" in csv_res.text

    # 9. Test Activity Recommendations endpoint
    rec_throw = requests.get(f"{BASE_URL}/recommendations/Throwing", headers=headers)
    print("Recommendations Throwing GET:", rec_throw.status_code, rec_throw.json()["activity"])
    assert rec_throw.status_code == 200
    assert len(rec_throw.json()["primary_risk_factors"]) >= 2
    assert len(rec_throw.json()["prescribed_exercises"]) >= 2

    rec_squat = requests.get(f"{BASE_URL}/recommendations/Squatting", headers=headers)
    print("Recommendations Squatting GET:", rec_squat.status_code, rec_squat.json()["activity"])
    assert rec_squat.status_code == 200
    assert "Dynamic Knee Valgus" in str(rec_squat.json()["primary_risk_factors"])

    # 10. Test Clear Overview & Restore Overview
    clr_res = requests.post(f"{BASE_URL}/athlete/analyses/clear-overview", headers=headers)
    print("Clear Overview POST:", clr_res.status_code, clr_res.json()["success"])
    assert clr_res.status_code == 200
    ov_after_clr = requests.get(f"{BASE_URL}/athlete/analyses?overview_only=true", headers=headers)
    assert len(ov_after_clr.json()) == 0
    all_after_clr = requests.get(f"{BASE_URL}/athlete/analyses?overview_only=false", headers=headers)
    assert len(all_after_clr.json()) >= 1
    print("Clear overview verified: Overview count is 0 while permanent Reports count is", len(all_after_clr.json()))

    rst_res = requests.post(f"{BASE_URL}/athlete/analyses/restore-overview", headers=headers)
    print("Restore Overview POST:", rst_res.status_code, rst_res.json()["success"])
    assert rst_res.status_code == 200
    ov_after_rst = requests.get(f"{BASE_URL}/athlete/analyses?overview_only=true", headers=headers)
    assert len(ov_after_rst.json()) == len(all_after_clr.json())
    print("Restore overview verified! Overview count restored to", len(ov_after_rst.json()))

    # 11. Test Delete Analyses endpoint
    del_res = requests.post(f"{BASE_URL}/athlete/analyses/delete", headers=headers, json={"analysis_ids": [999999]})
    print("Delete analyses POST:", del_res.status_code, del_res.json())
    assert del_res.status_code == 200

    # 12. Test Dual Video Comparisons Archive & Exports
    comps_res = requests.get(f"{BASE_URL}/athlete/comparisons", headers=headers)
    print("Comparisons list GET:", comps_res.status_code, "Count:", len(comps_res.json()))
    assert comps_res.status_code == 200
    assert len(comps_res.json()) >= 1

    first_comp = comps_res.json()[0]
    cid = first_comp["id"]

    comp_detail = requests.get(f"{BASE_URL}/athlete/comparisons/{cid}", headers=headers)
    print("Comparison detail GET:", comp_detail.status_code, "Actions count:", len(comp_detail.json()["actions_comparison"]))
    assert comp_detail.status_code == 200
    assert len(comp_detail.json()["actions_comparison"]) >= 8
    assert len(comp_detail.json()["kinematics_comparison"]) >= 20

    dual_pdf = requests.get(f"{BASE_URL}/athlete/comparisons/{cid}/export/pdf", headers=headers)
    print("Dual PDF export GET:", dual_pdf.status_code, "Bytes:", len(dual_pdf.content))
    assert dual_pdf.status_code == 200
    assert len(dual_pdf.content) > 1000

    dual_csv = requests.get(f"{BASE_URL}/athlete/comparisons/{cid}/export/csv", headers=headers)
    print("Dual CSV export GET:", dual_csv.status_code, "Bytes:", len(dual_csv.content))
    assert dual_csv.status_code == 200
    assert "Clinical Evaluation & Coaching Prescription" in dual_csv.text

    del_comp = requests.post(f"{BASE_URL}/athlete/comparisons/delete", headers=headers, json={"comparison_ids": [999999]})
    print("Delete dual comparisons POST:", del_comp.status_code, del_comp.json())
    assert del_comp.status_code == 200

    print("ALL BACKEND ENDPOINTS PASSED VERIFICATION!")

if __name__ == "__main__":
    test_all()

