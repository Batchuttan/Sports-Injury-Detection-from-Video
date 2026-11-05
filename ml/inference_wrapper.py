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
