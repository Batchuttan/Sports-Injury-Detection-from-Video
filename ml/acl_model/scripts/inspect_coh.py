import os
import time
import scipy.io as sio

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
angles_dir = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")

t0 = time.time()
path = os.path.join(angles_dir, "COH.mat")
print(f"Loading COH.mat (254 MB)...")
data = sio.loadmat(path)
print(f"Loaded in {time.time() - t0:.2f} s")

root_key = [k for k in data.keys() if not k.startswith("__")][0]
mat_arr = data[root_key]
print("Shape:", mat_arr.shape)

# Let's inspect sub01 (row 0)
cell = mat_arr[0, 0]
print("Cell dtype:", cell.dtype)
sub_obj = cell[0, 0]
sub_field = cell.dtype.names[0]
print("Sub field name:", sub_field)
coh_struct = sub_obj[sub_field]
print("Fields in struct:", coh_struct.dtype.names)
sub_data = coh_struct['sub_data'][0, 0]
print("sub_data shape:", sub_data.shape)
rep0 = sub_data[0, 0] if sub_data.ndim > 1 else sub_data[0]
print("rep0 fields:", rep0.dtype.names)
for f in rep0.dtype.names:
    val = rep0[f]
    print(f"  {f}: type={type(val)}, shape={getattr(val, 'shape', 'none')}")
    if f == 'IC':
        print(f"    IC value: {val}")
    elif f == 'Joint_Angles':
        ja = val[0, 0] if val.ndim > 1 and val.dtype == 'O' else val
        print(f"    Joint_Angles shape: {ja.shape}")

