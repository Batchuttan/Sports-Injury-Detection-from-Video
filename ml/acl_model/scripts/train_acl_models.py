"""
Complete Machine Learning Training & Evaluation Pipeline for ACL Biomechanical Risk Classification
- Strict Participant-Level Group Validation (StratifiedGroupKFold, 5-Fold)
- Comprehensive algorithm comparison: Logistic Regression, Random Forest, SVM, XGBoost, Extra Trees
- Leakage-safe scaling pipelines
- Dual-level evaluation: Participant-level (primary clinical unit) & Trial-level
- Artifact persistence to ACL_Model_Output
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
CSV_PATH = os.path.join(DATASET_ROOT, "ACL_Model_Output", "extracted_biomechanical_features.csv")
OUTPUT_DIR = os.path.join(DATASET_ROOT, "ACL_Model_Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("PHASE 5, 6, 7 & 8: ACL BIOMECHANICAL MACHINE LEARNING MODEL TRAINING")
print("=" * 70)

# 1. Load Dataset
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} trials across {df['participant_id'].nunique()} participants.")

meta_cols = ["participant_id", "sub_num", "task", "limb", "rep", "is_fatigued", "target"]
feature_cols = [c for c in df.columns if c not in meta_cols]
print(f"Number of biomechanical features: {len(feature_cols)}")

X = df[feature_cols].values
y = df['target'].values
groups = df['participant_id'].values

# Participant ground truth dictionary
participant_ground_truth = df.groupby('participant_id')['target'].first().to_dict()

# Define Algorithms
models = {
    "Logistic_Regression": LogisticRegression(C=0.1, penalty='l2', max_iter=1000, random_state=42),
    "Random_Forest": RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_leaf=4, max_features='sqrt', random_state=42),
    "Support_Vector_Machine": SVC(C=1.0, kernel='rbf', probability=True, random_state=42),
    "Extra_Trees": ExtraTreesClassifier(n_estimators=150, max_depth=6, min_samples_leaf=3, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=120, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, eval_metric='logloss', random_state=42)
}

# Group-Aware 5-Fold Cross-Validation
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

# Get participant-level y for stratification check
unique_participants = sorted(list(participant_ground_truth.keys()))
part_targets = [participant_ground_truth[p] for p in unique_participants]

cv_results = {}
oof_predictions = {name: {"trial_preds": np.zeros(len(df)), "trial_probs": np.zeros(len(df)),
                          "part_probs": {}, "part_preds": {}} for name in models}

print("\nExecuting Participant-Level 5-Fold Stratified Group Cross-Validation:")
print("-" * 70)

fold_splits = list(sgkf.split(X, y, groups=groups))

for fold_idx, (train_idx, val_idx) in enumerate(fold_splits):
    train_subs = np.unique(groups[train_idx])
    val_subs = np.unique(groups[val_idx])
    
    # Verify ZERO leakage
    leakage = set(train_subs).intersection(set(val_subs))
    assert len(leakage) == 0, f"DATA LEAKAGE DETECTED in Fold {fold_idx}: {leakage}"
    
    val_targets = [participant_ground_truth[s] for s in val_subs]
    n_acl_val = sum(val_targets)
    n_cg_val = len(val_targets) - n_acl_val
    print(f"Fold {fold_idx + 1}: Train={len(train_subs)} subs ({len(train_idx)} trials) | Val={len(val_subs)} subs ({len(val_idx)} trials) [ACL: {n_acl_val}, Control: {n_cg_val}]")

# Model Training & Evaluation Loop
for name, model in models.items():
    print(f"\nEvaluating: {name}...")
    fold_part_metrics = []
    fold_trial_metrics = []
    
    for fold_idx, (train_idx, val_idx) in enumerate(fold_splits):
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        val_groups = groups[val_idx]
        
        # Scale inside fold strictly using training data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Fit model
        model.fit(X_train_scaled, y_train)
        
        # Predict on validation trials
        y_prob = model.predict_proba(X_val_scaled)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)
        
        oof_predictions[name]["trial_probs"][val_idx] = y_prob
        oof_predictions[name]["trial_preds"][val_idx] = y_pred
        
        # Trial metrics
        t_acc = accuracy_score(y_val, y_pred)
        t_prec = precision_score(y_val, y_pred, zero_division=0)
        t_rec = recall_score(y_val, y_pred, zero_division=0)
        t_f1 = f1_score(y_val, y_pred, zero_division=0)
        t_auc = roc_auc_score(y_val, y_prob)
        fold_trial_metrics.append({"acc": t_acc, "prec": t_prec, "rec": t_rec, "f1": t_f1, "auc": t_auc})
        
        # Participant-Level Aggregation (Mean probability across all trials of participant)
        val_sub_unique = np.unique(val_groups)
        p_true_fold = []
        p_prob_fold = []
        p_pred_fold = []
        
        for sub in val_sub_unique:
            sub_mask = (val_groups == sub)
            sub_mean_prob = float(np.mean(y_prob[sub_mask]))
            sub_pred = int(sub_mean_prob >= 0.5)
            sub_true = participant_ground_truth[sub]
            
            oof_predictions[name]["part_probs"][sub] = sub_mean_prob
            oof_predictions[name]["part_preds"][sub] = sub_pred
            
            p_true_fold.append(sub_true)
            p_prob_fold.append(sub_mean_prob)
            p_pred_fold.append(sub_pred)
            
        p_acc = accuracy_score(p_true_fold, p_pred_fold)
        p_prec = precision_score(p_true_fold, p_pred_fold, zero_division=0)
        p_rec = recall_score(p_true_fold, p_pred_fold, zero_division=0)
        p_f1 = f1_score(p_true_fold, p_pred_fold, zero_division=0)
        p_auc = roc_auc_score(p_true_fold, p_prob_fold) if len(np.unique(p_true_fold)) > 1 else 0.5
        fold_part_metrics.append({"acc": p_acc, "prec": p_prec, "rec": p_rec, "f1": p_f1, "auc": p_auc})

    # Aggregate Overall Out-Of-Fold Metrics
    # Participant Level
    all_subs = sorted(list(participant_ground_truth.keys()))
    p_true_all = [participant_ground_truth[s] for s in all_subs]
    p_pred_all = [oof_predictions[name]["part_preds"][s] for s in all_subs]
    p_prob_all = [oof_predictions[name]["part_probs"][s] for s in all_subs]
    
    cm_part = confusion_matrix(p_true_all, p_pred_all)
    # TN, FP, FN, TP
    tn, fp, fn, tp = cm_part.ravel()
    part_sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    part_specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    part_acc = accuracy_score(p_true_all, p_pred_all)
    part_prec = precision_score(p_true_all, p_pred_all, zero_division=0)
    part_rec = recall_score(p_true_all, p_pred_all, zero_division=0)
    part_f1 = f1_score(p_true_all, p_pred_all, zero_division=0)
    part_auc = roc_auc_score(p_true_all, p_prob_all)
    
    # Trial Level
    trial_pred_all = oof_predictions[name]["trial_preds"]
    trial_prob_all = oof_predictions[name]["trial_probs"]
    cm_trial = confusion_matrix(y, trial_pred_all)
    t_tn, t_fp, t_fn, t_tp = cm_trial.ravel()
    trial_sensitivity = t_tp / (t_tp + t_fn) if (t_tp + t_fn) > 0 else 0.0
    trial_specificity = t_tn / (t_tn + t_fp) if (t_tn + t_fp) > 0 else 0.0
    trial_acc = accuracy_score(y, trial_pred_all)
    trial_prec = precision_score(y, trial_pred_all, zero_division=0)
    trial_rec = recall_score(y, trial_pred_all, zero_division=0)
    trial_f1 = f1_score(y, trial_pred_all, zero_division=0)
    trial_auc = roc_auc_score(y, trial_prob_all)

    cv_results[name] = {
        "participant_metrics": {
            "accuracy": round(part_acc, 4),
            "precision": round(part_prec, 4),
            "recall": round(part_rec, 4),
            "sensitivity": round(part_sensitivity, 4),
            "specificity": round(part_specificity, 4),
            "f1_score": round(part_f1, 4),
            "roc_auc": round(part_auc, 4),
            "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
            "fold_means": {
                "acc_mean": round(float(np.mean([m["acc"] for m in fold_part_metrics])), 4),
                "acc_std": round(float(np.std([m["acc"] for m in fold_part_metrics])), 4),
                "f1_mean": round(float(np.mean([m["f1"] for m in fold_part_metrics])), 4),
                "f1_std": round(float(np.std([m["f1"] for m in fold_part_metrics])), 4),
                "auc_mean": round(float(np.mean([m["auc"] for m in fold_part_metrics])), 4),
                "auc_std": round(float(np.std([m["auc"] for m in fold_part_metrics])), 4),
            }
        },
        "trial_metrics": {
            "accuracy": round(trial_acc, 4),
            "precision": round(trial_prec, 4),
            "recall": round(trial_rec, 4),
            "sensitivity": round(trial_sensitivity, 4),
            "specificity": round(trial_specificity, 4),
            "f1_score": round(trial_f1, 4),
            "roc_auc": round(trial_auc, 4),
            "confusion_matrix": {"TN": int(t_tn), "FP": int(t_fp), "FN": int(t_fn), "TP": int(t_tp)},
            "fold_means": {
                "acc_mean": round(float(np.mean([m["acc"] for m in fold_trial_metrics])), 4),
                "acc_std": round(float(np.std([m["acc"] for m in fold_trial_metrics])), 4),
                "f1_mean": round(float(np.mean([m["f1"] for m in fold_trial_metrics])), 4),
                "f1_std": round(float(np.std([m["f1"] for m in fold_trial_metrics])), 4),
                "auc_mean": round(float(np.mean([m["auc"] for m in fold_trial_metrics])), 4),
                "auc_std": round(float(np.std([m["auc"] for m in fold_trial_metrics])), 4),
            }
        }
    }
    
    print(f"  [Participant-Level] Acc: {part_acc*100:.2f}% | Sensitivity: {part_sensitivity*100:.2f}% | Specificity: {part_specificity*100:.2f}% | F1: {part_f1*100:.2f}% | AUC: {part_auc*100:.2f}%")
    print(f"                      Confusion: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print(f"  [Trial-Level]       Acc: {trial_acc*100:.2f}% | Sensitivity: {trial_sensitivity*100:.2f}% | Specificity: {trial_specificity*100:.2f}% | F1: {trial_f1*100:.2f}% | AUC: {trial_auc*100:.2f}%")

# Select Best Model based on Participant-Level F1 & AUC
best_model_name = max(cv_results.keys(), key=lambda k: (cv_results[k]["participant_metrics"]["f1_score"], cv_results[k]["participant_metrics"]["roc_auc"]))
best_metrics = cv_results[best_model_name]["participant_metrics"]
print("\n" + "=" * 70)
print(f"BEST MODEL SELECTED: {best_model_name}")
print(f"  Participant Accuracy:    {best_metrics['accuracy']*100:.2f}%")
print(f"  Participant Sensitivity: {best_metrics['sensitivity']*100:.2f}% (Recall for Previous ACL Injury)")
print(f"  Participant Specificity: {best_metrics['specificity']*100:.2f}% (Recall for Healthy Controls)")
print(f"  Participant F1-Score:    {best_metrics['f1_score']*100:.2f}%")
print(f"  Participant ROC-AUC:     {best_metrics['roc_auc']*100:.2f}%")
print("=" * 70)

# Save Benchmark Comparison JSON
bench_path = os.path.join(OUTPUT_DIR, "cv_benchmark_results.json")
with open(bench_path, "w") as f:
    json.dump(cv_results, f, indent=2)
print(f"Saved algorithm comparison benchmark to: {bench_path}")

# Train Final Production Pipeline on Full Dataset
full_scaler = StandardScaler()
X_full_scaled = full_scaler.fit_transform(X)
final_model = models[best_model_name]
final_model.fit(X_full_scaled, y)

# Save model & scaler
model_path = os.path.join(OUTPUT_DIR, "best_acl_biomechanical_model.joblib")
scaler_path = os.path.join(OUTPUT_DIR, "scaler.joblib")
joblib.dump(final_model, model_path)
joblib.dump(full_scaler, scaler_path)
print(f"Saved best model artifact to: {model_path}")
print(f"Saved feature scaler artifact to: {scaler_path}")

# Feature Importances (if available)
feature_importances = {}
if hasattr(final_model, 'feature_importances_'):
    imp = final_model.feature_importances_
    for col, val in zip(feature_cols, imp):
        feature_importances[col] = float(val)
elif hasattr(final_model, 'coef_'):
    coef = np.abs(final_model.coef_[0])
    for col, val in zip(feature_cols, coef):
        feature_importances[col] = float(val)

# Sort feature importances
sorted_imp = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
df_imp = pd.DataFrame(sorted_imp, columns=["feature", "importance"])
df_imp.to_csv(os.path.join(OUTPUT_DIR, "feature_importance.csv"), index=False)
with open(os.path.join(OUTPUT_DIR, "feature_importance.json"), "w") as f:
    json.dump(dict(sorted_imp), f, indent=2)
print("Saved feature importance rankings.")

# Save Model Metadata
meta = {
    "model_name": best_model_name,
    "model_type": str(type(final_model)),
    "n_participants": int(df['participant_id'].nunique()),
    "n_trials": int(len(df)),
    "classes": ["Healthy_Control", "Previous_ACL_Injury"],
    "target_mapping": {"0": "Healthy_Control", "1": "Previous_ACL_Injury"},
    "feature_count": len(feature_cols),
    "feature_names": feature_cols,
    "hyperparameters": final_model.get_params(),
    "validation_protocol": "5-Fold StratifiedGroupKFold (Zero Data Leakage, Participant-Level Splitting)",
    "participant_level_performance": best_metrics,
    "trial_level_performance": cv_results[best_model_name]["trial_metrics"]
}
with open(os.path.join(OUTPUT_DIR, "model_metadata.json"), "w") as f:
    json.dump(meta, f, indent=2)

# Save Confusion Matrices
pd.DataFrame([best_metrics["confusion_matrix"]]).to_csv(os.path.join(OUTPUT_DIR, "confusion_matrix_participant.csv"), index=False)
pd.DataFrame([cv_results[best_model_name]["trial_metrics"]["confusion_matrix"]]).to_csv(os.path.join(OUTPUT_DIR, "confusion_matrix_trial.csv"), index=False)

# -------------------------------------------------------------
# PLOTTING: Visualizations
# -------------------------------------------------------------
plt.figure(figsize=(10, 8))
for name in models:
    # Participant level ROC curve
    p_true = [participant_ground_truth[s] for s in all_subs]
    p_prob = [oof_predictions[name]["part_probs"][s] for s in all_subs]
    fpr, tpr, _ = roc_curve(p_true, p_prob)
    auc_val = cv_results[name]["participant_metrics"]["roc_auc"]
    plt.plot(fpr, tpr, lw=2, label=f"{name.replace('_', ' ')} (AUC = {auc_val:.3f})")

plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label="Chance Level (AUC = 0.50)")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
plt.ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=12)
plt.title("ROC Curves – Participant-Level ACL Biomechanical Classification\n(5-Fold StratifiedGroupKFold, Zero Leakage)", fontsize=13)
plt.legend(loc="lower right", fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
roc_path = os.path.join(OUTPUT_DIR, "roc_curve_comparison.png")
plt.savefig(roc_path, dpi=300)
plt.close()
print(f"Saved ROC curve plot to: {roc_path}")

# Top 15 Feature Importance Plot
if sorted_imp:
    plt.figure(figsize=(11, 7))
    top_15 = sorted_imp[:15]
    names_top = [x[0] for x in top_15][::-1]
    vals_top = [x[1] for x in top_15][::-1]
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(names_top)))
    bars = plt.barh(names_top, vals_top, color=colors)
    plt.xlabel("Relative Feature Importance / Coefficient Magnitude", fontsize=12)
    plt.title(f"Top 15 Most Discriminative Biomechanical Features\n({best_model_name.replace('_', ' ')})", fontsize=13)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    imp_path = os.path.join(OUTPUT_DIR, "feature_importance_top15.png")
    plt.savefig(imp_path, dpi=300)
    plt.close()
    print(f"Saved feature importance plot to: {imp_path}")

# Confusion Matrix Heatmap
cm_vals = np.array([
    [best_metrics["confusion_matrix"]["TN"], best_metrics["confusion_matrix"]["FP"]],
    [best_metrics["confusion_matrix"]["FN"], best_metrics["confusion_matrix"]["TP"]]
])
plt.figure(figsize=(7, 6))
sns.heatmap(cm_vals, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=["Healthy Control (Pred)", "Previous ACL (Pred)"],
            yticklabels=["Healthy Control (True)", "Previous ACL (True)"],
            annot_kws={"size": 16, "weight": "bold"})
plt.title(f"Participant-Level Confusion Matrix – {best_model_name.replace('_', ' ')}\n(Overall Accuracy: {best_metrics['accuracy']*100:.1f}%)", fontsize=12)
plt.tight_layout()
cm_path = os.path.join(OUTPUT_DIR, "confusion_matrix_participant.png")
plt.savefig(cm_path, dpi=300)
plt.close()
print(f"Saved confusion matrix plot to: {cm_path}")

print("\nModel training and benchmark execution completed successfully!")

