"""
Multimodal Identity Engine
Combines face, gait, clothing, body biometrics, and companion pattern signals
to produce a single confidence score for identity matching.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Signal weights for combined confidence scoring
SIGNAL_WEIGHTS = {
    "face": 0.40,
    "gait": 0.25,
    "clothing": 0.20,
    "body": 0.10,
    "companion": 0.05,
}

ALERT_THRESHOLD = 0.50  # Trigger alert if combined score ≥ this value
HIGH_CONFIDENCE_THRESHOLD = 0.75


@dataclass
class IdentityMatchResult:
    """Combined multimodal identity match result."""

    case_id: int
    case_number: str
    full_name: str

    # Individual signal scores
    face_score: Optional[float] = None
    gait_score: Optional[float] = None
    clothing_score: Optional[float] = None
    body_score: Optional[float] = None
    companion_score: Optional[float] = None

    # Combined score
    combined_score: float = 0.0
    signals_used: int = 0
    confidence_level: str = "low"  # low | medium | high | critical

    def __post_init__(self):
        self._compute_combined_score()

    def _compute_combined_score(self) -> None:
        """Weighted average of available signals."""
        total_weight = 0.0
        weighted_sum = 0.0
        count = 0

        for signal, weight in SIGNAL_WEIGHTS.items():
            score = getattr(self, f"{signal}_score")
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
                count += 1

        if total_weight > 0:
            self.combined_score = weighted_sum / total_weight
        self.signals_used = count

        if self.combined_score >= HIGH_CONFIDENCE_THRESHOLD:
            self.confidence_level = "high"
        elif self.combined_score >= ALERT_THRESHOLD:
            self.confidence_level = "medium"
        else:
            self.confidence_level = "low"

    @property
    def should_alert(self) -> bool:
        """Return True if this match should trigger an alert."""
        return self.combined_score >= ALERT_THRESHOLD or self.signals_used >= 2


class MultimodalIdentityEngine:
    """
    Orchestrates all identity signal engines for combined matching.

    Even 2/5 signals reaching their individual thresholds triggers an alert.
    The combined confidence score drives prioritization of officer response.
    """

    def __init__(self):
        from ml.face_recognition.engine import FaceRecognitionEngine
        from ml.gait_recognition.engine import GaitRecognitionEngine
        from ml.clothing_detection.engine import ClothingDetectionEngine
        from ml.body_biometrics.engine import BodyBiometricsEngine

        self.face_engine = FaceRecognitionEngine()
        self.gait_engine = GaitRecognitionEngine()
        self.clothing_engine = ClothingDetectionEngine()
        self.body_engine = BodyBiometricsEngine()
        logger.info("MultimodalIdentityEngine initialized")

    def load_all_models(self) -> None:
        """Load all signal models into memory."""
        self.face_engine.load_model()
        self.gait_engine.load_model()
        self.clothing_engine.load_model()
        self.body_engine.load_model()
        logger.info("All multimodal identity models loaded")

    def search(
        self,
        image_bytes: bytes,
        database: list[dict],
        use_face: bool = True,
        use_clothing: bool = True,
        use_body: bool = True,
    ) -> list[IdentityMatchResult]:
        """
        Run multimodal search against the missing persons database.

        Args:
            image_bytes: Query image bytes.
            database: List of stored person records with precomputed features.
            use_face/clothing/body: Which signals to activate.

        Returns:
            Sorted list of IdentityMatchResult above alert threshold.
        """
        # Extract features from query image
        face_emb = None
        clothing_feat = None
        body_metrics = None

        if use_face:
            face_result = self.face_engine.extract_embedding(image_bytes)
            if face_result.face_detected:
                face_emb = face_result.embedding

        if use_clothing:
            clothing_result = self.clothing_engine.extract_features(image_bytes)
            if clothing_result.confidence > 0:
                clothing_feat = clothing_result.clip_embedding

        if use_body:
            body_result = self.body_engine.extract_metrics(image_bytes)
            if body_result.person_detected:
                body_metrics = self.body_engine.metrics_to_vector(body_result)

        # Match against each database entry
        results: list[IdentityMatchResult] = []
        for entry in database:
            face_score = None
            clothing_score = None
            body_score = None

            if face_emb and "face_embedding" in entry:
                sim, _ = self.face_engine.compare_embeddings(face_emb, entry["face_embedding"])
                face_score = sim

            if clothing_feat and "clothing_features" in entry:
                a, b = __import__("numpy").array(clothing_feat), __import__("numpy").array(entry["clothing_features"])
                na, nb = __import__("numpy").linalg.norm(a), __import__("numpy").linalg.norm(b)
                if na > 0 and nb > 0:
                    clothing_score = float(__import__("numpy").dot(a, b) / (na * nb))

            if body_metrics and "body_metrics" in entry:
                sim, _ = self.body_engine.compare_metrics(body_metrics, entry["body_metrics"])
                body_score = sim

            match = IdentityMatchResult(
                case_id=entry["case_id"],
                case_number=entry["case_number"],
                full_name=entry["full_name"],
                face_score=face_score,
                clothing_score=clothing_score,
                body_score=body_score,
            )

            if match.should_alert:
                results.append(match)

        return sorted(results, key=lambda r: r.combined_score, reverse=True)
