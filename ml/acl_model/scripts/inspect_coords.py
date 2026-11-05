import os
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
ik_path = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles", "IK_column_labels.xlsx")

df_ik = pd.read_excel(ik_path, header=None)
col_names = df_ik.iloc[11].values.tolist()
for idx, name in enumerate(col_names):
    print(f"Col {idx:2d}: {name}")
