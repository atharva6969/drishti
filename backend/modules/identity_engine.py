"""Module 1 — Multimodal Identity Engine.

Combines 5 parallel identity signals to produce a unified confidence
score for a potential match, even when individual signals (e.g. face)
are unavailable.

Signals
-------
1. Face Recognition   (DeepFace / ArcFace)
2. Gait Recognition   (OpenGait)
3. Clothing / Accessories (CLIP)
4. Height + Body Proportions (MediaPipe Pose)
5. Companion Pattern Analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from backend.config import settings


@dataclass
class SignalResult:
    """Result from a single identity signal."""

    signal_name: str
    confidence: float  # 0.0 – 1.0
    available: bool = True
    details: str = ""


@dataclass
class IdentityMatch:
    """Aggregated identity match across all available signals."""

    person_id: str
    signals: list[SignalResult] = field(default_factory=list)
    combined_confidence: float = 0.0
    is_alert_worthy: bool = False

    @property
    def matched_signal_names(self) -> list[str]:
        return [s.signal_name for s in self.signals if s.available and s.confidence > 0]


# ── Individual Signal Processors ─────────────────────────────────────


def compute_face_confidence(
    probe_image: Optional[bytes],
    gallery_image: Optional[bytes],
) -> SignalResult:
    """Compare two face images and return a confidence score.

    In production this delegates to DeepFace/ArcFace; here we provide
    the callable interface and a stub confidence.
    """
    if probe_image is None or gallery_image is None:
        return SignalResult("face", 0.0, available=False, details="image unavailable")
    # Placeholder – real implementation wraps deepface.verify()
    return SignalResult("face", 0.0, available=True, details="awaiting model integration")


def compute_gait_confidence(
    probe_sequence: Optional[list],
    gallery_sequence: Optional[list],
) -> SignalResult:
    """Compare gait sequences (silhouette frame lists).

    Uses OpenGait model in production.  94 % accuracy at 10 m distance.
    """
    if not probe_sequence or not gallery_sequence:
        return SignalResult("gait", 0.0, available=False, details="sequence unavailable")
    return SignalResult("gait", 0.0, available=True, details="awaiting model integration")


def compute_clothing_confidence(
    probe_description: Optional[str],
    gallery_description: Optional[str],
) -> SignalResult:
    """Match clothing / accessory descriptions via CLIP embeddings."""
    if not probe_description or not gallery_description:
        return SignalResult("clothing", 0.0, available=False, details="description unavailable")
    return SignalResult("clothing", 0.0, available=True, details="awaiting model integration")


def compute_body_biometric_confidence(
    probe_landmarks: Optional[dict],
    gallery_landmarks: Optional[dict],
) -> SignalResult:
    """Compare body proportions (shoulder width, arm ratio, height)."""
    if not probe_landmarks or not gallery_landmarks:
        return SignalResult("body_biometrics", 0.0, available=False, details="landmarks unavailable")
    return SignalResult("body_biometrics", 0.0, available=True, details="awaiting model integration")


def compute_companion_confidence(
    probe_group_ids: Optional[list[str]],
    gallery_group_ids: Optional[list[str]],
) -> SignalResult:
    """Detect if the same companion cluster appears across sightings."""
    if not probe_group_ids or not gallery_group_ids:
        return SignalResult("companion", 0.0, available=False, details="group data unavailable")
    overlap = set(probe_group_ids) & set(gallery_group_ids)
    if not overlap:
        return SignalResult("companion", 0.0, available=True, details="no overlap")
    confidence = len(overlap) / max(len(probe_group_ids), len(gallery_group_ids))
    return SignalResult(
        "companion",
        round(confidence, 4),
        available=True,
        details=f"overlapping ids: {overlap}",
    )


# ── Aggregation ──────────────────────────────────────────────────────


# Weight per signal – face is weighted highest when available.
_SIGNAL_WEIGHTS: dict[str, float] = {
    "face": 0.35,
    "gait": 0.25,
    "clothing": 0.15,
    "body_biometrics": 0.15,
    "companion": 0.10,
}


def combine_signals(signals: list[SignalResult]) -> tuple[float, bool]:
    """Compute a weighted combined confidence from available signals.

    Returns (combined_confidence, is_alert_worthy).
    An alert is triggered when:
      • combined confidence >= COMBINED_MATCH_THRESHOLD **and**
      • at least MIN_SIGNALS_FOR_ALERT signals contributed.
    """
    available = [s for s in signals if s.available and s.confidence > 0]
    if not available:
        return 0.0, False

    total_weight = sum(_SIGNAL_WEIGHTS.get(s.signal_name, 0.1) for s in available)
    if total_weight == 0:
        return 0.0, False

    weighted_sum = sum(
        s.confidence * _SIGNAL_WEIGHTS.get(s.signal_name, 0.1) for s in available
    )
    combined = round(weighted_sum / total_weight, 4)

    alert_worthy = (
        combined >= settings.COMBINED_MATCH_THRESHOLD
        and len(available) >= settings.MIN_SIGNALS_FOR_ALERT
    )
    return combined, alert_worthy


def identify(
    person_id: str,
    *,
    probe_face: Optional[bytes] = None,
    gallery_face: Optional[bytes] = None,
    probe_gait: Optional[list] = None,
    gallery_gait: Optional[list] = None,
    probe_clothing: Optional[str] = None,
    gallery_clothing: Optional[str] = None,
    probe_landmarks: Optional[dict] = None,
    gallery_landmarks: Optional[dict] = None,
    probe_companions: Optional[list[str]] = None,
    gallery_companions: Optional[list[str]] = None,
) -> IdentityMatch:
    """Run all five identity signals and aggregate the result."""
    signals = [
        compute_face_confidence(probe_face, gallery_face),
        compute_gait_confidence(probe_gait, gallery_gait),
        compute_clothing_confidence(probe_clothing, gallery_clothing),
        compute_body_biometric_confidence(probe_landmarks, gallery_landmarks),
        compute_companion_confidence(probe_companions, gallery_companions),
    ]
    combined, alert_worthy = combine_signals(signals)
    return IdentityMatch(
        person_id=person_id,
        signals=signals,
        combined_confidence=combined,
        is_alert_worthy=alert_worthy,
    )
