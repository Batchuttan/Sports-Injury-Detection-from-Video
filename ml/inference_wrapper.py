"""
Inference Wrapper for Trained Sports Action Recognition Model
Provides standalone prediction functions for video files and pre-extracted kinematics.
"""

import os
import sys
from typing import Optional, Dict, Any, List
import torch
import numpy as np

# Ensure workspace root and ml directory are in sys.path
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

SAVED_MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")
BEST_MODEL_PATH = os.path.join(SAVED_MODELS_DIR, "best_sports_action_model.pt")

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

_cached_model: Optional[SportsActionSTNet] = None

def get_action_model() -> Optional[SportsActionSTNet]:
    global _cached_model
    if _cached_model is None:
        if not os.path.exists(BEST_MODEL_PATH):
            return None
        try:
            checkpoint = torch.load(BEST_MODEL_PATH, map_location=DEVICE)
            in_features = int(checkpoint.get("in_features", 95))
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
            _cached_model = model
        except Exception as e:
            print(f"Error loading trained action model: {e}")
            _cached_model = None
    return _cached_model

def predict_from_feature_sequence(seq_features: np.ndarray) -> Optional[Dict[str, Any]]:
    """
    Inference given a (T, 95) or (1, T, 95) kinematic feature sequence.
    Returns primary action, confidence, and complete 7-class probability breakdown.
    """
    model = get_action_model()
    if model is None:
        return None

    feat_input = np.asarray(seq_features, dtype=np.float32)
    if len(feat_input.shape) == 2:
        feat_input = np.expand_dims(feat_input, axis=0)  # (1, T, 95)

    x = torch.from_numpy(feat_input).float().to(DEVICE)
    with torch.no_grad():
        logits, _ = model(x)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    best_idx = int(np.argmax(probs))
    best_action = CLASSES[best_idx]
    best_conf = float(probs[best_idx])

    # Build per-action breakdown
    breakdown: List[Dict[str, Any]] = []
    performed_list: List[str] = []
    
    for idx, name in enumerate(CLASSES):
        prob = float(probs[idx])
        conf_pct = round(prob * 100.0, 1)
        performed = bool(prob >= 0.40 or idx == best_idx)
        if performed:
            performed_list.append(name)
        breakdown.append({
            "action": name,
            "performed": performed,
            "confidence": conf_pct,
            "probability": prob,
            "status": "Performed" if performed else "Not Detected"
        })

    return {
        "primary_action": best_action,
        "confidence": round(best_conf * 100.0, 1),
        "probabilities": {name: round(float(probs[i]), 4) for i, name in enumerate(CLASSES)},
        "performed_actions": performed_list,
        "breakdown": breakdown
    }

def _calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

def predict_from_keypoints(keypoints_list: List[np.ndarray], target_h: float = 720.0, fps: float = 30.0) -> Optional[Dict[str, Any]]:
    """
    Direct prediction from a list of per-frame (17, 3) keypoint arrays.
    Interpolates to 32 frames and computes the exact 95-dim kinematic features.
    """
    if not keypoints_list or len(keypoints_list) < 6:
        return None

    n_frames = 32
    indices = np.linspace(0, len(keypoints_list) - 1, n_frames, dtype=int)
    sampled_kpts = [keypoints_list[i] for i in indices]
    
    dt = 1.0 / max(1.0, float(fps))
    norm_scale = max(10.0, float(target_h))
    
    features = []
    prev_kpts = None
    
    for kpts in sampled_kpts:
        kpts = np.asarray(kpts, dtype=np.float32)
        if kpts.shape != (17, 3):
            kpts = np.zeros((17, 3), dtype=np.float32)
            
        xy_norm = kpts[:, :2] / norm_scale
        conf = kpts[:, 2:3]
        
        if prev_kpts is not None:
            vel = (xy_norm - (prev_kpts[:, :2] / norm_scale)) / dt
        else:
            vel = np.zeros_like(xy_norm)
        prev_kpts = kpts
        
        ang_lk = _calculate_angle(kpts[11][:2], kpts[13][:2], kpts[15][:2]) / 180.0
        ang_rk = _calculate_angle(kpts[12][:2], kpts[14][:2], kpts[16][:2]) / 180.0
        ang_lh = _calculate_angle(kpts[5][:2], kpts[11][:2], kpts[13][:2]) / 180.0
        ang_rh = _calculate_angle(kpts[6][:2], kpts[12][:2], kpts[14][:2]) / 180.0
        ang_le = _calculate_angle(kpts[5][:2], kpts[7][:2], kpts[9][:2]) / 180.0
        ang_re = _calculate_angle(kpts[6][:2], kpts[8][:2], kpts[10][:2]) / 180.0
        
        mid_sh = (kpts[5][:2] + kpts[6][:2]) / 2.0
        mid_hp = (kpts[11][:2] + kpts[12][:2]) / 2.0
        trunk_lean = abs(float(np.degrees(np.arctan2(abs(mid_sh[0] - mid_hp[0]), max(1e-4, abs(mid_hp[1] - mid_sh[1])))))) / 90.0
        
        ank_h_l = (norm_scale - kpts[15][1]) / norm_scale
        ank_h_r = (norm_scale - kpts[16][1]) / norm_scale
        flight_clearance = min(max(0.0, ank_h_l), max(0.0, ank_h_r))
        gait_spread = abs(kpts[15][0] - kpts[16][0]) / norm_scale
        hip_vert_v = float(vel[11, 1] + vel[12, 1]) / 2.0
        
        angles = np.array([ang_lk, ang_rk, ang_lh, ang_rh, ang_le, ang_re, trunk_lean], dtype=np.float32)
        kinetics = np.array([flight_clearance, gait_spread, hip_vert_v], dtype=np.float32)
        
        frame_feat = np.concatenate([xy_norm.flatten(), conf.flatten(), vel.flatten(), angles, kinetics])
        features.append(frame_feat)
        
    feat_matrix = np.array(features, dtype=np.float32)
    return predict_from_feature_sequence(feat_matrix)
