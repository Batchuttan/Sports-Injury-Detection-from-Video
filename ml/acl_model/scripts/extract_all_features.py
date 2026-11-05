"""
Complete Biomechanical Feature Extraction Engine for ACL Jump-Landing Dataset
Processes all 6 tasks (CMJ, DJ, SLH, COH, MRH, uCMJ) across all 43 participants and 2,199 trials.
Preserves participant IDs, task IDs, and fatigue states while avoiding any target leakage.
"""

import os
import sys
import time
import numpy as np
import scipy.io as sio
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
ANGLES_DIR = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")
PARTICIPANTS_DIR = os.path.join(DATASET_ROOT, "Participants")
OUTPUT_DIR = os.path.join(DATASET_ROOT, "ACL_Model_Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("PHASE 3 & 4: BIOMECHANICAL FEATURE EXTRACTION ENGINE")
print("=" * 70)

# 1. Load Participant Ground Truth Labels
log_path = os.path.join(PARTICIPANTS_DIR, "participant_log.xlsx")
df_log = pd.read_excel(log_path, header=0)
header_row = [str(c).strip() for c in df_log.iloc[0].values]
df_log.columns = header_row
df_log = df_log.iloc[1:].reset_index(drop=True)
df_log = df_log.dropna(how='all', subset=['participants'])
df_log['participants'] = df_log['participants'].astype(str).str.strip()

participant_labels = {}
for _, row in df_log.iterrows():
    p = row['participants']
    if p.startswith('sub'):
        sub_id = int(p.replace('sub', ''))
        grp_code = row['group (ACLG=1 ; CG=2)']
        # Group 1 = ACL Reconstruction (Previous ACL Injury)
        # Group 2 = Control Group (Healthy Control)
        is_acl = 1 if (grp_code == 1 or grp_code == '1') else 0
        participant_labels[sub_id] = {
            'participant_id': p,
            'sub_num': sub_id,
            'target': is_acl,
            'gender': row.get('Gender (female=1; male=2)', np.nan),
            'age': row.get('Age', np.nan),
            'height': row.get('Height (m)', np.nan),
            'weight': row.get('Weight (kg)', np.nan),
            'bmi': row.get('BMI', np.nan),
        }

print(f"Loaded ground-truth definitions for {len(participant_labels)} participants:")
n_acl = sum(1 for v in participant_labels.values() if v['target'] == 1)
n_cg = sum(1 for v in participant_labels.values() if v['target'] == 0)
print(f"  - Previous ACL Injury (target=1): {n_acl} participants")
print(f"  - Healthy Controls   (target=0): {n_cg} participants")

# Tasks mapping
TASK_SPECS = [
    {"name": "CMJ",  "file": "CMJ.mat",  "is_bilateral": True,  "desc": "Countermovement Jump"},
    {"name": "DJ",   "file": "DJ.mat",   "is_bilateral": True,  "desc": "Drop Jump"},
    {"name": "SLH",  "file": "SLH.mat",  "is_bilateral": False, "desc": "Single Leg Hop"},
    {"name": "COH",  "file": "COH.mat",  "is_bilateral": False, "desc": "Crossover Hop"},
    {"name": "MRH",  "file": "MRH.mat",  "is_bilateral": False, "desc": "Maximal Repeated Hops"},
    {"name": "uCMJ", "file": "uCMJ.mat", "is_bilateral": False, "desc": "Unanticipated CMJ"},
]

all_extracted_trials = []
task_summary = {}

for task in TASK_SPECS:
    task_name = task["name"]
    file_name = task["file"]
    mat_path = os.path.join(ANGLES_DIR, file_name)
    print(f"\nProcessing Task: {task_name} ({task['desc']})...")
    t0 = time.time()
    
    mat_data = sio.loadmat(mat_path)
    root_key = [k for k in mat_data.keys() if not k.startswith("__")][0]
    mat_arr = mat_data[root_key]
    
    n_subs, n_cols = mat_arr.shape
    task_trial_count = 0
    task_skipped_count = 0
    
    for r in range(n_subs):
        sub_id = r + 1
        if sub_id not in participant_labels:
            continue
        p_info = participant_labels[sub_id]
        
        for c in range(n_cols):
            limb_code = "bilateral" if task["is_bilateral"] else ("left" if c == 0 else "right")
            
            cell = mat_arr[r, c]
            if not (isinstance(cell, np.ndarray) and cell.size > 0 and cell.dtype.names):
                continue
                
            first_field = cell.dtype.names[0]
            struct_obj = cell[0, 0][first_field]
            if not (hasattr(struct_obj, 'dtype') and struct_obj.dtype.names and 'sub_data' in struct_obj.dtype.names):
                continue
                
            sub_data = struct_obj['sub_data'][0, 0]
            if not (hasattr(sub_data, 'size') and sub_data.size > 0):
                continue
                
            n_reps = sub_data.shape[0] if sub_data.ndim > 0 else 1
            
            for rep_idx in range(n_reps):
                rep_obj = sub_data[rep_idx, 0] if sub_data.ndim > 1 else sub_data[rep_idx]
                
                # Check for Joint_Angles
                if 'Joint_Angles' not in rep_obj.dtype.names:
                    task_skipped_count += 1
                    continue
                    
                ja = rep_obj['Joint_Angles']
                if ja.size == 0:
                    task_skipped_count += 1
                    continue

                # Flexible Initial Contact (IC) resolution
                ic_raw = None
                if 'IC' in rep_obj.dtype.names and rep_obj['IC'].size > 0:
                    ic_raw = rep_obj['IC']
                elif 'IC_K' in rep_obj.dtype.names and rep_obj['IC_K'].size > 0:
                    ic_raw = rep_obj['IC_K']
                elif 'IC_first_K' in rep_obj.dtype.names and rep_obj['IC_first_K'].size > 0:
                    ic_raw = rep_obj['IC_first_K']
                elif 'IC_A' in rep_obj.dtype.names and rep_obj['IC_A'].size > 0:
                    ic_raw = rep_obj['IC_A']
                
                if ic_raw is None or ic_raw.size == 0:
                    task_skipped_count += 1
                    continue
                    
                ic = int(ic_raw[0, 0]) if ic_raw.ndim > 0 else int(ic_raw)
                total_frames = ja.shape[0]
                
                # IC must be within valid frame range
                if ic <= 0 or ic >= total_frames:
                    task_skipped_count += 1
                    continue
                
                # Sampling frequency is 250 Hz (1 frame = 4 ms)
                # Landing impact phase: IC to IC + 25 frames (100 ms post-IC)
                # Full landing absorption phase: IC to min(IC + 62, total_frames) (250 ms post-IC)
                impact_end = min(ic + 25, total_frames)
                land_end = min(ic + 62, total_frames)
                
                land_window = ja[ic:land_end, :]
                impact_window = ja[ic:impact_end, :]
                
                if land_window.shape[0] < 5:
                    task_skipped_count += 1
                    continue
                
                # Fatigue state: typically rep 1-3 non-fatigued (0), rep 4-6 fatigued (1)
                is_fatigued = 1 if rep_idx >= 3 else 0
                
                # Extract Biomechanical Features
                # --- Knee Kinematics (Cols: R_flex=10, R_add=11, R_rot=12, L_flex=20, L_add=21, L_rot=22)
                knee_flex_ic_r = float(ja[ic, 10])
                knee_flex_peak_r = float(np.max(land_window[:, 10]))
                knee_flex_min_r = float(np.min(land_window[:, 10]))
                knee_flex_rom_r = knee_flex_peak_r - knee_flex_min_r
                
                knee_flex_ic_l = float(ja[ic, 20])
                knee_flex_peak_l = float(np.max(land_window[:, 20]))
                knee_flex_min_l = float(np.min(land_window[:, 20]))
                knee_flex_rom_l = knee_flex_peak_l - knee_flex_min_l
                
                # Knee Valgus/Adduction (Frontal plane excursion)
                knee_valg_ic_r = float(ja[ic, 11])
                knee_valg_peak_r = float(np.max(impact_window[:, 11]))
                knee_valg_rom_r = float(np.ptp(impact_window[:, 11]))
                
                knee_valg_ic_l = float(ja[ic, 21])
                knee_valg_peak_l = float(np.max(impact_window[:, 21]))
                knee_valg_rom_l = float(np.ptp(impact_window[:, 21]))
                
                # Knee Rotation (Transverse plane)
                knee_rot_ic_r = float(ja[ic, 12])
                knee_rot_peak_r = float(np.max(impact_window[:, 12]))
                knee_rot_ic_l = float(ja[ic, 22])
                knee_rot_peak_l = float(np.max(impact_window[:, 22]))
                
                # --- Hip Kinematics (Cols: R_flex=7, R_add=8, R_rot=9, L_flex=17, L_add=18, L_rot=19)
                hip_flex_ic_r = float(ja[ic, 7])
                hip_flex_peak_r = float(np.max(land_window[:, 7]))
                hip_flex_rom_r = float(np.ptp(land_window[:, 7]))
                
                hip_flex_ic_l = float(ja[ic, 17])
                hip_flex_peak_l = float(np.max(land_window[:, 17]))
                hip_flex_rom_l = float(np.ptp(land_window[:, 17]))
                
                hip_add_ic_r = float(ja[ic, 8])
                hip_add_peak_r = float(np.max(impact_window[:, 8]))
                hip_add_ic_l = float(ja[ic, 18])
                hip_add_peak_l = float(np.max(impact_window[:, 18]))
                
                hip_rot_peak_r = float(np.max(impact_window[:, 9]))
                hip_rot_peak_l = float(np.max(impact_window[:, 19]))
                
                # --- Ankle Kinematics (Cols: R_dorsi=14, R_subtalar=15, L_dorsi=24, L_subtalar=25)
                ankle_dorsi_ic_r = float(ja[ic, 14])
                ankle_dorsi_peak_r = float(np.max(land_window[:, 14]))
                ankle_dorsi_rom_r = float(np.ptp(land_window[:, 14]))
                
                ankle_dorsi_ic_l = float(ja[ic, 24])
                ankle_dorsi_peak_l = float(np.max(land_window[:, 24]))
                ankle_dorsi_rom_l = float(np.ptp(land_window[:, 24]))
                
                subtalar_peak_r = float(np.max(impact_window[:, 15]))
                subtalar_peak_l = float(np.max(impact_window[:, 25]))
                
                # --- Trunk & Pelvis (Cols: Pelvis_list=1, Pelvis_tilt=2, Pelvis_rot=3, Lumbar_ext=27, Lumbar_bend=28, Lumbar_rot=29)
                trunk_ext_ic = float(ja[ic, 27])
                trunk_ext_peak = float(np.max(land_window[:, 27]))
                trunk_ext_rom = float(np.ptp(land_window[:, 27]))
                
                trunk_bend_ic = float(ja[ic, 28])
                trunk_bend_peak = float(np.max(np.abs(impact_window[:, 28])))
                trunk_rot_peak = float(np.max(np.abs(impact_window[:, 29])))
                
                pelvis_tilt_peak = float(np.max(land_window[:, 2]))
                pelvis_list_peak = float(np.max(np.abs(impact_window[:, 1])))
                pelvis_rot_peak = float(np.max(np.abs(impact_window[:, 3])))
                
                # --- Bilateral Symmetry Indices (R vs L differences)
                asym_knee_flex_ic = abs(knee_flex_ic_r - knee_flex_ic_l)
                asym_knee_flex_peak = abs(knee_flex_peak_r - knee_flex_peak_l)
                asym_knee_valg_peak = abs(knee_valg_peak_r - knee_valg_peak_l)
                asym_hip_flex_peak = abs(hip_flex_peak_r - hip_flex_peak_l)
                asym_hip_add_peak = abs(hip_add_peak_r - hip_add_peak_l)
                asym_ankle_dorsi_peak = abs(ankle_dorsi_peak_r - ankle_dorsi_peak_l)
                
                # Hip-Knee Coordination Ratios (stiff vs compliant strategy)
                hip_knee_ratio_r = hip_flex_rom_r / (knee_flex_rom_r + 1e-4)
                hip_knee_ratio_l = hip_flex_rom_l / (knee_flex_rom_l + 1e-4)
                
                # Active Limb specific features (for unilateral hops)
                if limb_code == "left":
                    act_knee_flex_ic = knee_flex_ic_l
                    act_knee_flex_peak = knee_flex_peak_l
                    act_knee_valg_peak = knee_valg_peak_l
                    act_hip_add_peak = hip_add_peak_l
                    act_ankle_dorsi_peak = ankle_dorsi_peak_l
                elif limb_code == "right":
                    act_knee_flex_ic = knee_flex_ic_r
                    act_knee_flex_peak = knee_flex_peak_r
                    act_knee_valg_peak = knee_valg_peak_r
                    act_hip_add_peak = hip_add_peak_r
                    act_ankle_dorsi_peak = ankle_dorsi_peak_r
                else:
                    # Bilateral average
                    act_knee_flex_ic = 0.5 * (knee_flex_ic_r + knee_flex_ic_l)
                    act_knee_flex_peak = 0.5 * (knee_flex_peak_r + knee_flex_peak_l)
                    act_knee_valg_peak = 0.5 * (knee_valg_peak_r + knee_valg_peak_l)
                    act_hip_add_peak = 0.5 * (hip_add_peak_r + hip_add_peak_l)
                    act_ankle_dorsi_peak = 0.5 * (ankle_dorsi_peak_r + ankle_dorsi_peak_l)
                
                # --- Dynamic Center of Mass (COM) Metrics
                com_vz_ic = 0.0
                com_az_peak = 0.0
                com_v_res_ic = 0.0
                com_z_excursion = 0.0
                
                if 'COM_velocity' in rep_obj.dtype.names and rep_obj['COM_velocity'].size > 0:
                    cv = rep_obj['COM_velocity']
                    if ic < cv.shape[0]:
                        com_vz_ic = float(cv[ic, 2])
                        com_v_res_ic = float(np.linalg.norm(cv[ic, :]))
                        
                if 'COM_acceleration' in rep_obj.dtype.names and rep_obj['COM_acceleration'].size > 0:
                    ca = rep_obj['COM_acceleration']
                    if impact_end <= ca.shape[0]:
                        com_az_peak = float(np.max(np.abs(ca[ic:impact_end, 2])))
                        
                if 'COM_position' in rep_obj.dtype.names and rep_obj['COM_position'].size > 0:
                    cp = rep_obj['COM_position']
                    if land_end <= cp.shape[0]:
                        com_z_excursion = float(np.ptp(cp[ic:land_end, 2]))
                
                trial_dict = {
                    # Trial Identifiers & Grouping
                    "participant_id": p_info["participant_id"],
                    "sub_num": sub_id,
                    "task": task_name,
                    "limb": limb_code,
                    "rep": rep_idx + 1,
                    "is_fatigued": is_fatigued,
                    
                    # Target Label (0 = Healthy Control, 1 = Previous ACL Injury)
                    "target": p_info["target"],
                    
                    # Knee Biomechanical Features
                    "knee_flex_ic_r": knee_flex_ic_r,
                    "knee_flex_peak_r": knee_flex_peak_r,
                    "knee_flex_min_r": knee_flex_min_r,
                    "knee_flex_rom_r": knee_flex_rom_r,
                    
                    "knee_flex_ic_l": knee_flex_ic_l,
                    "knee_flex_peak_l": knee_flex_peak_l,
                    "knee_flex_min_l": knee_flex_min_l,
                    "knee_flex_rom_l": knee_flex_rom_l,
                    
                    "knee_valg_ic_r": knee_valg_ic_r,
                    "knee_valg_peak_r": knee_valg_peak_r,
                    "knee_valg_rom_r": knee_valg_rom_r,
                    
                    "knee_valg_ic_l": knee_valg_ic_l,
                    "knee_valg_peak_l": knee_valg_peak_l,
                    "knee_valg_rom_l": knee_valg_rom_l,
                    
                    "knee_rot_ic_r": knee_rot_ic_r,
                    "knee_rot_peak_r": knee_rot_peak_r,
                    "knee_rot_ic_l": knee_rot_ic_l,
                    "knee_rot_peak_l": knee_rot_peak_l,
                    
                    # Hip Biomechanical Features
                    "hip_flex_ic_r": hip_flex_ic_r,
                    "hip_flex_peak_r": hip_flex_peak_r,
                    "hip_flex_rom_r": hip_flex_rom_r,
                    "hip_flex_ic_l": hip_flex_ic_l,
                    "hip_flex_peak_l": hip_flex_peak_l,
                    "hip_flex_rom_l": hip_flex_rom_l,
                    
                    "hip_add_ic_r": hip_add_ic_r,
                    "hip_add_peak_r": hip_add_peak_r,
                    "hip_add_ic_l": hip_add_ic_l,
                    "hip_add_peak_l": hip_add_peak_l,
                    "hip_rot_peak_r": hip_rot_peak_r,
                    "hip_rot_peak_l": hip_rot_peak_l,
                    
                    # Ankle Biomechanical Features
                    "ankle_dorsi_ic_r": ankle_dorsi_ic_r,
                    "ankle_dorsi_peak_r": ankle_dorsi_peak_r,
                    "ankle_dorsi_rom_r": ankle_dorsi_rom_r,
                    "ankle_dorsi_ic_l": ankle_dorsi_ic_l,
                    "ankle_dorsi_peak_l": ankle_dorsi_peak_l,
                    "ankle_dorsi_rom_l": ankle_dorsi_rom_l,
                    "subtalar_peak_r": subtalar_peak_r,
                    "subtalar_peak_l": subtalar_peak_l,
                    
                    # Trunk & Pelvis Biomechanical Features
                    "trunk_ext_ic": trunk_ext_ic,
                    "trunk_ext_peak": trunk_ext_peak,
                    "trunk_ext_rom": trunk_ext_rom,
                    "trunk_bend_ic": trunk_bend_ic,
                    "trunk_bend_peak": trunk_bend_peak,
                    "trunk_rot_peak": trunk_rot_peak,
                    "pelvis_tilt_peak": pelvis_tilt_peak,
                    "pelvis_list_peak": pelvis_list_peak,
                    "pelvis_rot_peak": pelvis_rot_peak,
                    
                    # Asymmetry Features
                    "asym_knee_flex_ic": asym_knee_flex_ic,
                    "asym_knee_flex_peak": asym_knee_flex_peak,
                    "asym_knee_valg_peak": asym_knee_valg_peak,
                    "asym_hip_flex_peak": asym_hip_flex_peak,
                    "asym_hip_add_peak": asym_hip_add_peak,
                    "asym_ankle_dorsi_peak": asym_ankle_dorsi_peak,
                    
                    # Coordination
                    "hip_knee_ratio_r": hip_knee_ratio_r,
                    "hip_knee_ratio_l": hip_knee_ratio_l,
                    
                    # Active Limb Specific
                    "act_knee_flex_ic": act_knee_flex_ic,
                    "act_knee_flex_peak": act_knee_flex_peak,
                    "act_knee_valg_peak": act_knee_valg_peak,
                    "act_hip_add_peak": act_hip_add_peak,
                    "act_ankle_dorsi_peak": act_ankle_dorsi_peak,
                    
                    # COM Dynamic Kinetics
                    "com_vz_ic": com_vz_ic,
                    "com_az_peak": com_az_peak,
                    "com_v_res_ic": com_v_res_ic,
                    "com_z_excursion": com_z_excursion,
                }
                
                all_extracted_trials.append(trial_dict)
                task_trial_count += 1
                
    task_summary[task_name] = {
        "trials_extracted": task_trial_count,
        "trials_skipped": task_skipped_count,
        "time_s": round(time.time() - t0, 2)
    }
    print(f"Task {task_name}: Extracted {task_trial_count} trials ({task_skipped_count} skipped/missing) in {task_summary[task_name]['time_s']} s")

# Convert to DataFrame
df_features = pd.DataFrame(all_extracted_trials)
print(f"\nTotal Trials Extracted: {len(df_features)}")
print(f"Total Features per Trial: {df_features.shape[1]}")
print(f"Participant representation: {df_features['participant_id'].nunique()} participants")
print(f"Target breakdown:\n{df_features['target'].value_counts()}")

# Save to output folder
out_csv = os.path.join(OUTPUT_DIR, "extracted_biomechanical_features.csv")
df_features.to_csv(out_csv, index=False)
print(f"Successfully saved feature dataset to: {out_csv}")

