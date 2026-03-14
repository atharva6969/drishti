import pytest
from datetime import datetime
from app.modules.identity_engine import IdentityEngine


@pytest.fixture
def engine():
    return IdentityEngine()


def test_analyze_face_returns_proper_structure(engine):
    result = engine.analyze_face("test_image.jpg")
    
    assert "embedding" in result
    assert "confidence" in result
    assert "detected" in result
    assert isinstance(result["embedding"], list)
    assert len(result["embedding"]) > 0
    assert 0.0 <= result["confidence"] <= 1.0


def test_analyze_face_confidence_in_range(engine):
    result = engine.analyze_face("test_image.jpg")
    assert 0.0 <= result["confidence"] <= 1.0


def test_analyze_gait_returns_proper_structure(engine):
    result = engine.analyze_gait("test_video.mp4")
    
    assert "gait_embedding" in result
    assert "confidence" in result
    assert "detected" in result
    assert isinstance(result["gait_embedding"], list)


def test_analyze_clothing_returns_proper_structure(engine):
    result = engine.analyze_clothing("test_image.jpg")
    
    assert "confidence" in result
    assert "detected" in result
    assert "embedding" in result


def test_analyze_body_proportions_returns_proper_structure(engine):
    result = engine.analyze_body_proportions("test_image.jpg")
    
    assert "height_ratio" in result
    assert "confidence" in result
    assert "detected" in result


def test_companion_pattern_analysis(engine):
    result = engine.analyze_companion_patterns(
        person_id="test_person_1",
        location="Howrah Station",
        timestamp=datetime.utcnow()
    )
    
    assert "person_id" in result
    assert "location" in result
    assert "companions_detected" in result
    assert result["person_id"] == "test_person_1"


def test_confidence_score_computation_single_signal(engine):
    signals = {
        "face": {"confidence": 0.9, "detected": True}
    }
    result = engine.compute_identity_confidence(signals)
    
    assert "overall_confidence" in result
    assert "signal_scores" in result
    assert "is_match" in result
    assert "confidence_level" in result
    assert 0.0 <= result["overall_confidence"] <= 1.0


def test_confidence_score_computation_multi_signal(engine):
    signals = {
        "face": {"confidence": 0.85, "detected": True},
        "gait": {"confidence": 0.70, "detected": True},
        "clothing": {"confidence": 0.60, "detected": True},
        "body": {"confidence": 0.75, "detected": True}
    }
    result = engine.compute_identity_confidence(signals)
    
    assert result["overall_confidence"] > 0
    assert len(result["signals_used"]) == 4
    assert result["confidence_level"] in ["high", "medium", "low"]


def test_high_confidence_is_match(engine):
    signals = {
        "face": {"confidence": 0.95, "detected": True},
        "gait": {"confidence": 0.90, "detected": True}
    }
    result = engine.compute_identity_confidence(signals)
    assert result["is_match"] is True
    assert result["confidence_level"] in ["high", "medium"]


def test_low_confidence_not_match(engine):
    signals = {
        "face": {"confidence": 0.30, "detected": True},
        "gait": {"confidence": 0.25, "detected": True}
    }
    result = engine.compute_identity_confidence(signals)
    assert result["is_match"] is False
    assert result["confidence_level"] == "low"


def test_no_detected_signals(engine):
    signals = {
        "face": {"confidence": 0.8, "detected": False},
        "gait": {"confidence": 0.7, "detected": False}
    }
    result = engine.compute_identity_confidence(signals)
    assert result["overall_confidence"] == 0.0


def test_full_identification_pipeline(engine):
    result = engine.identify_person("test_image.jpg", case_id="CASE-001")
    
    assert "case_id" in result
    assert "signals" in result
    assert "identity_result" in result
    assert result["case_id"] == "CASE-001"
