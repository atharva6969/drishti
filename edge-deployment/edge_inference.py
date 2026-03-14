"""
DRISHTI Edge Inference Module

Runs face recognition and person detection on CCTV hardware using
TensorFlow Lite — enabling deployment without cloud connectivity.
"""
from __future__ import annotations

import io
import json
import logging
import os
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

MODEL_DIR = Path(os.getenv("TFLITE_MODEL_DIR", Path(__file__).parent / "tflite_models"))
CENTRAL_API = os.getenv("DRISHTI_API_URL", "http://central-api:8000/api/v1")
EDGE_API_KEY = os.getenv("EDGE_API_KEY", "")


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DetectedFace:
    bbox: tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    embedding: list[float] = field(default_factory=list)
    landmark_points: Optional[list] = None


@dataclass
class EdgeMatchResult:
    detected: bool
    match_found: bool
    case_number: Optional[str]
    confidence: float
    camera_id: str
    timestamp: float
    frame_id: int


# ─────────────────────────────────────────────────────────────────────────────
# TFLite Interpreter wrapper
# ─────────────────────────────────────────────────────────────────────────────

class TFLiteModel:
    """Generic TensorFlow Lite model wrapper."""

    def __init__(self, model_path: Path):
        self._path = model_path
        self._interpreter = None
        self._input_details = None
        self._output_details = None
        self._load()

    def _load(self) -> None:
        try:
            import tflite_runtime.interpreter as tflite  # type: ignore
            self._interpreter = tflite.Interpreter(model_path=str(self._path))
        except ImportError:
            try:
                import tensorflow as tf  # type: ignore
                self._interpreter = tf.lite.Interpreter(model_path=str(self._path))
            except ImportError:
                logger.warning("TFLite runtime not available — running in stub mode")
                return

        if self._interpreter:
            self._interpreter.allocate_tensors()
            self._input_details = self._interpreter.get_input_details()
            self._output_details = self._interpreter.get_output_details()
            logger.info("Loaded TFLite model: %s", self._path.name)

    @property
    def is_available(self) -> bool:
        return self._interpreter is not None

    def run(self, input_data: np.ndarray) -> list[np.ndarray]:
        if not self.is_available:
            raise RuntimeError("TFLite interpreter not available")
        self._interpreter.set_tensor(self._input_details[0]["index"], input_data)
        self._interpreter.invoke()
        return [
            self._interpreter.get_tensor(out["index"])
            for out in self._output_details
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Face Detection Engine (TFLite)
# ─────────────────────────────────────────────────────────────────────────────

class EdgeFaceDetector:
    """
    Lightweight BlazeFace or MobileNet-SSD face detector for edge devices.
    Falls back to stub detection when TFLite is unavailable.
    """

    INPUT_SIZE = (128, 128)

    def __init__(self):
        model_path = MODEL_DIR / "face_detection.tflite"
        self._model = TFLiteModel(model_path) if model_path.exists() else None
        if self._model is None:
            logger.warning("Face detection model not found at %s", model_path)

    def detect_faces(self, frame: np.ndarray) -> list[DetectedFace]:
        """
        Detect faces in a camera frame.
        Returns a list of DetectedFace objects.
        """
        if self._model is None or not self._model.is_available:
            return self._stub_detect(frame)

        try:
            h, w = frame.shape[:2]
            resized = self._preprocess(frame)
            outputs = self._model.run(resized)
            return self._parse_detections(outputs, w, h)
        except Exception as exc:
            logger.error("Face detection error: %s", exc)
            return []

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Resize + normalize to model input requirements."""
        import cv2  # type: ignore
        resized = cv2.resize(frame, self.INPUT_SIZE)
        normalized = (resized.astype(np.float32) - 128.0) / 128.0
        return np.expand_dims(normalized, axis=0)

    def _parse_detections(
        self, outputs: list[np.ndarray], orig_w: int, orig_h: int
    ) -> list[DetectedFace]:
        faces = []
        # Output format depends on model — BlazeFace: [boxes, scores]
        if len(outputs) >= 2:
            boxes = outputs[0][0]
            scores = outputs[1][0]
            for box, score in zip(boxes, scores):
                if score > 0.5:
                    y1, x1, y2, x2 = box
                    x = int(x1 * orig_w)
                    y = int(y1 * orig_h)
                    w = int((x2 - x1) * orig_w)
                    h = int((y2 - y1) * orig_h)
                    faces.append(DetectedFace(bbox=(x, y, w, h), confidence=float(score)))
        return faces

    def _stub_detect(self, frame: np.ndarray) -> list[DetectedFace]:
        """Stub: returns a synthetic detection for testing."""
        logger.debug("Stub face detection called")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Face Embedding Engine (TFLite)
# ─────────────────────────────────────────────────────────────────────────────

class EdgeFaceEmbedder:
    """
    Lightweight MobileFaceNet embedding model.
    Generates 128-d embeddings suitable for similarity comparison.
    """

    EMBEDDING_SIZE = 128
    INPUT_SIZE = (112, 112)

    def __init__(self):
        model_path = MODEL_DIR / "face_embedding.tflite"
        self._model = TFLiteModel(model_path) if model_path.exists() else None

    def embed_face(self, face_crop: np.ndarray) -> list[float]:
        """Generate a 128-d face embedding from a cropped face image."""
        if self._model is None or not self._model.is_available:
            return self._stub_embed(face_crop)

        try:
            import cv2  # type: ignore
            resized = cv2.resize(face_crop, self.INPUT_SIZE).astype(np.float32)
            normalized = (resized - 127.5) / 128.0
            input_data = np.expand_dims(normalized, axis=0)
            outputs = self._model.run(input_data)
            embedding = outputs[0][0].tolist()
            norm = np.linalg.norm(embedding)
            return (np.array(embedding) / (norm + 1e-10)).tolist()
        except Exception as exc:
            logger.error("Face embedding error: %s", exc)
            return [0.0] * self.EMBEDDING_SIZE

    def _stub_embed(self, face_crop: np.ndarray) -> list[float]:
        """Stub: deterministic embedding from pixel hash."""
        seed = hash(face_crop.tobytes()) % (2 ** 31)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.EMBEDDING_SIZE)
        return (vec / (np.linalg.norm(vec) + 1e-10)).tolist()


# ─────────────────────────────────────────────────────────────────────────────
# Edge Inference Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class EdgeInferencePipeline:
    """
    Complete edge inference pipeline:
    1. Frame arrives from CCTV
    2. Face detection (TFLite)
    3. Face embedding (TFLite)
    4. Compare against local embedding cache
    5. If match: report to central API
    """

    def __init__(self, camera_id: str, match_threshold: float = 0.6):
        self.camera_id = camera_id
        self.threshold = match_threshold
        self.detector = EdgeFaceDetector()
        self.embedder = EdgeFaceEmbedder()
        self._embedding_cache: dict[str, list[float]] = {}
        self._frame_counter = 0
        logger.info("Edge pipeline initialized for camera: %s", camera_id)

    def load_embedding_cache(self, cache_path: Path) -> None:
        """Load the active missing persons embedding cache from JSON."""
        if not cache_path.exists():
            logger.warning("Embedding cache not found: %s", cache_path)
            return
        with open(cache_path) as f:
            data = json.load(f)
        self._embedding_cache = {
            item["case_number"]: item["embedding"]
            for item in data.get("embeddings", [])
        }
        logger.info("Loaded %d embeddings into edge cache", len(self._embedding_cache))

    def process_frame(self, frame: np.ndarray) -> list[EdgeMatchResult]:
        """Process a single camera frame and return any matches."""
        self._frame_counter += 1
        results = []

        faces = self.detector.detect_faces(frame)
        if not faces:
            return results

        for face in faces:
            # Crop face from frame
            x, y, w, h = face.bbox
            face_crop = frame[max(0, y):y + h, max(0, x):x + w]
            if face_crop.size == 0:
                continue

            embedding = self.embedder.embed_face(face_crop)
            face.embedding = embedding

            # Compare against cache
            best_match, best_score = self._find_best_match(embedding)

            if best_score >= self.threshold:
                result = EdgeMatchResult(
                    detected=True,
                    match_found=True,
                    case_number=best_match,
                    confidence=best_score,
                    camera_id=self.camera_id,
                    timestamp=time.time(),
                    frame_id=self._frame_counter,
                )
                results.append(result)
                self._report_match(result)
                logger.warning(
                    "MATCH FOUND: case=%s confidence=%.2f camera=%s frame=%d",
                    best_match, best_score, self.camera_id, self._frame_counter,
                )

        return results

    def _find_best_match(
        self, query_embedding: list[float]
    ) -> tuple[Optional[str], float]:
        """Cosine similarity comparison against the embedding cache."""
        if not self._embedding_cache:
            return None, 0.0

        query = np.array(query_embedding, dtype=np.float32)
        query_norm = query / (np.linalg.norm(query) + 1e-10)

        best_case = None
        best_score = 0.0

        for case_number, cached_emb in self._embedding_cache.items():
            cached = np.array(cached_emb, dtype=np.float32)
            cached_norm = cached / (np.linalg.norm(cached) + 1e-10)
            score = float(np.dot(query_norm, cached_norm))
            if score > best_score:
                best_score = score
                best_case = case_number

        return best_case, best_score

    def _report_match(self, result: EdgeMatchResult) -> None:
        """Send match to central DRISHTI API (non-blocking)."""
        try:
            import urllib.request
            payload = json.dumps({
                "case_number": result.case_number,
                "confidence": result.confidence,
                "camera_id": result.camera_id,
                "timestamp": result.timestamp,
                "source": "edge_camera",
            }).encode()
            req = urllib.request.Request(
                f"{CENTRAL_API}/search/edge-sighting",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Edge-API-Key": EDGE_API_KEY,
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as exc:
            logger.error("Failed to report match to central API: %s", exc)
            # Queue for retry — store locally and resync when connected
            self._queue_offline_report(result)

    def _queue_offline_report(self, result: EdgeMatchResult) -> None:
        """Store undelivered reports for later sync."""
        queue_file = MODEL_DIR / "offline_queue.jsonl"
        with open(queue_file, "a") as f:
            f.write(json.dumps({
                "case_number": result.case_number,
                "confidence": result.confidence,
                "camera_id": result.camera_id,
                "timestamp": result.timestamp,
            }) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the edge inference pipeline on a video source."""
    import argparse
    parser = argparse.ArgumentParser(description="DRISHTI Edge Inference")
    parser.add_argument("--camera", default="0", help="Camera ID or RTSP URL")
    parser.add_argument("--camera-id", default="CAM-001", help="Logical camera identifier")
    parser.add_argument("--threshold", type=float, default=0.6, help="Match threshold")
    parser.add_argument("--cache", type=Path, default=MODEL_DIR / "embeddings.json",
                        help="Embedding cache file")
    parser.add_argument("--skip-frames", type=int, default=5,
                        help="Process every N-th frame (performance)")
    args = parser.parse_args()

    try:
        import cv2  # type: ignore
    except ImportError:
        print("ERROR: OpenCV required. Install with: pip install opencv-python")
        return

    pipeline = EdgeInferencePipeline(camera_id=args.camera_id, match_threshold=args.threshold)
    pipeline.load_embedding_cache(args.cache)

    src = int(args.camera) if args.camera.isdigit() else args.camera
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        print(f"ERROR: Cannot open camera: {args.camera}")
        return

    print(f"DRISHTI Edge Inference running on camera {args.camera_id}")
    print("Press Ctrl+C to stop")

    frame_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            if frame_idx % args.skip_frames != 0:
                continue
            pipeline.process_frame(frame)
    except KeyboardInterrupt:
        print("\nStopping edge inference.")
    finally:
        cap.release()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
