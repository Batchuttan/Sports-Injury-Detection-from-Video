"""
Training Script for Sports Activity Classification
Trains Spatial-Temporal CNN-BiLSTM with Group-Level Splitting and Anti-Overfitting Techniques.
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

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
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

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
    
    return {
        "accuracy": acc,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "precisions": precisions,
        "recalls": recalls,
        "f1s": f1s,
        "supports": supports,
        "confusion_matrix": cm
    }

class SportsKinematicDataset(Dataset):
    def __init__(self, features, labels, is_train=False):
        self.features = np.asarray(features, dtype=np.float32)  # (N, T, 95)
        self.labels = np.asarray(labels, dtype=np.int64)        # (N,)
        self.is_train = is_train

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        feat = self.features[idx].copy()  # (T, 95)
        label = int(self.labels[idx])

        if self.is_train:
            # 1. Coordinate Jitter (Gaussian noise on x, y coordinates)
            if np.random.rand() > 0.5:
                noise = np.random.normal(0, 0.015, feat[:, :34].shape).astype(np.float32)
                feat[:, :34] = np.clip(feat[:, :34] + noise, 0.0, 1.0)

            # 2. Velocity scaling (speed variation: 0.85x to 1.15x)
            if np.random.rand() > 0.5:
                scale = float(np.random.uniform(0.85, 1.15))
                feat[:, 51:85] = feat[:, 51:85] * scale

            # 3. Horizontal Flip (anatomical joint swap for bilateral invariance)
            if np.random.rand() > 0.5:
                # Mirror x-coordinates: x_norm = 1.0 - x_norm
                feat[:, 0:34:2] = 1.0 - feat[:, 0:34:2]
                # Invert x-velocities: vx = -vx
                feat[:, 51:85:2] = -feat[:, 51:85:2]
                # Swap L/R keypoints (e.g. 5<->6, 7<->8, 9<->10, 11<->12, 13<->14, 15<->16)
                pairs = [(5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16), (1, 2), (3, 4)]
                for p1, p2 in pairs:
                    feat[:, [p1*2, p2*2]] = feat[:, [p2*2, p1*2]]
                    feat[:, [p1*2+1, p2*2+1]] = feat[:, [p2*2+1, p1*2+1]]
                    feat[:, [34+p1, 34+p2]] = feat[:, [34+p2, 34+p1]]
                    feat[:, [51+p1*2, 51+p2*2]] = feat[:, [51+p2*2, 51+p1*2]]
                    feat[:, [51+p1*2+1, 51+p2*2+1]] = feat[:, [51+p2*2+1, 51+p1*2+1]]
                # Swap knee/hip/elbow angles (indices 85/86, 87/88, 89/90)
                feat[:, [85, 86]] = feat[:, [86, 85]]
                feat[:, [87, 88]] = feat[:, [88, 87]]
                feat[:, [89, 90]] = feat[:, [90, 89]]

            # 4. Temporal shift (circular roll shift of frames)
            if np.random.rand() > 0.5:
                shift = int(np.random.randint(-3, 4))
                feat = np.roll(feat, shift, axis=0)

        return torch.from_numpy(feat).float(), torch.tensor(label, dtype=torch.long)

def group_level_split(groups, labels, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42):
    """
    Split at the original-video / source-group level to prevent data leakage.
    Ensures all clips from group_XX belong exclusively to either train, val, or test.
    """
    np.random.seed(seed)
    unique_groups = np.unique(groups)
    np.random.shuffle(unique_groups)

    n_groups = len(unique_groups)
    n_train = int(round(train_ratio * n_groups))
    n_val = int(round(val_ratio * n_groups))

    train_groups = set(unique_groups[:n_train])
    val_groups = set(unique_groups[n_train:n_train + n_val])
    test_groups = set(unique_groups[n_train + n_val:])

    train_idx = [i for i, g in enumerate(groups) if g in train_groups]
    val_idx = [i for i, g in enumerate(groups) if g in val_groups]
    test_idx = [i for i, g in enumerate(groups) if g in test_groups]

    return train_idx, val_idx, test_idx

def train_model():
    print(f"Loading extracted features from: {FEATURES_PATH}")
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Features file {FEATURES_PATH} not found. Run extract_features.py first.")

    data = np.load(FEATURES_PATH, allow_pickle=True)
    features = data["features"]  # (N, T, D)
    labels = data["labels"]      # (N,)
    groups = data["groups"]      # (N,)

    print(f"Loaded {len(features)} total kinematic samples. Dimensions: {features.shape}")

    # Group-level split (70% Train, 15% Val, 15% Test)
    train_idx, val_idx, test_idx = group_level_split(groups, labels, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    print(f"Split sizes: Train={len(train_idx)} ({len(train_idx)/len(features)*100:.1f}%), "
          f"Val={len(val_idx)} ({len(val_idx)/len(features)*100:.1f}%), "
          f"Test={len(test_idx)} ({len(test_idx)/len(features)*100:.1f}%)")

    # Verify zero group leakage
    train_g = set(groups[train_idx])
    val_g = set(groups[val_idx])
    test_g = set(groups[test_idx])
    assert len(train_g.intersection(val_g)) == 0, "Data Leakage: Overlap between Train and Val groups!"
    assert len(train_g.intersection(test_g)) == 0, "Data Leakage: Overlap between Train and Test groups!"
    assert len(val_g.intersection(test_g)) == 0, "Data Leakage: Overlap between Val and Test groups!"
    print("Zero Data Leakage Confirmed: Strict separation by source group.")

    # Class distribution & weighting
    class_counts = np.bincount(labels[train_idx], minlength=len(CLASSES))
    total_samples = len(train_idx)
    class_weights = total_samples / (len(CLASSES) * np.maximum(1, class_counts))
    class_weights_t = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)
    print("\nClass distribution in Training Set:")
    for i, c in enumerate(CLASSES):
        print(f"  {c:24s}: {class_counts[i]:4d} clips (weight={class_weights[i]:.2f})")

    # Datasets and Loaders
    train_dataset = SportsKinematicDataset(features[train_idx], labels[train_idx], is_train=True)
    val_dataset = SportsKinematicDataset(features[val_idx], labels[val_idx], is_train=False)
    test_dataset = SportsKinematicDataset(features[test_idx], labels[test_idx], is_train=False)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # Initialize Model
    in_features = int(features.shape[2])  # 95
    model = SportsActionSTNet(
        in_features=in_features,
        num_classes=len(CLASSES),
        conv_dim=128,
        lstm_hidden=128,
        num_lstm_layers=2,
        dropout=0.40
    ).to(DEVICE)

    criterion = nn.CrossEntropyLoss(weight=class_weights_t, label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=40, eta_min=1e-5)

    print(f"\nModel Architecture initialized on {DEVICE}:")
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total trainable parameters: {total_params:,}")

    # Training Loop
    EPOCHS = 40
    best_val_f1 = 0.0
    best_epoch = 0
    patience = 12
    patience_counter = 0

    history = {
        "train_loss": [], "train_acc": [],
        "val_loss": [], "val_acc": [], "val_f1": []
    }

    best_model_path = os.path.join(SAVED_MODELS_DIR, "best_sports_action_model.pt")

    for epoch in range(1, EPOCHS + 1):
        # 1. Training Phase
        model.train()
        running_loss = 0.0
        train_preds, train_trues = [], []

        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(DEVICE)
            y_batch = y_batch.to(DEVICE)

            optimizer.zero_grad()
            logits, _ = model(x_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()

            running_loss += float(loss.item()) * len(y_batch)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            train_preds.extend(preds)
            train_trues.extend(y_batch.cpu().numpy())

        scheduler.step()
        epoch_train_loss = running_loss / len(train_dataset)
        train_metrics = compute_metrics(train_trues, train_preds, len(CLASSES))
        train_acc = train_metrics["accuracy"]

        # 2. Validation Phase
        model.eval()
        val_loss = 0.0
        val_preds, val_trues = [], []

        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch = x_batch.to(DEVICE)
                y_batch = y_batch.to(DEVICE)

                logits, _ = model(x_batch)
                loss = criterion(logits, y_batch)

                val_loss += float(loss.item()) * len(y_batch)
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_trues.extend(y_batch.cpu().numpy())

        epoch_val_loss = val_loss / len(val_dataset)
        val_metrics = compute_metrics(val_trues, val_preds, len(CLASSES))
        val_acc = val_metrics["accuracy"]
        epoch_val_f1 = val_metrics["macro_f1"]

        history["train_loss"].append(epoch_train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(epoch_val_loss)
        history["val_acc"].append(val_acc)
        history["val_f1"].append(epoch_val_f1)

        print(f"Epoch {epoch:2d}/{EPOCHS:2d} | "
              f"Train Loss: {epoch_train_loss:.4f}, Acc: {train_acc*100:.1f}% | "
              f"Val Loss: {epoch_val_loss:.4f}, Acc: {val_acc*100:.1f}%, Macro-F1: {epoch_val_f1*100:.1f}%")

        # Save Best Model Checkpoint
        if epoch_val_f1 > best_val_f1:
            best_val_f1 = epoch_val_f1
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_f1": best_val_f1,
                "val_acc": val_acc,
                "in_features": in_features,
                "classes": CLASSES
            }, best_model_path)
            print(f"  --> Saved new best model checkpoint (Val Macro-F1: {best_val_f1*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping triggered after {epoch} epochs (Best epoch was {best_epoch}).")
                break

    print(f"\nTraining Complete. Best Validation Macro-F1: {best_val_f1*100:.2f}% at epoch {best_epoch}.")

    # Save model configuration & label mapping
    config = {
        "model_architecture": "SportsActionSTNet (Spatial-Temporal 1D-CNN + BiLSTM + Temporal Attention)",
        "in_features": in_features,
        "sequence_length": 32,
        "num_classes": len(CLASSES),
        "classes": CLASSES,
        "class_mapping": {i: c for i, c in enumerate(CLASSES)},
        "best_epoch": best_epoch,
        "best_val_macro_f1": float(best_val_f1),
        "best_model_weights": best_model_path,
        "normalization": "Bounding-box / Torso height normalized coordinates + angular velocities"
    }
    with open(os.path.join(SAVED_MODELS_DIR, "model_config.json"), "w") as f:
        json.dump(config, f, indent=2)

    with open(os.path.join(SAVED_MODELS_DIR, "label_mapping.json"), "w") as f:
        json.dump({i: c for i, c in enumerate(CLASSES)}, f, indent=2)

    # Save split metadata for evaluation
    np.savez_compressed(
        os.path.join(SAVED_MODELS_DIR, "eval_split.npz"),
        test_idx=test_idx,
        val_idx=val_idx,
        train_idx=train_idx,
        history=np.array(history, dtype=object)
    )
    print(f"Saved model config and evaluation partition metadata to: {SAVED_MODELS_DIR}")

if __name__ == "__main__":
    train_model()
