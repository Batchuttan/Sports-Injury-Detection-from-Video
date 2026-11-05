"""
Participant-Level Aggregated Feature Modeling & Leave-One-Subject-Out (LOSO) Validation
Each of the 43 participants is summarized into:
- Mean and standard deviation across all trials for each biomechanical variable
- Tested under 43-Fold Leave-One-Subject-Out (LOSO) Cross-Validation
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

DATASET_ROOT = r"C:\Users\User\Downloads\28890545"
CSV_PATH = os.path.join(DATASET_ROOT, "ACL_Model_Output", "extracted_biomechanical_features.csv")
OUTPUT_DIR = os.path.join(DATASET_ROOT, "ACL_Model_Output")

df = pd.read_csv(CSV_PATH)
meta_cols = ["participant_id", "sub_num", "task", "limb", "rep", "is_fatigued", "target"]
feature_cols = [c for c in df.columns if c not in meta_cols]

# Build Participant-level summary table (Mean and Std per participant)
grouped = df.groupby(["participant_id", "target"])
df_mean = grouped[feature_cols].mean().reset_index()
df_std = grouped[feature_cols].std().fillna(0).reset_index()

# Rename std columns
df_std = df_std.rename(columns={c: f"{c}_std" for c in feature_cols})
df_part = pd.merge(df_mean, df_std.drop(columns=["target"]), on="participant_id")

part_feature_cols = [c for c in df_part.columns if c not in ["participant_id", "target"]]
X_part = df_part[part_feature_cols].values
y_part = df_part["target"].values
groups_part = df_part["participant_id"].values

print(f"Participant-level dataset: {X_part.shape[0]} subjects, {X_part.shape[1]} aggregated features")

logo = LeaveOneGroupOut()
models = {
    "Logistic_Regression_L2": LogisticRegression(C=0.1, penalty='l2', max_iter=1000, random_state=42),
    "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=4, min_samples_leaf=2, max_features='sqrt', random_state=42),
    "SVM_RBF": SVC(C=1.0, kernel='rbf', probability=True, random_state=42)
}

loso_results = {}

for name, model in models.items():
    y_preds = []
    y_probs = []
    y_trues = []
    
    for train_idx, test_idx in logo.split(X_part, y_part, groups=groups_part):
        X_tr, y_tr = X_part[train_idx], y_part[train_idx]
        X_te, y_te = X_part[test_idx], y_part[test_idx]
        
        scaler = StandardScaler()
        X_tr_sc = scaler.fit_transform(X_tr)
        X_te_sc = scaler.transform(X_te)
        
        model.fit(X_tr_sc, y_tr)
        prob = model.predict_proba(X_te_sc)[0, 1]
        pred = int(prob >= 0.5)
        
        y_preds.append(pred)
        y_probs.append(prob)
        y_trues.append(int(y_te[0]))
        
    acc = accuracy_score(y_trues, y_preds)
    prec = precision_score(y_trues, y_preds, zero_division=0)
    rec = recall_score(y_trues, y_preds, zero_division=0)
    f1 = f1_score(y_trues, y_preds, zero_division=0)
    auc = roc_auc_score(y_trues, y_probs)
    cm = confusion_matrix(y_trues, y_preds)
    tn, fp, fn, tp = cm.ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    loso_results[name] = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "sensitivity": round(sens, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}
    }
    print(f"LOSO {name:24s} | Acc: {acc*100:.2f}% | Sens: {sens*100:.2f}% | Spec: {spec*100:.2f}% | F1: {f1*100:.2f}% | AUC: {auc*100:.2f}% (TN={tn}, FP={fp}, FN={fn}, TP={tp})")

# Save LOSO results
with open(os.path.join(OUTPUT_DIR, "loso_cv_results.json"), "w") as f:
    json.dump(loso_results, f, indent=2)
print("Saved LOSO benchmark results to loso_cv_results.json")
