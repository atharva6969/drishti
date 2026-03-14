"""Tests for Module 1 — Multimodal Identity Engine."""

import pytest

from backend.modules.identity_engine import (
    SignalResult,
    combine_signals,
    compute_companion_confidence,
    compute_face_confidence,
    compute_gait_confidence,
    compute_clothing_confidence,
    compute_body_biometric_confidence,
    identify,
)


class TestIndividualSignals:
    def test_face_unavailable_when_no_images(self):
        result = compute_face_confidence(None, None)
        assert not result.available
        assert result.confidence == 0.0

    def test_face_available_with_images(self):
        result = compute_face_confidence(b"img1", b"img2")
        assert result.available
        assert result.signal_name == "face"

    def test_gait_unavailable_when_no_sequences(self):
        result = compute_gait_confidence(None, None)
        assert not result.available

    def test_gait_available_with_sequences(self):
        result = compute_gait_confidence([1, 2], [3, 4])
        assert result.available

    def test_clothing_unavailable_when_empty(self):
        result = compute_clothing_confidence("", "")
        assert not result.available

    def test_clothing_available_with_descriptions(self):
        result = compute_clothing_confidence("red dupatta", "red dupatta blue bag")
        assert result.available

    def test_body_biometrics_unavailable(self):
        result = compute_body_biometric_confidence(None, None)
        assert not result.available

    def test_body_biometrics_available(self):
        result = compute_body_biometric_confidence({"h": 150}, {"h": 152})
        assert result.available

    def test_companion_no_overlap(self):
        result = compute_companion_confidence(["a", "b"], ["c", "d"])
        assert result.available
        assert result.confidence == 0.0

    def test_companion_full_overlap(self):
        result = compute_companion_confidence(["a", "b"], ["a", "b"])
        assert result.confidence == 1.0

    def test_companion_partial_overlap(self):
        result = compute_companion_confidence(["a", "b", "c"], ["a", "d"])
        assert 0 < result.confidence < 1


class TestCombineSignals:
    def test_no_available_signals(self):
        signals = [
            SignalResult("face", 0.0, available=False),
            SignalResult("gait", 0.0, available=False),
        ]
        confidence, alert = combine_signals(signals)
        assert confidence == 0.0
        assert alert is False

    def test_single_signal_below_threshold(self):
        signals = [SignalResult("face", 0.5, available=True)]
        confidence, alert = combine_signals(signals)
        assert confidence == 0.5
        # Only 1 signal → below MIN_SIGNALS_FOR_ALERT (default 2)
        assert alert is False

    def test_two_high_signals_trigger_alert(self):
        signals = [
            SignalResult("face", 0.95, available=True),
            SignalResult("gait", 0.90, available=True),
        ]
        confidence, alert = combine_signals(signals)
        assert confidence > 0.7
        assert alert is True

    def test_empty_signal_list(self):
        confidence, alert = combine_signals([])
        assert confidence == 0.0
        assert alert is False


class TestIdentify:
    def test_identify_no_data(self):
        match = identify("person-1")
        assert match.person_id == "person-1"
        assert match.combined_confidence == 0.0
        assert match.is_alert_worthy is False
        assert len(match.signals) == 5

    def test_identify_with_companions_overlap(self):
        match = identify(
            "person-2",
            probe_companions=["x", "y"],
            gallery_companions=["x", "y"],
        )
        assert match.combined_confidence > 0
        # Only 1 signal contributing → not alert worthy
        assert match.is_alert_worthy is False

    def test_matched_signal_names(self):
        match = identify(
            "person-3",
            probe_companions=["a"],
            gallery_companions=["a"],
        )
        assert "companion" in match.matched_signal_names
