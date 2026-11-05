import os
import scipy.io as sio

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
angles_dir = os.path.join(DATASET_ROOT, "Kinematic_data", "Joint_angles")

mat_files = ["CMJ.mat", "DJ.mat", "SLH.mat", "COH.mat", "MRH.mat", "uCMJ.mat"]

for mf in mat_files:
    p = os.path.join(angles_dir, mf)
    data = sio.loadmat(p)
    key = [k for k in data.keys() if not k.startswith("__")][0]
    arr = data[key]
    print(f"{mf:10s} | Root key: {key:8s} | Shape: {arr.shape}")

