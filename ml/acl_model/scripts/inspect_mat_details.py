import os
import scipy.io as sio
import numpy as np

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
angles_dir = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")

mat_files = ["CMJ.mat", "DJ.mat", "SLH.mat", "COH.mat", "MRH.mat", "uCMJ.mat"]

for mf in mat_files:
    path = os.path.join(angles_dir, mf)
    data = sio.loadmat(path)
    root_key = [k for k in data.keys() if not k.startswith("__")][0]
    mat_arr = data[root_key]
    print(f"\n==================== {mf} (Key: {root_key}) ====================")
    print(f"Shape: {mat_arr.shape}, type: {type(mat_arr)}")
    
    # Check dimensions
    # In figures.m: SLH{i_sub, 1}.SLH.sub_data(i_rep)
    n_rows, n_cols = mat_arr.shape
    print(f"Rows: {n_rows}, Cols: {n_cols}")
    
    # Inspect first non-empty cell
    found = False
    for r in range(n_rows):
        for c in range(n_cols):
            cell = mat_arr[r, c]
            if isinstance(cell, np.ndarray) and cell.size > 0:
                print(f"Cell ({r}, {c}) type: {type(cell)}, shape: {cell.shape}, dtype: {cell.dtype}")
                if cell.dtype.names:
                    print(f"  Fields: {cell.dtype.names}")
                    inner_obj = cell[0, 0]
                    first_field = cell.dtype.names[0]
                    sub_struct = inner_obj[first_field]
                    print(f"  Field '{first_field}' type: {type(sub_struct)}, shape: {getattr(sub_struct, 'shape', 'none')}")
                    if hasattr(sub_struct, 'dtype') and sub_struct.dtype.names:
                        print(f"    sub_struct fields: {sub_struct.dtype.names}")
                        if 'sub_data' in sub_struct.dtype.names:
                            sd = sub_struct['sub_data'][0, 0]
                            print(f"    sub_data shape: {sd.shape}, fields: {sd.dtype.names if hasattr(sd, 'dtype') else 'none'}")
                            if hasattr(sd, 'dtype') and sd.dtype.names:
                                # Inspect rep 0
                                rep0 = sd[0, 0] if sd.ndim > 1 else sd[0]
                                print("    Rep 0 fields:", rep0.dtype.names)
                                for f in rep0.dtype.names:
                                    f_val = rep0[f]
                                    print(f"      '{f}': shape={getattr(f_val, 'shape', 'none')}, type={type(f_val)}, val={f_val if getattr(f_val, 'size', 0) == 1 else 'array'}")
                found = True
                break
        if found:
            break

