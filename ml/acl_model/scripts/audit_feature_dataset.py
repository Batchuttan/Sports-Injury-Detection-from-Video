"""
Data Quality & Inspection Audit for Extracted Biomechanical Features
"""

import os
import pandas as pd
import numpy as np

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
csv_path = os.path.join(DATASET_ROOT, "ACL_Model_Output", "extracted_biomechanical_features.csv")
df = pd.read_csv(csv_path)

print("=" * 70)
print("BIOMECHANICAL DATASET QUALITY AUDIT")
print("=" * 70)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

meta_cols = ["participant_id", "sub_num", "task", "limb", "rep", "is_fatigued", "target"]
feature_cols = [c for c in df.columns if c not in meta_cols]
print(f"Total Biomechanical Features: {len(feature_cols)}")

# Missing values check
missing = df[feature_cols].isnull().sum()
n_missing = missing[missing > 0]
print(f"\nMissing values in features: {len(n_missing)} columns have missing values")
if len(n_missing) > 0:
    print(n_missing)
else:
    print("Zero missing values across all 64 biomechanical features!")

# Inf check
infs = np.isinf(df[feature_cols].values).sum()
print(f"Infinite values in features: {infs}")

# Participant level balance
pt = df.groupby(["participant_id", "target"]).size().reset_index(name="trial_count")
print(f"\nParticipant-level count: {len(pt)} participants")
print(f"Mean trials per participant: {pt['trial_count'].mean():.1f} (min: {pt['trial_count'].min()}, max: {pt['trial_count'].max()})")
print("\nTarget balance at participant level:")
print(pt["target"].value_counts())

# Task balance
print("\nTrials by Task:")
print(df["task"].value_counts())

# Fatigue balance
print("\nTrials by Fatigue Condition (0=non-fatigued, 1=fatigued):")
print(df["is_fatigued"].value_counts())

# Sample stats of key ACL biomarkers
biomarkers = ["knee_valg_peak_r", "knee_valg_peak_l", "knee_flex_ic_r", "knee_flex_ic_l", "asym_knee_valg_peak", "com_az_peak"]
print("\nKey ACL Biomechanical Markers Summary:")
print(df[biomarkers].describe().to_string())

