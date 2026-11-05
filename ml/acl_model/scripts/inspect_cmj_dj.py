import os
import scipy.io as sio

p_cmj = r"C:\Users\User\Downloads\28890545\Kinematic_data\Joint_angles\CMJ.mat"
d_cmj = sio.loadmat(p_cmj)
arr = d_cmj["CMJ"]
cell = arr[0, 0]
print("CMJ cell dtype:", cell.dtype)
sub_obj = cell[0, 0][cell.dtype.names[0]]
print("sub_obj dtype:", getattr(sub_obj, "dtype", type(sub_obj)))
if hasattr(sub_obj, "dtype") and sub_obj.dtype.names:
    print("sub_obj fields:", sub_obj.dtype.names)
    for f in sub_obj.dtype.names:
        val = sub_obj[f]
        print(f"  Field '{f}': shape={val.shape}, type={type(val)}")
        if f == 'sub_data':
            sd = val[0, 0]
            print(f"    sub_data shape: {sd.shape}, dtype: {getattr(sd, 'dtype', 'none')}")
            if hasattr(sd, 'dtype') and sd.dtype.names:
                print(f"    sub_data rep0 fields: {sd[0, 0].dtype.names if sd.ndim > 1 else sd[0].dtype.names}")

p_dj = r"C:\Users\User\Downloads\28890545\Kinematic_data\Joint_angles\DJ.mat"
d_dj = sio.loadmat(p_dj)
arr_dj = d_dj["DJ"]
cell_dj = arr_dj[0, 0]
print("\nDJ cell dtype:", cell_dj.dtype)
sub_obj_dj = cell_dj[0, 0][cell_dj.dtype.names[0]]
print("DJ sub_obj dtype:", getattr(sub_obj_dj, "dtype", type(sub_obj_dj)))
if hasattr(sub_obj_dj, "dtype") and sub_obj_dj.dtype.names:
    print("DJ sub_obj fields:", sub_obj_dj.dtype.names)
    for f in sub_obj_dj.dtype.names:
        val = sub_obj_dj[f]
        print(f"  Field '{f}': shape={val.shape}")
        if f == 'sub_data':
            sd = val[0, 0]
            print(f"    sub_data shape: {sd.shape}, dtype: {getattr(sd, 'dtype', 'none')}")
            if hasattr(sd, 'dtype') and sd.dtype.names:
                print(f"    sub_data rep0 fields: {sd[0, 0].dtype.names if sd.ndim > 1 else sd[0].dtype.names}")

