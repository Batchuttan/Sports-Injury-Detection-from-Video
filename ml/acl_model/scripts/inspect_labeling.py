import os
import glob
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
processing_dir = os.path.join(DATASET_ROOT, "Data_processing")
label_files = sorted(glob.glob(os.path.join(processing_dir, "labeling_*.xlsx")))

total_trials = 0
print("--- SUMMARY OF LABELING FILES ---")
for lf in label_files:
    fname = os.path.basename(lf)
    df = pd.read_excel(lf)
    n_rows = len(df)
    total_trials += n_rows
    subs = df['sub'].unique() if 'sub' in df.columns else []
    print(f"\n{fname}: {n_rows} rows, {len(subs)} participants")
    print("Columns:", df.columns.tolist())
    print("Sample rows:")
    print(df.head(2).to_string())

print(f"\nTotal trial rows across all labeling files: {total_trials}")

