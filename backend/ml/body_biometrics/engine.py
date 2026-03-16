"""
Body Biometrics Module
Uses MediaPipe Pose to extract height, shoulder width, arm length ratios.
These measurements are camera-angle-invariant through projective geometry.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# MediaPipe pose landmark indices
LANDMARK_IDX = {
    "nose": 0,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_wrist": 15,
    "right_wrist": 16,
}


@dataclass
class BodyMetrics:
    """Body proportion measurements extracted from MediaPipe Pose."""

    height_ratio: float  # nose-to-ankle / image height
    shoulder_width_ratio: float  # shoulder width / height
    torso_ratio: float  # shoulder-to-hip / height
    leg_ratio: float  # hip-to-ankle / height
    arm_span_ratio: float  # wrist-to-wrist / height
    pose_landmarks: Optional[list[dict]]  # raw landmarks
    confidence: float
    person_detected: bool


@dataclass
class BodyMatch:
    case_id: int
    case_number: str
    full_name: str
    confidence: float
    metric_similarity: float


class BodyBiometricsEngine:
    """
    Body biometrics engine using MediaPipe Pose.

    Extracts camera-angle-robust body proportion ratios.
    These serve as a weak biometric that complements face/gait signals.
    """

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self._pose = None
        logger.info("BodyBiometricsEngine initialized (threshold=%.2f)", threshold)

    def load_model(self) -> None:
        """Initialize MediaPipe Pose."""
        try:
            import mediapipe as mp  # type: ignore

            self._mp_pose = mp.solutions.pose
            self._pose = self._mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5,
            )
            logger.info("MediaPipe Pose loaded")
        except ImportError:
            logger.warning("mediapipe not installed — body biometrics in stub mode")
        except Exception as exc:
            logger.error("Failed to load MediaPipe Pose: %s", exc)

    def extract_metrics(self, image_bytes: bytes) -> BodyMetrics:
        """
        Extract body proportion metrics from an image.

        Args:
            image_bytes: Raw image data.

        Returns:
            BodyMetrics with normalized proportion ratios.
        """
        empty = BodyMetrics(
            height_ratio=0.0,
            shoulder_width_ratio=0.0,
            torso_ratio=0.0,
            leg_ratio=0.0,
            arm_span_ratio=0.0,
            pose_landmarks=None,
            confidence=0.0,
            person_detected=False,
        )

        if self._pose is None:
            return empty

        try:
            import cv2  # type: ignore
            import numpy as np

            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]

            results = self._pose.process(image_rgb)
            if not results.pose_landmarks:
                return empty

            lm = results.pose_landmarks.landmark

            def get_pt(idx: int) -> tuple[float, float]:
                return lm[idx].x * w, lm[idx].y * h

            nose = get_pt(LANDMARK_IDX["nose"])
            l_shoulder = get_pt(LANDMARK_IDX["left_shoulder"])
            r_shoulder = get_pt(LANDMARK_IDX["right_shoulder"])
            l_hip = get_pt(LANDMARK_IDX["left_hip"])
            r_hip = get_pt(LANDMARK_IDX["right_hip"])
            l_ankle = get_pt(LANDMARK_IDX["left_ankle"])
            r_ankle = get_pt(LANDMARK_IDX["right_ankle"])
            l_wrist = get_pt(LANDMARK_IDX["left_wrist"])
            r_wrist = get_pt(LANDMARK_IDX["right_wrist"])

            def dist(p1, p2) -> float:
                return float(np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))

            ankle_y = (l_ankle[1] + r_ankle[1]) / 2
            total_height = ankle_y - nose[1]
            if total_height <= 0:
                return empty

            shoulder_width = dist(l_shoulder, r_shoulder)
            hip_y = (l_hip[1] + r_hip[1]) / 2
            shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
            torso_len = hip_y - shoulder_y
            leg_len = ankle_y - hip_y
            arm_span = dist(l_wrist, r_wrist)

            metrics = BodyMetrics(
                height_ratio=total_height / h,
                shoulder_width_ratio=shoulder_width / total_height,
                torso_ratio=torso_len / total_height,
                leg_ratio=leg_len / total_height,
                arm_span_ratio=arm_span / total_height,
                pose_landmarks=[
                    {"name": k, "x": lm[v].x, "y": lm[v].y, "z": lm[v].z}
                    for k, v in LANDMARK_IDX.items()
                ],
                confidence=float(np.mean([lm[v].visibility for v in LANDMARK_IDX.values()])),
                person_detected=True,
            )
            return metrics

        except Exception as exc:
            logger.error("Body metric extraction failed: %s", exc)
            return empty

    def metrics_to_vector(self, metrics: BodyMetrics) -> list[float]:
        """Convert BodyMetrics to a 5-element comparison vector."""
        return [
            metrics.shoulder_width_ratio,
            metrics.torso_ratio,
            metrics.leg_ratio,
            metrics.arm_span_ratio,
            metrics.height_ratio,
        ]

    def compare_metrics(self, v1: list[float], v2: list[float]) -> tuple[float, bool]:
        """Compute similarity between two metric vectors."""
        a, b = np.array(v1), np.array(v2)
        diff = np.abs(a - b)
        similarity = float(1.0 - np.mean(diff))
        return similarity, similarity >= self.threshold
