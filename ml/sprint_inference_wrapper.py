"""
Standalone Inference Wrapper for Sprinting Activity Recognition
Model: SprintTemporalNet
Returns:
- classification: "SPRINTING" or "NOT SPRINTING"
- confidence: float (0.0 to 1.0)
- sprint_probability: float (0.0 to 1.0)
"""

import os
import sys
import json
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_models", "sprint_model", "best_sprint_model.pt")
CONFIG_PATH = os.path.join(BASE_DIR, "ml", "saved_models", "sprint_model", "sprint_config.json")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Import or define SprintTemporalNet
class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, rnn_out):
        scores = self.attn(torch.tanh(rnn_out))
        weights = F.softmax(scores, dim=1)
        context = torch.sum(rnn_out * weights, dim=1)
        return context, weights

class SprintTemporalNet(nn.Module):
    def __init__(self, in_features=95, conv_dim=64, rnn_dim=64, num_classes=2, dropout=0.3):
        super().__init__()
        self.conv1 = nn.Conv1d(in_features, conv_dim, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(conv_dim)
        self.relu = nn.ReLU()
        self.gru = nn.GRU(
            input_size=conv_dim,
            hidden_size=rnn_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if dropout > 0 else 0
        )
        self.attention = TemporalAttention(rnn_dim * 2)
        self.head = nn.Sequential(
            nn.Linear(rnn_dim * 2, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        x_conv = x.transpose(1, 2)
        h = self.relu(self.bn1(self.conv1(x_conv)))
        h = h.transpose(1, 2)
        gru_out, _ = self.gru(h)
        context, _ = self.attention(gru_out)
        logits = self.head(context)
        return logits

class SprintClassifier:
    def __init__(self, model_path=MODEL_PATH):
        self.device = DEVICE
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Sprint model checkpoint not found at: {model_path}")
            
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        self.model = SprintTemporalNet(
            in_features=checkpoint.get("in_features", 95),
            conv_dim=checkpoint.get("conv_dim", 64),
            rnn_dim=checkpoint.get("rnn_dim", 64),
            num_classes=2,
            dropout=0.0
        ).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        self._pose_model = None

    def _get_pose_model(self):
        if self._pose_model is None:
            self._pose_model = YOLO("yolov8n-pose.pt")
        return self._pose_model

    def predict_from_keypoint_sequence(self, keypoints_list):
        """
        Predicts from a list of per-frame (17, 3) keypoint arrays.
        """
        if not keypoints_list or len(keypoints_list) < 8:
            return {
                "classification": "NOT SPRINTING",
                "is_sprinting": False,
                "confidence": 0.50,
                "sprint_probability": 0.0,
                "evidence": "Insufficient tracked keypoint frames (<8 frames)."
            }
            
        n_frames = 32
        indices = np.linspace(0, len(keypoints_list) - 1, n_frames, dtype=int)
        sampled_kpts = [keypoints_list[i] for i in indices]
        
        feature_seq = np.zeros((n_frames, 95), dtype=np.float32)
        prev_kpts = None
        stride_spreads = []
        
        for i, kpts in enumerate(sampled_kpts):
            kpts = np.asarray(kpts, dtype=np.float32)
            coords = kpts[:, :2].copy()
            confs = kpts[:, 2].copy() if kpts.shape[1] > 2 else np.ones(17, dtype=np.float32)
            
            mid_shoulder = (coords[5] + coords[6]) / 2.0
            mid_hip = (coords[11] + coords[12]) / 2.0
            torso_len = np.linalg.norm(mid_shoulder - mid_hip)
            if torso_len < 10.0:
                torso_len = 100.0
                
            norm_coords = (coords - mid_hip) / torso_len
            
            if prev_kpts is not None:
                vels = norm_coords - prev_kpts
            else:
                vels = np.zeros_like(norm_coords)
            prev_kpts = norm_coords.copy()
            
            stride_spread = abs(norm_coords[16, 0] - norm_coords[15, 0])
            stride_spreads.append(stride_spread)
            vert_ankle = abs(norm_coords[16, 1] - norm_coords[15, 1])
            pelvis_disp = float(np.linalg.norm(vels[11:13]))
            
            # Simple angles
            def ang(a, b, c):
                ba, bc = a - b, c - b
                nba, nbc = np.linalg.norm(ba), np.linalg.norm(bc)
                if nba < 1e-4 or nbc < 1e-4: return 0.0
                return float(np.degrees(np.arccos(np.clip(np.dot(ba, bc)/(nba*nbc), -1.0, 1.0)))) / 180.0
                
            k_l = ang(coords[11], coords[13], coords[15])
            k_r = ang(coords[12], coords[14], coords[16])
            h_l = ang(coords[5], coords[11], coords[13])
            h_r = ang(coords[6], coords[12], coords[14])
            e_l = ang(coords[5], coords[7], coords[9])
            e_r = ang(coords[6], coords[8], coords[10])
            
            t_vec = mid_shoulder - mid_hip
            t_incline = float(np.arctan2(abs(t_vec[0]), abs(t_vec[1]) + 1e-4) / (np.pi / 2.0))
            
            f_vec = np.concatenate([
                norm_coords.flatten(), confs, vels.flatten(),
                [k_l, k_r, h_l, h_r, e_l, e_r, t_incline],
                [stride_spread, vert_ankle, pelvis_disp]
            ]).astype(np.float32)
            feature_seq[i] = f_vec
            
        tensor_in = torch.tensor(feature_seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.model(tensor_in)
            probs = F.softmax(logits, dim=1)[0].cpu().numpy()
            
        p_not_sprint = float(probs[0])
        p_sprint = float(probs[1])
        
        is_sprint = bool(p_sprint >= 0.50)
        classification = "SPRINTING" if is_sprint else "NOT SPRINTING"
        confidence = float(max(p_sprint, p_not_sprint))
        
        mean_stride = float(np.mean(stride_spreads)) if stride_spreads else 0.0
        
        return {
            "classification": classification,
            "is_sprinting": is_sprint,
            "confidence": round(confidence, 4),
            "sprint_probability": round(p_sprint, 4),
            "mean_normalized_stride": round(mean_stride, 3),
            "evidence": f"Temporal stride dynamics & leg frequency model output: {classification} (p={p_sprint*100:.1f}%)"
        }

