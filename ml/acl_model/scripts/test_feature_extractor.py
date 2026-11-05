"""
Feature Extraction Test Script for ACL Jump-Landing Dataset
Tests extracting biomechanical features from CMJ, DJ, and SLH trials.
"""

import os
import sys
import numpy as np
import scipy.io as sio
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
angles_dir = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")

# Load COH.mat
coh_path = os.path.join(angles_dir, "COH.mat")
data = sio.loadmat(coh_path)
coh_arr = data['COH']

# Participant sub01, Left leg (col 0), Rep 0
cell = coh_arr[0, 0]
struct_obj = cell[0, 0]['COH']
sub_data = struct_obj['sub_data'][0, 0]
rep0 = sub_data[0, 0] if sub_data.ndim > 1 else sub_data[0]

ic_val = int(rep0['IC'][0, 0])
ja = rep0['Joint_Angles']
com_v = rep0['COM_velocity']
com_a = rep0['COM_acceleration']

print(f"Sub01 COH Left Rep 0: IC={ic_val}, Total Frames={ja.shape[0]}")
# Landing window: IC to IC + 62 frames (250 ms)
ic = ic_val
win_end = min(ic + 62, ja.shape[0])
land_ja = ja[ic:win_end, :]

# Knee angles:
# Col 10: knee_angle_r, Col 11: knee_adduction_r, Col 12: knee_rotation_r
# Col 20: knee_angle_l, Col 21: knee_adduction_l, Col 22: knee_rotation_l
# Hip angles:
# Col 7: hip_flexion_r, Col 8: hip_adduction_r
# Col 17: hip_flexion_l, Col 18: hip_adduction_l
# Trunk angles:
# Col 27: lumbar_extension, Col 28: lumbar_bending, Col 29: lumbar_rotation

k_flex_l_ic = float(ja[ic, 20])
k_flex_l_peak = float(np.max(land_ja[:, 20]))
k_valg_l_ic = float(ja[ic, 21])
k_valg_l_peak = float(np.max(land_ja[:, 21]))

print(f"Knee Flexion (Left) at IC: {k_flex_l_ic:.2f} deg, Peak: {k_flex_l_peak:.2f} deg")
print(f"Knee Adduction/Valgus (Left) at IC: {k_valg_l_ic:.2f} deg, Peak: {k_valg_l_peak:.2f} deg")

