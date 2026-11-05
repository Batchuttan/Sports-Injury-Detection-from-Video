"""
Dataset Inspection Script for ACL Jump-Landing Dataset (DOI: 10.6084/m9.figshare.28890545)
Inspects:
- Participants logs and questionnaires (injury status, healthy controls, demographics)
- Joint angle columns (IK_column_labels.xlsx)
- Kinematic .mat data files (CMJ, DJ, SLH, MRH, COH, uCMJ)
- Task labeling files
"""

import os
import sys
import glob
import json
import pandas as pd
import numpy as np

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
PARTICIPANTS_DIR = os.path.join(DATASET_ROOT, "Participants")
KINEMATIC_DIR = os.path.join(DATASET_ROOT, "Kinematic_data")
JOINT_ANGLES_DIR = os.path.join(KINEMATIC_DIR, "Joint_angles")
PROCESSING_DIR = os.path.join(DATASET_ROOT, "Data_processing")
OUTPUT_DIR = os.path.join(DATASET_ROOT, "ACL_Model_Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("PHASE 1 & 2: ACL JUMP-LANDING DATASET INSPECTION")
print("=" * 70)

# 1. Inspect Participants Files
log_path = os.path.join(PARTICIPANTS_DIR, "participant_log.xlsx")
quest_path = os.path.join(PARTICIPANTS_DIR, "ACL_questionnaires.xlsx")

if os.path.exists(log_path):
    excel = pd.ExcelFile(log_path)
    print(f"\n[participant_log.xlsx] Sheet names: {excel.sheet_names}")
    for sheet in excel.sheet_names:
        df = pd.read_excel(log_path, sheet_name=sheet)
        print(f"\n--- Sheet: {sheet} (Shape: {df.shape}) ---")
        print("Columns:", df.columns.tolist())
        print(df.head(3))

if os.path.exists(quest_path):
    excel_q = pd.ExcelFile(quest_path)
    print(f"\n[ACL_questionnaires.xlsx] Sheet names: {excel_q.sheet_names}")
    for sheet in excel_q.sheet_names:
        df_q = pd.read_excel(quest_path, sheet_name=sheet)
        print(f"\n--- Sheet: {sheet} (Shape: {df_q.shape}) ---")
        print("Columns:", df_q.columns.tolist())
        print(df_q.head(3))

# 2. Inspect IK Column Labels
ik_path = os.path.join(JOINT_ANGLES_DIR, "IK_column_labels.xlsx")
if os.path.exists(ik_path):
    df_ik = pd.read_excel(ik_path)
    print(f"\n[IK_column_labels.xlsx] (Shape: {df_ik.shape})")
    print("Columns:", df_ik.columns.tolist())
    print(df_ik)

# 3. Inspect Labeling Files
label_files = glob.glob(os.path.join(PROCESSING_DIR, "labeling_*.xlsx"))
print(f"\n[Labeling files in Data_processing]: Found {len(label_files)} files")
for lf in label_files[:3]:
    df_lf = pd.read_excel(lf)
    print(f"File {os.path.basename(lf)} shape: {df_lf.shape}, columns: {df_lf.columns.tolist()[:6]}")

