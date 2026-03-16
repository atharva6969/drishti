"""Tests for Module 4 — AI Age Progression Pipeline."""

import pytest
from datetime import datetime, timedelta, timezone

from backend.modules.age_progression import AgeProgressionPipeline


@pytest.fixture
def pipeline():
    return AgeProgressionPipeline(update_interval_months=3)


class TestGeneration:
    def test_generate_returns_record(self, pipeline):
        rec = pipeline.generate_progression("p-1", original_age=7, years_since_missing=2.0)
        assert rec.person_id == "p-1"
        assert rec.original_age == 7
        assert rec.projected_age == 9.0

    def test_projected_age_accumulates(self, pipeline):
        rec = pipeline.generate_progression("p-1", original_age=7, years_since_missing=5.5)
        assert rec.projected_age == 12.5


class TestUpdateSchedule:
    def test_needs_update_when_no_records(self, pipeline):
        assert pipeline.needs_update("new-person") is True

    def test_no_update_needed_after_generation(self, pipeline):
        pipeline.generate_progression("p-1", 7, 1.0)
        assert pipeline.needs_update("p-1") is False

    def test_persons_needing_update(self, pipeline):
        pipeline.generate_progression("p-1", 7, 1.0)
        result = pipeline.persons_needing_update(["p-1", "p-2"])
        assert "p-2" in result
        assert "p-1" not in result


class TestRetrieval:
    def test_get_latest(self, pipeline):
        pipeline.generate_progression("p-1", 7, 1.0)
        pipeline.generate_progression("p-1", 7, 2.0)
        latest = pipeline.get_latest("p-1")
        assert latest is not None
        assert latest.projected_age == 9.0

    def test_get_latest_none_for_unknown(self, pipeline):
        assert pipeline.get_latest("unknown") is None

    def test_get_all_records(self, pipeline):
        pipeline.generate_progression("p-1", 7, 1.0)
        pipeline.generate_progression("p-1", 7, 2.0)
        assert len(pipeline.get_all_records("p-1")) == 2
