import os
import pandas as pd

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
log_path = os.path.join(DATASET_ROOT, "Participants", "participant_log.xlsx")
cmj_label_path = os.path.join(DATASET_ROOT, "Data_processing", "labeling_CMJ.xlsx")

df_log = pd.read_excel(log_path, header=0)
header_row = [str(c).strip() for c in df_log.iloc[0].values]
df_log.columns = header_row
df_log = df_log.iloc[1:].reset_index(drop=True)
df_log = df_log.dropna(how='all', subset=['participants'])
df_log['participants'] = df_log['participants'].astype(str).str.strip()

# Map sub strings to integer numbers: sub01 -> 1, etc.
participant_map = {}
for idx, row in df_log.iterrows():
    p = row['participants']
    if p.startswith('sub'):
        sub_id = int(p.replace('sub', ''))
        # in participant_log: ACLG=1 ; CG=2
        grp_val = row['group (ACLG=1 ; CG=2)']
        participant_map[sub_id] = {
            'participant': p,
            'log_group_code': grp_val,
            'is_acl': (grp_val == 1 or grp_val == '1')
        }

df_cmj = pd.read_excel(cmj_label_path)
print("Comparing participant_log vs labeling_CMJ:")
grp_col = [c for c in df_cmj.columns if 'group' in c.lower()][0]
inj_col = [c for c in df_cmj.columns if 'injured' in c.lower()][0]

for sub_id in sorted(participant_map.keys()):
    sub_cmj = df_cmj[df_cmj['sub'] == sub_id]
    if len(sub_cmj) > 0:
        cmj_grp = sub_cmj[grp_col].iloc[0]
        cmj_inj = sub_cmj[inj_col].iloc[0]
        log_is_acl = participant_map[sub_id]['is_acl']
        print(f"Sub {sub_id:02d} ({participant_map[sub_id]['participant']}): log_is_acl={log_is_acl} (code {participant_map[sub_id]['log_group_code']}) | CMJ grp={cmj_grp}, injured_leg={cmj_inj}")

