import os
import scipy.io as sio
import numpy as np

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
angles_dir = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")

def inspect_task(mf_name):
    path = os.path.join(angles_dir, mf_name)
    data = sio.loadmat(path)
    root_key = [k for k in data.keys() if not k.startswith("__")][0]
    mat_arr = data[root_key]
    print(f"\n==================== {mf_name} ({root_key}) ====================")
    print(f"Matrix shape: {mat_arr.shape}")
    
    n_rows, n_cols = mat_arr.shape
    found = False
    for r in range(n_rows):
        for c in range(n_cols):
            cell = mat_arr[r, c]
            if isinstance(cell, np.ndarray) and cell.size > 0 and cell.dtype.names:
                first_field = cell.dtype.names[0]
                struct_val = cell[0, 0][first_field]
                if hasattr(struct_val, 'dtype') and struct_val.dtype.names and 'sub_data' in struct_val.dtype.names:
                    sd = struct_val['sub_data'][0, 0]
                    n_reps = sd.shape[0] if sd.ndim > 0 else 1
                    rep0 = sd[0, 0] if sd.ndim > 1 else sd[0]
                    print(f"Sample at (row {r}, col {c}) -> Participant sub{r+1:02d}, leg col {c}: {n_reps} repetitions")
                    print("Rep 0 fields:")
                    for f in rep0.dtype.names:
                        val = rep0[f][0, 0] if rep0[f].ndim > 1 and rep0[f].size > 0 else rep0[f]
                        shape = getattr(val, 'shape', 'scalar')
                        dtype = getattr(val, 'dtype', type(val))
                        print(f"  - {f}: shape={shape}, type={dtype}")
                    found = True
                    break
        if found:
            break

for mf in ["CMJ.mat", "DJ.mat", "SLH.mat", "COH.mat", "MRH.mat", "uCMJ.mat"]:
    inspect_task(mf)

