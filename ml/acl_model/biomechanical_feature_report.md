# Biomechanical Feature Extraction Report

## 1. Feature Space Definition (64 Numeric Features)
The feature engineering engine (`extract_all_features.py`) extracts 64 biomechanical quantities computed at touchdown (Initial Contact, IC), peak loading phase (0–100 ms post-IC), and full landing absorption phase (0–250 ms post-IC):

### Knee Kinematics (Primary ACL Risk Markers)
1. `knee_flex_ic_r`, `knee_flex_ic_l`: Knee flexion at Initial Contact (degrees).
2. `knee_flex_peak_r`, `knee_flex_peak_l`: Peak knee flexion during landing absorption.
3. `knee_flex_min_r`, `knee_flex_min_l`: Minimum knee angle during landing.
4. `knee_flex_rom_r`, `knee_flex_rom_l`: Knee flexion range of motion.
5. `knee_valg_ic_r`, `knee_valg_ic_l`: Knee adduction/valgus angle at Initial Contact.
6. `knee_valg_peak_r`, `knee_valg_peak_l`: Peak dynamic knee valgus during 100 ms deceleration.
7. `knee_valg_rom_r`, `knee_valg_rom_l`: Knee frontal-plane excursion.
8. `knee_rot_ic_r`, `knee_rot_ic_l`: Transverse knee internal/external rotation at touchdown.
9. `knee_rot_peak_r`, `knee_rot_peak_l`: Peak transverse knee rotation during deceleration.

### Hip Kinematics
10. `hip_flex_ic_r`, `hip_flex_ic_l`: Hip flexion at Initial Contact.
11. `hip_flex_peak_r`, `hip_flex_peak_l`: Peak hip flexion angle.
12. `hip_flex_rom_r`, `hip_flex_rom_l`: Hip sagittal range of motion.
13. `hip_add_ic_r`, `hip_add_ic_l`: Hip adduction at touchdown.
14. `hip_add_peak_r`, `hip_add_peak_l`: Peak dynamic hip adduction (femoral collapse vector).
15. `hip_rot_peak_r`, `hip_rot_peak_l`: Peak hip transverse rotation.

### Ankle Kinematics
16. `ankle_dorsi_ic_r`, `ankle_dorsi_ic_l`: Ankle dorsiflexion/plantarflexion at touchdown.
17. `ankle_dorsi_peak_r`, `ankle_dorsi_peak_l`: Peak dorsiflexion angle.
18. `ankle_dorsi_rom_r`, `ankle_dorsi_rom_l`: Ankle sagittal excursion.
19. `subtalar_peak_r`, `subtalar_peak_l`: Subtalar frontal excursion (inversion/eversion).

### Trunk & Pelvis Mechanics
20. `trunk_ext_ic`, `trunk_ext_peak`, `trunk_ext_rom`: Lumbar extension/flexion excursion.
21. `trunk_bend_ic`, `trunk_bend_peak`: Lumbar lateral bending (ipsilateral trunk lean).
22. `trunk_rot_peak`: Lumbar axial rotation.
23. `pelvis_tilt_peak`, `pelvis_list_peak`, `pelvis_rot_peak`: 3D Pelvic excursions.

### Bilateral Asymmetry Indices
24. `asym_knee_flex_ic`, `asym_knee_flex_peak`: Inter-limb knee flexion disparity.
25. `asym_knee_valg_peak`: Inter-limb frontal plane knee disparity.
26. `asym_hip_flex_peak`, `asym_hip_add_peak`: Inter-limb hip disparity.
27. `asym_ankle_dorsi_peak`: Inter-limb ankle disparity.

### Coordination & Center of Mass (COM) Dynamics
28. `hip_knee_ratio_r`, `hip_knee_ratio_l`: Hip-to-knee flexion ratio.
29. `com_vz_ic`: Downward vertical center-of-mass velocity at touchdown.
30. `com_az_peak`: Peak vertical deceleration magnitude.
31. `com_v_res_ic`: Resultant COM velocity magnitude.
32. `com_z_excursion`: Vertical displacement during landing absorption.
33. `act_knee_flex_ic`, `act_knee_flex_peak`, `act_knee_valg_peak`, `act_hip_add_peak`, `act_ankle_dorsi_peak`: Active-limb specific metrics for unilateral tasks.
