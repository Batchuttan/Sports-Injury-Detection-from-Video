"""
Evaluation & Benchmarking Script for Sports Activity Classification
Pure NumPy implementation:
- Test Accuracy, Precision, Recall, F1-Score
- Per-class Performance Matrix
- Full Confusion Matrix
- Targeted Analysis of Confused Pairs (Sprinting vs Jumping, Jumping vs Landing, Squatting vs Landing, etc.)
"""

import os
import sys
import json
import numpy as np
import torch

# Ensure workspace root and ml directory are in sys.path for IDE & CLI import resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
ML_DIR = os.path.dirname(os.path.abspath(__file__))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

try:
    from ml.models import SportsActionSTNet
except ImportError:
    from models import SportsActionSTNet

FEATURES_PATH = os.path.join(BASE_DIR, "ml", "dataset_features.npz")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")
BEST_MODEL_PATH = os.path.join(SAVED_MODELS_DIR, "best_sports_action_model.pt")
SPLIT_PATH = os.path.join(SAVED_MODELS_DIR, "eval_split.npz")
REPORT_PATH = os.path.join(SAVED_MODELS_DIR, "evaluation_report.json")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = [
    "Jumping",
    "Squatting",
    "Sprinting",
    "Landing",
    "Throwing",
    "Cutting Movements",
    "Sports Specific Drills"
]

def compute_metrics(y_true, y_pred, num_classes=7):
    """Computes comprehensive classification metrics using pure NumPy."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    acc = float(np.mean(y_true == y_pred)) if len(y_true) > 0 else 0.0
    
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    
    precisions = np.zeros(num_classes, dtype=float)
    recalls = np.zeros(num_classes, dtype=float)
    f1s = np.zeros(num_classes, dtype=float)
    supports = np.zeros(num_classes, dtype=int)
    
    for c in range(num_classes):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        supports[c] = cm[c, :].sum()
        precisions[c] = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recalls[c] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        denom = precisions[c] + recalls[c]
        f1s[c] = float(2 * precisions[c] * recalls[c] / denom) if denom > 0 else 0.0
        
    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))
    
    total_supp = int(supports.sum())
    weighted_f1 = float(np.sum(f1s * supports) / total_supp) if total_supp > 0 else 0.0
    weighted_prec = float(np.sum(precisions * supports) / total_supp) if total_supp > 0 else 0.0
    weighted_rec = float(np.sum(recalls * supports) / total_supp) if total_supp > 0 else 0.0

    return {
        "accuracy": acc,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_prec,
        "weighted_recall": weighted_rec,
        "weighted_f1": weighted_f1,
        "precisions": precisions,
        "recalls": recalls,
        "f1s": f1s,
        "supports": supports,
        "confusion_matrix": cm
    }

def run_evaluation():
    print(f"Loading evaluation dataset and model on {DEVICE}...")
    if not os.path.exists(FEATURES_PATH) or not os.path.exists(SPLIT_PATH) or not os.path.exists(BEST_MODEL_PATH):
        raise FileNotFoundError("Required model checkpoints or features not found in ml/saved_models.")

    data = np.load(FEATURES_PATH, allow_pickle=True)
    features = data["features"]
    labels = data["labels"]
    
    split = np.load(SPLIT_PATH, allow_pickle=True)
    test_idx = split["test_idx"]
    val_idx = split["val_idx"]
    train_idx = split["train_idx"]
    history = split["history"].item() if "history" in split else {}

    print(f"Loaded {len(test_idx)} completely unseen test video samples.")

    # Load Model Checkpoint
    checkpoint = torch.load(BEST_MODEL_PATH, map_location=DEVICE)
    in_features = int(checkpoint.get("in_features", features.shape[2]))
    
    model = SportsActionSTNet(
        in_features=in_features,
        num_classes=len(CLASSES),
        conv_dim=128,
        lstm_hidden=128,
        num_lstm_layers=2,
        dropout=0.0
    ).to(DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    def evaluate_split(indices):
        x = torch.from_numpy(features[indices]).float().to(DEVICE)
        y = labels[indices]
        with torch.no_grad():
            logits, attn = model(x)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)
        return y, preds, probs

    train_y, train_preds, _ = evaluate_split(train_idx)
    val_y, val_preds, _ = evaluate_split(val_idx)
    test_y, test_preds, _ = evaluate_split(test_idx)

    train_acc = float(np.mean(train_y == train_preds)) if len(train_y) > 0 else 0.0
    val_acc = float(np.mean(val_y == val_preds)) if len(val_y) > 0 else 0.0
    
    test_metrics = compute_metrics(test_y, test_preds, len(CLASSES))
    acc = test_metrics["accuracy"]
    m_prec = test_metrics["macro_precision"]
    m_rec = test_metrics["macro_recall"]
    m_f1 = test_metrics["macro_f1"]
    w_f1 = test_metrics["weighted_f1"]
    p_cls = test_metrics["precisions"]
    r_cls = test_metrics["recalls"]
    f_cls = test_metrics["f1s"]
    s_cls = test_metrics["supports"]
    cm = test_metrics["confusion_matrix"]

    # Print Formatted Report
    print("\n" + "=" * 70)
    print("                 AI MODEL EVALUATION & BENCHMARK REPORT")
    print("=" * 70)
    print(f"  Training Accuracy:   {train_acc * 100:.2f}%")
    print(f"  Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"  Testing Accuracy:    {acc * 100:.2f}% (Completely Unseen Test Videos)")
    print(f"  Macro Precision:     {m_prec * 100:.2f}%")
    print(f"  Macro Recall:        {m_rec * 100:.2f}%")
    print(f"  Macro F1-Score:      {m_f1 * 100:.2f}%")
    print(f"  Weighted F1-Score:   {w_f1 * 100:.2f}%")
    print("-" * 70)

    print("\nPER-CLASS CLASSIFICATION PERFORMANCE:")
    print(f"{'Class Name':<26} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<8}")
    print("-" * 70)
    per_class_results = {}
    for i, name in enumerate(CLASSES):
        p = float(p_cls[i])
        r = float(r_cls[i])
        f = float(f_cls[i])
        s = int(s_cls[i])
        per_class_results[name] = {"precision": p, "recall": r, "f1_score": f, "support": s}
        print(f"{name:<26} {p*100:>10.2f}% {r*100:>10.2f}% {f*100:>10.2f}% {s:>8d}")
    print("-" * 70)

    print("\nCONFUSION MATRIX (Rows: Ground Truth, Columns: Predicted):")
    header = "       " + "".join([f"{name[:6]:>8}" for name in CLASSES])
    print(header)
    for i, row in enumerate(cm):
        row_str = f"{CLASSES[i][:6]:<7}" + "".join([f"{val:>8d}" for val in row])
        print(row_str)

    # Specific Misclassification Analysis for Challenging Action Pairs
    print("\nTARGETED MISCLASSIFICATION PAIR AUDIT:")
    print("-" * 70)
    PAIRS = [
        ("Sprinting", "Jumping"),
        ("Jumping", "Landing"),
        ("Squatting", "Landing"),
        ("Sprinting", "Sports Specific Drills"),
        ("Throwing", "Sports Specific Drills"),
        ("Cutting Movements", "Sprinting")
    ]
    pair_audit = {}
    for c1, c2 in PAIRS:
        i1 = CLASSES.index(c1)
        i2 = CLASSES.index(c2)
        conf_1_to_2 = int(cm[i1, i2])
        conf_2_to_1 = int(cm[i2, i1])
        total_eval = int(cm[i1].sum() + cm[i2].sum())
        pair_audit[f"{c1} vs {c2}"] = {
            f"{c1} predicted as {c2}": conf_1_to_2,
            f"{c2} predicted as {c1}": conf_2_to_1,
            "resolved_status": "EXCELLENT" if (conf_1_to_2 + conf_2_to_1) == 0 else "CONTROLLED" if (conf_1_to_2 + conf_2_to_1) <= 2 else "NEEDS MORE DATA"
        }
        print(f"  [{pair_audit[f'{c1} vs {c2}']['resolved_status']:<14}] {c1} vs {c2}: "
              f"{conf_1_to_2} {c1}->{c2}, {conf_2_to_1} {c2}->{c1} (out of {total_eval} clips)")
    print("-" * 70)

    # Save detailed JSON report
    report_data = {
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "test_accuracy": acc,
        "macro_precision": m_prec,
        "macro_recall": m_rec,
        "macro_f1": m_f1,
        "weighted_f1": w_f1,
        "per_class": per_class_results,
        "confusion_matrix": cm.tolist(),
        "pair_audit": pair_audit,
        "history": history
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nEvaluation report successfully saved to: {REPORT_PATH}")
    return report_data

if __name__ == "__main__":
    run_evaluation()
