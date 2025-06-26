
"""Posture analysis utilities."""
import math
from typing import Dict, Tuple
from .config import ANGLE_THRESHOLD_DEG

def _angle_between(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    """Return angle in degrees between two 3‑D vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 * mag2 == 0:
        return 0.0
    # Clamp value to valid acos range
    return math.degrees(math.acos(max(-1.0, min(1.0, dot / (mag1 * mag2)))))

def is_slouch(landmarks: Dict[int, Tuple[float, float, float]]) -> tuple[bool, float]:
    """Return (is_slouch, angle). Uses shoulders & hips to approximate back angle."""
    # Required landmark IDs
    left_shoulder, right_shoulder = landmarks[11], landmarks[12]
    left_hip, right_hip = landmarks[23], landmarks[24]

    shoulder_mid = tuple((l + r) / 2 for l, r in zip(left_shoulder, right_shoulder))
    hip_mid = tuple((l + r) / 2 for l, r in zip(left_hip, right_hip))

    # Simple neck vector (vertical)
    neck_vec = (0.0, left_shoulder[1] - shoulder_mid[1], 0.0)
    back_vec = tuple(h - s for h, s in zip(hip_mid, shoulder_mid))

    angle = _angle_between(neck_vec, back_vec)
    return angle > ANGLE_THRESHOLD_DEG, angle
