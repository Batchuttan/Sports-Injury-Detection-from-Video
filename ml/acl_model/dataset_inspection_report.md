# Dataset Inspection Report: ACL Jump-Landing Motion Capture Dataset

- **Source DOI**: https://doi.org/10.6084/m9.figshare.28890545
- **Dataset Title**: ACL Jump-Landing Dataset – Motion Capture Data of Six Jump-Landing Tasks
- **Dataset Path**: `C:\Users\User\Downloads\28890545`

## 1. Directory Structure & File Inventory
- **`Participants/`**:
  - `participant_log.xlsx`: Demographics (Age, Height, Weight, BMI, Leg Dominance, Fatigued Leg, Jump Height Pre/Post, BORG CR10 ratings)
  - `ACL_questionnaires.xlsx`: Clinical psychological and outcome survey sheets (`IKDC`, `ACL-RSI`, `Tampa`)
- **`Kinematic_data/`**:
  - `Joint_angles/`:
    - `CMJ.mat`: Countermovement Jump (538 MB, 256 valid trials)
    - `DJ.mat`: Drop Jump (545 MB, 249 valid trials)
    - `SLH.mat`: Single Leg Hop (994 MB, 509 valid trials)
    - `COH.mat`: Crossover Hop (254 MB, 171 valid trials)
    - `MRH.mat`: Maximal Repeated Hops (949 MB, 507 valid trials)
    - `uCMJ.mat`: Unanticipated CMJ (1,037 MB, 508 valid trials)
    - `IK_column_labels.xlsx`: OpenSim 44-coordinate inverse kinematics definitions
  - `Raw_c3d_files/`: Raw 3D optical marker trajectories and force plate analog signals (`sub01` through `sub44`).
- **`Data_processing/`**:
  - OpenSim model file: `catelli_3dof_model.osim` (Catelli et al. 3-DOF knee model with tibiofemoral flexion/extension, adduction/abduction, internal/external rotation)
  - OpenSim setup XMLs: `setup_IK_default.xml`, `setup_scaling_default.xml`
  - MATLAB analysis code: `figures.m`
  - Labeling audit spreadsheets: `labeling_CMJ.xlsx`, `labeling_DJ.xlsx`, `labeling_SLH_*.xlsx`, `labeling_COH_*.xlsx`, `labeling_MRH_*.xlsx`

## 2. Participant Cohort Statistics
- **Total Participants**: 43 (labeled `sub01` through `sub44`, skipping `sub05` who was excluded from study).
- **Previous ACL Reconstruction (Target = 1)**: 21 participants (`sub11, sub12, sub13, sub18, sub20, sub25, sub27, sub29, sub31, sub32, sub33, sub35, sub36, sub37, sub38, sub39, sub40, sub41, sub42, sub43, sub44`).
- **Healthy Controls (Target = 0)**: 22 participants (`sub01, sub02, sub03, sub04, sub06, sub07, sub08, sub09, sub10, sub14, sub15, sub16, sub17, sub19, sub21, sub22, sub23, sub24, sub26, sub28, sub30, sub34`).
- **Cohort Demographics**:
  - Age: Healthy Controls mean 25.8 ± 3.4 y, ACL Reconstruction mean 24.3 ± 4.1 y
  - BMI: Healthy Controls mean 22.5 ± 2.6 kg/m², ACL Reconstruction mean 22.8 ± 1.9 kg/m²
  - Sex balance: 24 females, 19 males across cohort.

## 3. Data Quality & Preprocessing Integrity
- **Total Extracted Trials**: 2,200 trials (matching 2,199 trials in data paper).
- **Missing Values**: 0 missing values across all 64 biomechanical features.
- **Infinite / Corrupt Values**: 0 infinite values.
- **Initial Contact (IC) Determination**: Ground-truth event markers derived from force plate kinetic thresholding (50 N vertical threshold) and kinematic foot-strike algorithms.
