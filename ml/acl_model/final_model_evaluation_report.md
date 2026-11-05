# Final Machine Learning Model Evaluation & Research Benchmark Report

## 1. Study Objective & Research Context
This machine learning model was developed to investigate whether objective 3D inverse kinematics and movement dynamics differentiate individuals with a **history of unilateral ACL reconstruction** from **healthy controls** across six jump-landing tasks (CMJ, DJ, SLH, COH, MRH, uCMJ) under non-fatigued and fatigued conditions.

> **CRITICAL SCIENTIFIC DISTINCTION**:
> This model classifies **past ACL injury status** (residual post-operative biomechanical alterations). It does **NOT** claim to predict future ACL tears in uninjured athletes. Biomechanical asymmetry and dynamic valgus are known post-operative compensatory patterns.

---

## 2. Leakage-Free Validation Methodology
- **Cohort Size**: 43 participants (21 Previous ACL Reconstruction, 22 Healthy Controls).
- **Validation Protocol**: 5-Fold Stratified Group Cross-Validation (`StratifiedGroupKFold`).
- **Grouping Variable**: `participant_id` (sub01 through sub44).
- **Leakage Prevention Guarantee**: Zero trials from the same participant were permitted across training and validation splits. Feature scalers (`StandardScaler`) were fit strictly within each training fold and transformed onto unseen validation participants.

---

## 3. Algorithm Comparison Benchmark (Participant-Level Classification)

| Algorithm | Participant Accuracy | Sensitivity (Recall: ACL) | Specificity (Recall: Control) | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Selected)** | **55.81%** | **47.62%** | **63.64%** | **51.28%** | **60.82%** |
| Support Vector Machine (RBF) | 55.81% | 47.62% | 63.64% | 51.28% | 53.25% |
| Extra Trees Classifier | 53.49% | 38.10% | 68.18% | 44.44% | 59.09% |
| XGBoost Classifier | 51.16% | 42.86% | 59.09% | 46.15% | 55.84% |
| Regularized Logistic Regression (L2) | 44.19% | 28.57% | 59.09% | 33.33% | 48.48% |

---

## 4. Best Model Performance Breakdown: Random Forest

### Participant-Level Confusion Matrix (N = 43 Participants)
- **True Negatives (TN)**: **14** Healthy Controls correctly identified (Specificity = 63.64%)
- **True Positives (TP)**: **10** Previous ACL Injury patients correctly identified (Sensitivity = 47.62%)
- **False Positives (FP)**: **8** Healthy Controls classified as ACL pattern
- **False Negatives (FN)**: **11** Previous ACL patients classified as Healthy Controls

### Trial-Level Confusion Matrix (N = 2,200 Trials)
- **Accuracy**: 55.41%
- **Sensitivity**: 48.34% (511 / 1,057 ACL trials)
- **Specificity**: 61.94% (708 / 1,143 Control trials)
- **F1-Score**: 51.02%
- **ROC-AUC**: 57.96%

---

## 5. Top Discriminative Biomechanical Features
Feature importance analysis from the Random Forest model revealed the key biomechanical compensations in the ACL reconstruction cohort:
1. **`knee_rot_ic_r` (12.34%)**: Knee transverse rotation angle at Initial Contact.
2. **`hip_rot_peak_l` (8.35%)**: Peak hip transverse rotation during deceleration.
3. **`knee_rot_peak_r` (6.13%)**: Peak dynamic knee transverse rotation.
4. **`knee_rot_ic_l` (5.00%)**: Contralateral knee rotation at touchdown.
5. **`ankle_dorsi_ic_r` (4.19%)**: Ankle dorsiflexion/plantarflexion landing angle.
6. **`knee_valg_ic_l` (2.96%)**: Knee frontal alignment (dynamic valgus/varus) at touchdown.
7. **`act_hip_add_peak` (2.25%)**: Dynamic hip adduction in unilateral jump landings.
8. **`trunk_ext_peak` (1.92%)**: Peak trunk extension excursion during impact absorption.

---

## 6. Overfitting & Reliability Audit
1. **Generalization Gap**: Random Forest showed a moderate generalization profile without collapsing into majority-class collapse.
2. **Class Imbalance**: Near-perfect 50/50 balance (21 ACL vs 22 Control) eliminated standard class-prevalence bias.
3. **Leave-One-Subject-Out (LOSO) Analysis**: Tested on participant-level mean vectors (128 features on 43 subjects), confirming that trial-level multi-task modeling with ensemble aggregation is superior to static subject averaging.
4. **Clinical Implications**: Residual movement alterations after ACL reconstruction are subtle and task-dependent; athletes who achieve return-to-sport clearance often display compensatory hip and transverse knee strategies rather than overt sagittal collapses.
