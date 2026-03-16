"""
Unit tests for DRISHTI backend.
Tests cover core security, ML engines, and route predictor logic.
"""
import pytest
import numpy as np


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------
class TestSecurity:
    def test_password_hash_and_verify(self):
        from app.core.security import get_password_hash, verify_password
        pw = "SecurePassword123!"
        hashed = get_password_hash(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_create_and_decode_access_token(self):
        from app.core.security import create_access_token, decode_token
        token = create_access_token(subject="42", role="officer")
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "officer"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        from app.core.security import create_refresh_token, decode_token
        token = create_refresh_token(subject="42")
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self):
        from jose import JWTError
        from app.core.security import decode_token
        with pytest.raises(JWTError):
            decode_token("not-a-valid-token")


# ---------------------------------------------------------------------------
# Case number generation
# ---------------------------------------------------------------------------
class TestCaseService:
    def test_case_number_format(self):
        from app.services.case_service import _generate_case_number
        case_number = _generate_case_number()
        assert case_number.startswith("DRISHTI-")
        parts = case_number.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # hex suffix


# ---------------------------------------------------------------------------
# Face recognition engine (stub mode)
# ---------------------------------------------------------------------------
class TestFaceRecognitionEngine:
    def test_stub_embedding_shape(self):
        from ml.face_recognition.engine import FaceRecognitionEngine
        engine = FaceRecognitionEngine()
        result = engine.extract_embedding(b"fake_image_bytes")
        assert len(result.embedding) == 512
        assert result.face_detected is False

    def test_cosine_similarity_identical(self):
        from ml.face_recognition.engine import FaceRecognitionEngine
        engine = FaceRecognitionEngine(threshold=0.6)
        emb = [1.0] * 512
        sim, is_match = engine.compare_embeddings(emb, emb)
        assert abs(sim - 1.0) < 1e-6
        assert is_match is True

    def test_cosine_similarity_orthogonal(self):
        from ml.face_recognition.engine import FaceRecognitionEngine
        engine = FaceRecognitionEngine(threshold=0.6)
        emb1 = [1.0] + [0.0] * 511
        emb2 = [0.0, 1.0] + [0.0] * 510
        sim, is_match = engine.compare_embeddings(emb1, emb2)
        assert abs(sim) < 1e-6
        assert is_match is False

    def test_zero_vector_no_match(self):
        from ml.face_recognition.engine import FaceRecognitionEngine
        engine = FaceRecognitionEngine()
        sim, is_match = engine.compare_embeddings([0.0] * 512, [1.0] * 512)
        assert is_match is False


# ---------------------------------------------------------------------------
# Gait recognition engine (stub mode)
# ---------------------------------------------------------------------------
class TestGaitRecognitionEngine:
    def test_insufficient_frames_returns_no_detection(self):
        from ml.gait_recognition.engine import GaitRecognitionEngine
        engine = GaitRecognitionEngine()
        frames = [np.zeros((64, 64), dtype=np.uint8) for _ in range(5)]
        sig = engine.extract_signature(frames)
        assert sig.subject_detected is False

    def test_gei_computation(self):
        from ml.gait_recognition.engine import GaitRecognitionEngine
        engine = GaitRecognitionEngine()
        frames = [np.ones((64, 64), dtype=np.uint8) * 128 for _ in range(15)]
        gei = engine.extract_gait_energy_image(frames)
        assert gei is not None
        assert gei.shape == (64, 64)
        assert abs(float(gei.mean()) - 128.0) < 1.0

    def test_compare_signatures_identical(self):
        from ml.gait_recognition.engine import GaitRecognitionEngine
        engine = GaitRecognitionEngine(threshold=0.75)
        sig = [1.0] * 256
        sim, is_match = engine.compare_signatures(sig, sig)
        assert abs(sim - 1.0) < 1e-6
        assert is_match is True


# ---------------------------------------------------------------------------
# Route predictor
# ---------------------------------------------------------------------------
class TestTraffickingRoutePredictor:
    def test_stub_activation_when_no_networkx(self, monkeypatch):
        """Predictor returns a valid stub when networkx not available."""
        import sys
        import types

        # Create a fake networkx module that raises on import
        fake_nx = types.ModuleType("networkx")

        def _raise(*args, **kwargs):
            raise ImportError("networkx not available")

        fake_nx.DiGraph = _raise
        monkeypatch.setitem(sys.modules, "networkx", None)

        from ml.route_predictor.predictor import TraffickingRoutePredictor
        predictor = TraffickingRoutePredictor()
        activation = predictor.predict_routes(
            case_id=1,
            case_number="DRISHTI-20240101-AABBCC",
            source_location="Murshidabad",
        )
        # Should return stub data
        assert activation.case_id == 1
        assert len(activation.predicted_routes) >= 1

    def test_probability_adjustment_trafficking(self):
        """Trafficking case type increases route probability."""
        try:
            import networkx  # noqa: F401
        except ImportError:
            pytest.skip("networkx not installed")

        from ml.route_predictor.predictor import TraffickingRoutePredictor
        predictor = TraffickingRoutePredictor()
        if predictor._graph is None:
            pytest.skip("Graph not built")

        path = ["MSD", "HWH", "NDLS", "DEL"]
        prob_normal = predictor._calculate_probability(path, age=25, gender="male", case_type="missing")
        prob_trafficking = predictor._calculate_probability(path, age=25, gender="male", case_type="trafficking")
        assert prob_trafficking > prob_normal

    def test_route_database_integrity(self):
        """Verify route database has required fields."""
        from ml.route_predictor.predictor import ROUTE_DATABASE
        assert "nodes" in ROUTE_DATABASE
        assert "edges" in ROUTE_DATABASE
        for node in ROUTE_DATABASE["nodes"]:
            assert "id" in node
            assert "name" in node
            assert "type" in node
        for edge in ROUTE_DATABASE["edges"]:
            assert len(edge) == 6  # src, tgt, weight, h_min, h_max, transport


# ---------------------------------------------------------------------------
# Multimodal identity engine
# ---------------------------------------------------------------------------
class TestMultimodalIdentityEngine:
    def test_identity_match_result_combined_score(self):
        from ml.multimodal_engine import IdentityMatchResult
        match = IdentityMatchResult(
            case_id=1,
            case_number="DRISHTI-20240101-AABBCC",
            full_name="Test Person",
            face_score=0.9,
            clothing_score=0.8,
            body_score=0.7,
        )
        assert match.combined_score > 0.0
        assert match.combined_score <= 1.0
        assert match.signals_used == 3

    def test_should_alert_with_two_signals(self):
        from ml.multimodal_engine import IdentityMatchResult
        match = IdentityMatchResult(
            case_id=1,
            case_number="X",
            full_name="Test",
            face_score=0.8,
            gait_score=0.85,
        )
        assert match.should_alert is True

    def test_no_alert_below_threshold(self):
        from ml.multimodal_engine import IdentityMatchResult, ALERT_THRESHOLD
        match = IdentityMatchResult(
            case_id=1,
            case_number="X",
            full_name="Test",
            face_score=0.3,
        )
        assert match.combined_score < ALERT_THRESHOLD
