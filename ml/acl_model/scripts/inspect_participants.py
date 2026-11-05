import os
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
log_path = os.path.join(DATASET_ROOT, "Participants", "participant_log.xlsx")

df = pd.read_excel(log_path, header=0)
header_row = [str(c).strip() for c in df.iloc[0].values]
df.columns = header_row
df = df.iloc[1:].reset_index(drop=True)
df = df.dropna(how='all', subset=['participants'])

# Strip strings in participants
df['participants'] = df['participants'].astype(str).str.strip()

cols_to_show = ['participants', 'group (ACLG=1 ; CG=2)', 'Gender (female=1; male=2)', 'Age', 'Height (m)', 'Weight (kg)', 'BMI']
cols_avail = [c for c in cols_to_show if c in df.columns]
print(df[cols_avail].to_string())

print("\n--- Group breakdown ---")
grp_col = 'group (ACLG=1 ; CG=2)'
print(df[grp_col].value_counts())
print("\nUnique participants count:", df['participants'].nunique())
print("Participants list:", sorted(df['participants'].unique()))
