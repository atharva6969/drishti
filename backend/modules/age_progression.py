"""Module 4 — AI Age Progression Pipeline.

Maintains a schedule of periodic age-progression updates so that
search profiles stay current even for cold cases.

In production the actual image generation is delegated to a
SAM-Age (or equivalent) model service.  This module manages the
schedule, metadata, and re-scan trigger logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.config import settings


@dataclass
class AgeProgressionRecord:
    """A single age-progression result for a missing person."""

    person_id: str
    original_age: int
    projected_age: float
    generated_photo_url: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AgeProgressionPipeline:
    """Manages periodic age-progression for all active missing persons."""

    def __init__(
        self,
        update_interval_months: int = settings.AGE_PROGRESSION_UPDATE_MONTHS,
    ) -> None:
        self._update_interval = timedelta(days=update_interval_months * 30)
        self._records: dict[str, list[AgeProgressionRecord]] = {}

    # ── Core operations ───────────────────────────────────────────

    def generate_progression(
        self,
        person_id: str,
        original_age: int,
        years_since_missing: float,
    ) -> AgeProgressionRecord:
        """Generate (or stub) an age-progressed photo.

        In production this calls the SAM-Age model service.  For the
        MVP it records the metadata so the pipeline can be exercised
        end-to-end.
        """
        projected_age = original_age + years_since_missing
        record = AgeProgressionRecord(
            person_id=person_id,
            original_age=original_age,
            projected_age=round(projected_age, 1),
            generated_photo_url=None,  # populated by model service
        )
        self._records.setdefault(person_id, []).append(record)
        return record

    def needs_update(self, person_id: str) -> bool:
        """Check whether this person's progression photo is stale."""
        records = self._records.get(person_id, [])
        if not records:
            return True
        latest = max(records, key=lambda r: r.created_at)
        return datetime.now(timezone.utc) - latest.created_at >= self._update_interval

    def get_latest(self, person_id: str) -> Optional[AgeProgressionRecord]:
        """Return the most recent progression record."""
        records = self._records.get(person_id, [])
        if not records:
            return None
        return max(records, key=lambda r: r.created_at)

    def get_all_records(self, person_id: str) -> list[AgeProgressionRecord]:
        return list(self._records.get(person_id, []))

    def persons_needing_update(self, person_ids: list[str]) -> list[str]:
        """Filter to person IDs that are due for an age-progression refresh."""
        return [pid for pid in person_ids if self.needs_update(pid)]
