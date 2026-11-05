import os
import sys
import scipy.io as sio
import pandas as pd
import numpy as np

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
mat_path = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles", "CMJ.mat")

data = sio.loadmat(mat_path)
cmj = data['CMJ']
print(f"CMJ shape: {cmj.shape}, type: {type(cmj)}")

# Check first few entries of CMJ
for i in range(min(5, len(cmj))):
    item = cmj[i, 0]
    print(f"\nIndex {i}: type={type(item)}, shape={getattr(item, 'shape', 'none')}, dtype={getattr(item, 'dtype', 'none')}")
    if hasattr(item, 'dtype') and item.dtype.names:
        print(f"  Field names: {item.dtype.names}")
    elif isinstance(item, np.ndarray):
        print(f"  Sample value: {item[:2] if len(item) > 0 else 'empty'}")

# Also check IK_column_labels.xlsx completely
ik_path = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles", "IK_column_labels.xlsx")
df_ik = pd.read_excel(ik_path)
print("\n--- IK_column_labels.xlsx full display ---")
print(df_ik.iloc[8:])

# Also check participant_log.xlsx
log_path = os.path.join(DATASET_ROOT, "Participants", "participant_log.xlsx")
df_log = pd.read_excel(log_path, header=0)
print("\n--- participant_log.xlsx full display ---")
print(df_log.iloc[:10, :10])
