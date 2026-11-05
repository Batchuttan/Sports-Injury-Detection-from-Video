import os
import scipy.io as sio

p_cmj = r"C:\Users\User\Downloads\28890545\Kinematic_data\Joint_angles\CMJ.mat"
d_cmj = sio.loadmat(p_cmj)
arr = d_cmj["CMJ"]
sd = arr[0, 0][0, 0]['CMJ_bil']['sub_data'][0, 0]
rep0 = sd[0, 0]
print("CMJ Rep 0 IC_K:", rep0['IC_K'])
print("CMJ Rep 0 IC_A:", rep0['IC_A'])
print("CMJ Rep 0 JA shape:", rep0['Joint_Angles'].shape)

p_dj = r"C:\Users\User\Downloads\28890545\Kinematic_data\Joint_angles\DJ.mat"
d_dj = sio.loadmat(p_dj)
arr_dj = d_dj["DJ"]
sd_dj = arr_dj[0, 0][0, 0]['DJ_bil']['sub_data'][0, 0]
rep0_dj = sd_dj[0, 0]
print("\nDJ Rep 0 IC_first_K:", rep0_dj['IC_first_K'])
print("DJ Rep 0 IC_second_K:", rep0_dj['IC_second_K'])
print("DJ Rep 0 JA shape:", rep0_dj['Joint_Angles'].shape)

