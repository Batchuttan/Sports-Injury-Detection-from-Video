"""
Training Pipeline for SPRINTING vs NOT SPRINTING Temporal Recognition Model
Architecture: SprintTemporalNet (1D Conv + BiGRU + Temporal Attention + MLP Head)
Stratified Video-Level Split (70% Train, 15% Val, 15% Test)
Zero Data Leakage
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPZ_PATH = os.path.join(BASE_DIR, "ml", "sprint_features.npz")
SAVED_DIR = os.path.join(BASE_DIR, "ml", "saved_models", "sprint_model")
os.makedirs(SAVED_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on device: {DEVICE}")

# 1. Dataset & Augmentation
class SprintPoseDataset(Dataset):
    def __init__(self, features, labels, is_train=False):
        self.features = features
        self.labels = labels
        self.is_train = is_train

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        feat = self.features[idx].copy()  # (32, 95)
        
        if self.is_train:
            # 1. Gaussian noise on coordinates
            if np.random.rand() > 0.4:
                feat[:, :34] += np.random.normal(0, 0.015, feat[:, :34].shape).astype(np.float32)
                
            # 2. Random temporal roll (phase shift)
            if np.random.rand() > 0.4:
                shift = np.random.randint(-4, 5)
                feat = np.roll(feat, shift, axis=0)
                
            # 3. Random temporal frame dropout (simulate occlusion)
            if np.random.rand() > 0.4:
                drop_mask = (np.random.rand(32, 1) > 0.1).astype(np.float32)
                feat = feat * drop_mask
                
        return torch.tensor(feat, dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.long)

# 2. Model Architecture: SprintTemporalNet
class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, rnn_out):
        # rnn_out: (B, T, hidden_dim)
        scores = self.attn(torch.tanh(rnn_out))  # (B, T, 1)
        weights = F.softmax(scores, dim=1)        # (B, T, 1)
        context = torch.sum(rnn_out * weights, dim=1)  # (B, hidden_dim)
        return context, weights

class SprintTemporalNet(nn.Module):
    def __init__(self, in_features=95, conv_dim=64, rnn_dim=64, num_classes=2, dropout=0.3):
        super().__init__()
        
        # 1D Temporal Convolution
        self.conv1 = nn.Conv1d(in_features, conv_dim, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(conv_dim)
        self.relu = nn.ReLU()
        
        # Bidirectional GRU (2 layers)
        self.gru = nn.GRU(
            input_size=conv_dim,
            hidden_size=rnn_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if dropout > 0 else 0
        )
        
        # Temporal Attention
        self.attention = TemporalAttention(rnn_dim * 2)
        
        # Classification MLP
        self.head = nn.Sequential(
            nn.Linear(rnn_dim * 2, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x: (B, T, in_features)
        # Conv1d expects (B, C, T)
        x_conv = x.transpose(1, 2)
        h = self.relu(self.bn1(self.conv1(x_conv)))
        h = h.transpose(1, 2)  # (B, T, conv_dim)
        
        # GRU
        gru_out, _ = self.gru(h)  # (B, T, rnn_dim * 2)
        
        # Attention Pooling
        context, attn_weights = self.attention(gru_out)  # (B, rnn_dim * 2)
        
        # Classification Logits
        logits = self.head(context)  # (B, num_classes)
        return logits

def train_sprint_model():
    print("Loading sprint dataset...")
    data = np.load(NPZ_PATH)
    features = data["features"]
    labels = data["labels"]
    
    n_total = len(labels)
    print(f"Loaded {n_total} video samples. (Sprinting: {np.sum(labels == 1)}, Not Sprinting: {np.sum(labels == 0)})")
    
    # Stratified Train/Val/Test Split (70% / 15% / 15%)
    np.random.seed(42)
    pos_idx = np.where(labels == 1)[0]
    neg_idx = np.where(labels == 0)[0]
    
    np.random.shuffle(pos_idx)
    np.random.shuffle(neg_idx)
    
    n_pos_train = int(0.70 * len(pos_idx))
    n_pos_val = int(0.15 * len(pos_idx))
    
    n_neg_train = int(0.70 * len(neg_idx))
    n_neg_val = int(0.15 * len(neg_idx))
    
    train_idx = np.concatenate([pos_idx[:n_pos_train], neg_idx[:n_neg_train]])
    val_idx = np.concatenate([pos_idx[n_pos_train:n_pos_train+n_pos_val], neg_idx[n_neg_train:n_neg_train+n_neg_val]])
    test_idx = np.concatenate([pos_idx[n_pos_train+n_pos_val:], neg_idx[n_neg_train+n_neg_val:]])
    
    np.random.shuffle(train_idx)
    np.random.shuffle(val_idx)
    np.random.shuffle(test_idx)
    
    print(f"Dataset Partitions:")
    print(f"  Train:      {len(train_idx)} samples (Sprinting: {np.sum(labels[train_idx] == 1)}, Not: {np.sum(labels[train_idx] == 0)})")
    print(f"  Validation: {len(val_idx)} samples (Sprinting: {np.sum(labels[val_idx] == 1)}, Not: {np.sum(labels[val_idx] == 0)})")
    print(f"  Test:       {len(test_idx)} samples (Sprinting: {np.sum(labels[test_idx] == 1)}, Not: {np.sum(labels[test_idx] == 0)})")
    
    train_ds = SprintPoseDataset(features[train_idx], labels[train_idx], is_train=True)
    val_ds = SprintPoseDataset(features[val_idx], labels[val_idx], is_train=False)
    test_ds = SprintPoseDataset(features[test_idx], labels[test_idx], is_train=False)
    
    train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=16, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=16, shuffle=False)
    
    model = SprintTemporalNet(in_features=95, conv_dim=64, rnn_dim=64, num_classes=2, dropout=0.3).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=35, eta_min=1e-5)
    
    # Class weights for slight imbalance
    pos_weight = float(len(labels[train_idx]) - np.sum(labels[train_idx] == 1)) / float(np.sum(labels[train_idx] == 1))
    class_weights = torch.tensor([1.0, pos_weight], dtype=torch.float32).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.08)
    
    best_val_f1 = 0.0
    best_epoch = 0
    best_model_path = os.path.join(SAVED_DIR, "best_sprint_model.pt")
    
    print("\nStarting model training...")
    for epoch in range(1, 36):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for x_b, y_b in train_loader:
            x_b, y_b = x_b.to(DEVICE), y_b.to(DEVICE)
            optimizer.zero_grad()
            logits = model(x_b)
            loss = criterion(logits, y_b)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            
            train_loss += loss.item() * len(y_b)
            preds = torch.argmax(logits, dim=1)
            train_correct += (preds == y_b).sum().item()
            train_total += len(y_b)
            
        scheduler.step()
        train_loss /= train_total
        train_acc = train_correct / train_total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_preds_all = []
        val_trues_all = []
        
        with torch.no_grad():
            for x_b, y_b in val_loader:
                x_b, y_b = x_b.to(DEVICE), y_b.to(DEVICE)
                logits = model(x_b)
                loss = criterion(logits, y_b)
                val_loss += loss.item() * len(y_b)
                preds = torch.argmax(logits, dim=1)
                val_preds_all.extend(preds.cpu().numpy())
                val_trues_all.extend(y_b.cpu().numpy())
                
        val_loss /= len(val_trues_all)
        val_preds_all = np.array(val_preds_all)
        val_trues_all = np.array(val_trues_all)
        
        val_acc = np.mean(val_preds_all == val_trues_all)
        tp = np.sum((val_preds_all == 1) & (val_trues_all == 1))
        fp = np.sum((val_preds_all == 1) & (val_trues_all == 0))
        fn = np.sum((val_preds_all == 0) & (val_trues_all == 1))
        val_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        val_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        val_f1 = 2 * val_prec * val_rec / (val_prec + val_rec) if (val_prec + val_rec) > 0 else 0.0
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            torch.save({
                "epoch": int(epoch),
                "model_state_dict": model.state_dict(),
                "in_features": 95,
                "conv_dim": 64,
                "rnn_dim": 64,
                "num_classes": 2,
                "val_acc": float(val_acc),
                "val_f1": float(val_f1)
            }, best_model_path)
            
        if epoch % 5 == 0 or epoch == 35:
            print(f"Epoch {epoch:2d}/35 | Train Loss: {train_loss:.4f}, Acc: {train_acc*100:.1f}% | Val Loss: {val_loss:.4f}, Acc: {val_acc*100:.1f}%, F1: {val_f1*100:.1f}% {'*Best*' if epoch == best_epoch else ''}")

    print(f"\nTraining completed. Best model saved at epoch {best_epoch} with Val F1: {best_val_f1*100:.2f}%")
    
    # Evaluation on Completely Unseen Test Split
    print("\n" + "=" * 70)
    print("FINAL EVALUATION ON COMPLETELY UNSEEN TEST SPLIT (50 Videos)")
    print("=" * 70)
    
    checkpoint = torch.load(best_model_path, map_location=DEVICE, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    test_preds_all = []
    test_trues_all = []
    test_probs_all = []
    
    with torch.no_grad():
        for x_b, y_b in test_loader:
            x_b = x_b.to(DEVICE)
            logits = model(x_b)
            probs = F.softmax(logits, dim=1)[:, 1]
            preds = torch.argmax(logits, dim=1)
            test_probs_all.extend(probs.cpu().numpy())
            test_preds_all.extend(preds.cpu().numpy())
            test_trues_all.extend(y_b.numpy())
            
    test_preds = np.array(test_preds_all)
    test_trues = np.array(test_trues_all)
    test_probs = np.array(test_probs_all)
    
    acc = np.mean(test_preds == test_trues)
    tp = int(np.sum((test_preds == 1) & (test_trues == 1)))
    fp = int(np.sum((test_preds == 1) & (test_trues == 0)))
    fn = int(np.sum((test_preds == 0) & (test_trues == 1)))
    tn = int(np.sum((test_preds == 0) & (test_trues == 0)))
    
    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    print(f"Test Accuracy:    {acc*100:.2f}%")
    print(f"Precision:        {prec*100:.2f}%")
    print(f"Recall (Sens):    {rec*100:.2f}% (Sprinting detection rate)")
    print(f"Specificity:      {spec*100:.2f}% (Non-sprinting rejection rate)")
    print(f"F1-Score:         {f1*100:.2f}%")
    print("\nCONFUSION MATRIX:")
    print(f"               Predicted NOT SPRINTING  Predicted SPRINTING")
    print(f"True NOT SPRINTING:       {tn:3d} (TN)                 {fp:3d} (FP)")
    print(f"True SPRINTING:           {fn:3d} (FN)                 {tp:3d} (TP)")
    
    # Save Report
    report = {
        "model_architecture": "SprintTemporalNet (1D Conv + BiGRU + Temporal Attention + MLP)",
        "test_accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {"TN": tn, "FP": fp, "FN": fn, "TP": tp},
        "target_mapping": {"0": "NOT SPRINTING", "1": "SPRINTING"},
        "samples_evaluated": len(test_trues)
    }
    
    rep_path = os.path.join(SAVED_DIR, "sprint_evaluation_report.json")
    with open(rep_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved evaluation report to: {rep_path}")
    
    # Save Model Config
    config = {
        "in_features": 95,
        "conv_dim": 64,
        "rnn_dim": 64,
        "num_classes": 2,
        "labels": ["NOT SPRINTING", "SPRINTING"],
        "seq_len": 32
    }
    with open(os.path.join(SAVED_DIR, "sprint_config.json"), "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved model config to: {SAVED_DIR}")

if __name__ == "__main__":
    train_sprint_model()
