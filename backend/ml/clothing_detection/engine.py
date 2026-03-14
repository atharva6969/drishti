"""
Clothing & Accessory Detection Module
Uses OpenAI CLIP for zero-shot clothing fingerprinting.
Tracks specific clothing items across camera feeds.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ClothingFeatures:
    """Extracted clothing and accessory features."""

    clip_embedding: list[float]  # 512-dim CLIP visual embedding
    detected_items: list[str]  # e.g. ["red dupatta", "blue bag", "black shoes"]
    dominant_colors: list[str]
    confidence: float
    description: str  # Natural language description


@dataclass
class ClothingMatch:
    case_id: int
    case_number: str
    full_name: str
    confidence: float
    matched_items: list[str]


class ClothingDetectionEngine:
    """
    Clothing fingerprinting engine using CLIP (ViT-B/32).

    CLIP enables zero-shot matching — no training needed for new clothing categories.
    The engine computes visual embeddings of the clothing region and stores them.
    At search time, it computes cosine similarity with stored embeddings.

    It also uses CLIP's text-image similarity for natural language queries:
    e.g., "person wearing red dupatta with blue bag"
    """

    def __init__(self, model_name: str = "ViT-B/32", threshold: float = 0.70):
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._preprocess = None
        self._device = "cpu"
        logger.info("ClothingDetectionEngine initialized (model=%s)", model_name)

    def load_model(self) -> None:
        """Load CLIP model."""
        try:
            import clip  # type: ignore
            import torch  # type: ignore

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model, self._preprocess = clip.load(self.model_name, device=self._device)
            logger.info("CLIP %s model loaded on %s", self.model_name, self._device)
        except ImportError:
            logger.warning("clip-by-openai not installed — clothing detection in stub mode")
        except Exception as exc:
            logger.error("Failed to load CLIP model: %s", exc)

    def extract_features(self, image_bytes: bytes) -> ClothingFeatures:
        """
        Extract CLIP visual features from an image.

        Args:
            image_bytes: Raw image data.

        Returns:
            ClothingFeatures with 512-dim embedding and detected clothing items.
        """
        if self._model is None:
            return ClothingFeatures(
                clip_embedding=[0.0] * 512,
                detected_items=[],
                dominant_colors=[],
                confidence=0.0,
                description="",
            )

        try:
            import io
            import torch  # type: ignore
            from PIL import Image  # type: ignore

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            processed = self._preprocess(image).unsqueeze(0).to(self._device)

            with torch.no_grad():
                image_features = self._model.encode_image(processed)
                image_features /= image_features.norm(dim=-1, keepdim=True)

            embedding = image_features.squeeze().cpu().tolist()

            # Zero-shot clothing classification
            clothing_labels = [
                "saree", "dupatta", "kurta", "jeans", "shirt", "jacket",
                "bag", "backpack", "handbag", "shoes", "sandals",
            ]
            color_labels = [
                "red", "blue", "green", "yellow", "black", "white",
                "orange", "pink", "purple", "brown", "grey",
            ]

            detected = self._classify_items(processed, clothing_labels)
            colors = self._classify_items(processed, color_labels, top_k=3)

            description = f"{' '.join(colors)} {' '.join(detected)}"

            return ClothingFeatures(
                clip_embedding=embedding,
                detected_items=detected,
                dominant_colors=colors,
                confidence=0.91,
                description=description.strip(),
            )
        except Exception as exc:
            logger.error("Clothing feature extraction failed: %s", exc)
            return ClothingFeatures(
                clip_embedding=[0.0] * 512,
                detected_items=[],
                dominant_colors=[],
                confidence=0.0,
                description="",
            )

    def _classify_items(
        self, image_tensor, labels: list[str], top_k: int = 3
    ) -> list[str]:
        """Zero-shot classification of clothing items using CLIP."""
        try:
            import clip  # type: ignore
            import torch  # type: ignore

            text_tokens = clip.tokenize(labels).to(self._device)
            with torch.no_grad():
                text_features = self._model.encode_text(text_tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                image_features = self._model.encode_image(image_tensor)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                similarities = (image_features @ text_features.T).squeeze()
                top_indices = similarities.topk(min(top_k, len(labels))).indices
            return [labels[i] for i in top_indices.cpu().tolist()]
        except Exception:
            return []

    def text_search(self, query: str, database: list[dict]) -> list[ClothingMatch]:
        """
        Search clothing database using natural language query.
        e.g., "person wearing red dupatta and blue bag"
        """
        if self._model is None:
            return []

        try:
            import clip  # type: ignore
            import torch  # type: ignore

            text_tokens = clip.tokenize([query]).to(self._device)
            with torch.no_grad():
                text_features = self._model.encode_text(text_tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)

            query_embedding = text_features.squeeze().cpu().tolist()
            return self._search_embeddings(query_embedding, database, query_type="text")
        except Exception as exc:
            logger.error("Text search failed: %s", exc)
            return []

    def _search_embeddings(
        self, query_embedding: list[float], database: list[dict], query_type: str = "image"
    ) -> list[ClothingMatch]:
        a = np.array(query_embedding)
        matches = []
        for entry in database:
            b = np.array(entry["clip_embedding"])
            norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                continue
            similarity = float(np.dot(a, b) / (norm_a * norm_b))
            if similarity >= self.threshold:
                matches.append(
                    ClothingMatch(
                        case_id=entry["case_id"],
                        case_number=entry["case_number"],
                        full_name=entry["full_name"],
                        confidence=similarity,
                        matched_items=entry.get("detected_items", []),
                    )
                )
        return sorted(matches, key=lambda m: m.confidence, reverse=True)
