"""
Face Recognition Engine
Uses DeepFace as the primary face analysis framework with ArcFace model.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FaceMatch:
    """Result of a face matching operation."""

    case_id: int
    case_number: str
    full_name: str
    confidence: float
    distance: float
    model: str = "ArcFace"


@dataclass
class FaceEmbedding:
    """Extracted face embedding vector."""

    embedding: list[float]
    face_detected: bool
    confidence: float
    model: str = "ArcFace"
    bounding_box: Optional[dict] = None


class FaceRecognitionEngine:
    """
    Face recognition engine using DeepFace + ArcFace.

    In production, this class loads the ArcFace model and performs:
    1. Face detection (MTCNN or RetinaFace)
    2. Face alignment
    3. Embedding extraction (512-dim ArcFace vector)
    4. Cosine similarity search against stored embeddings

    Note: Requires deepface>=0.0.80 and tensorflow>=2.12
    """

    def __init__(
        self,
        model_name: str = "ArcFace",
        detector_backend: str = "retinaface",
        threshold: float = 0.6,
        enforce_detection: bool = False,
    ):
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.threshold = threshold
        self.enforce_detection = enforce_detection
        self._model_loaded = False
        logger.info(
            "FaceRecognitionEngine initialized (model=%s, detector=%s)",
            model_name,
            detector_backend,
        )

    def load_model(self) -> None:
        """Load DeepFace model into memory. Call once at startup."""
        try:
            # Lazy import to avoid loading tensorflow unless needed
            from deepface import DeepFace  # type: ignore

            DeepFace.build_model(self.model_name)
            self._model_loaded = True
            logger.info("DeepFace %s model loaded", self.model_name)
        except ImportError:
            logger.warning(
                "deepface not installed — face recognition running in stub mode"
            )
        except Exception as exc:
            logger.error("Failed to load face model: %s", exc)

    def extract_embedding(self, image_bytes: bytes) -> FaceEmbedding:
        """
        Extract face embedding from raw image bytes.

        Args:
            image_bytes: Raw image data (JPEG/PNG).

        Returns:
            FaceEmbedding with 512-dimensional ArcFace vector.
        """
        if not self._model_loaded:
            logger.warning("Model not loaded — returning stub embedding")
            return FaceEmbedding(
                embedding=[0.0] * 512,
                face_detected=False,
                confidence=0.0,
            )

        try:
            import cv2  # type: ignore
            from deepface import DeepFace  # type: ignore

            # Decode bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result = DeepFace.represent(
                img_path=img,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
            )

            if result:
                emb = result[0]["embedding"]
                region = result[0].get("facial_area", {})
                return FaceEmbedding(
                    embedding=emb,
                    face_detected=True,
                    confidence=result[0].get("face_confidence", 1.0),
                    bounding_box=region,
                )
        except Exception as exc:
            logger.error("Embedding extraction failed: %s", exc)

        return FaceEmbedding(embedding=[0.0] * 512, face_detected=False, confidence=0.0)

    def compare_embeddings(
        self, emb1: list[float], emb2: list[float]
    ) -> tuple[float, bool]:
        """
        Compute cosine similarity between two embeddings.

        Returns:
            (similarity_score, is_match) where similarity ∈ [0, 1]
        """
        a = np.array(emb1)
        b = np.array(emb2)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0, False
        similarity = float(np.dot(a, b) / (norm_a * norm_b))
        return similarity, similarity >= self.threshold

    def search_database(
        self, query_embedding: list[float], database: list[dict]
    ) -> list[FaceMatch]:
        """
        Search a list of stored embeddings for matches.

        Args:
            query_embedding: 512-dim ArcFace embedding of query face.
            database: List of dicts with keys: case_id, case_number, full_name, embedding.

        Returns:
            Sorted list of FaceMatch objects above threshold.
        """
        matches: list[FaceMatch] = []
        for entry in database:
            similarity, is_match = self.compare_embeddings(
                query_embedding, entry["embedding"]
            )
            if is_match:
                matches.append(
                    FaceMatch(
                        case_id=entry["case_id"],
                        case_number=entry["case_number"],
                        full_name=entry["full_name"],
                        confidence=similarity,
                        distance=1.0 - similarity,
                    )
                )
        return sorted(matches, key=lambda m: m.confidence, reverse=True)


# Module-level singleton
_engine: Optional[FaceRecognitionEngine] = None


def get_face_engine() -> FaceRecognitionEngine:
    """Get or create the module-level face recognition engine."""
    global _engine
    if _engine is None:
        _engine = FaceRecognitionEngine()
    return _engine
