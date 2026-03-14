"""Module 6 — Privacy & Ethics Architecture.

Implements the five safeguards that make DRISHTI a humanitarian alert
system rather than a surveillance system:

1. Consent-First Database — only registered missing persons processed.
2. No Live Tracking — activates only on registered queries.
3. Audit Trail — every action logged with officer ID.
4. Decentralised Architecture — state-scoped data access.
5. Human-in-Loop — AI flags, human decides.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.config import settings
from backend.models.schemas import AuditEntry, CaseStatus, MissingPerson


class PrivacyManager:
    """Enforces all DRISHTI privacy and ethics safeguards."""

    def __init__(self) -> None:
        self._audit_log: list[AuditEntry] = []
        self._active_persons: dict[str, MissingPerson] = {}

    # ── 1. Consent-first database ─────────────────────────────────

    def register_person(self, person: MissingPerson) -> bool:
        """Register a missing person only if consent is provided."""
        if not person.consent_given:
            self._log("register_blocked", "system", person.id, "consent not given")
            return False
        self._active_persons[person.id] = person
        self._log("person_registered", "system", person.id)
        return True

    def is_registered(self, person_id: str) -> bool:
        return person_id in self._active_persons

    # ── 2. Data lifecycle (30-day retention after resolution) ─────

    def resolve_case(self, person_id: str, officer_id: str) -> bool:
        person = self._active_persons.get(person_id)
        if person is None:
            return False
        person.case_status = CaseStatus.RESOLVED
        self._log("case_resolved", officer_id, person_id)
        return True

    def purge_expired(self) -> list[str]:
        """Remove records that have exceeded the retention period."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=settings.ACTIVE_SEARCH_RETENTION_DAYS)
        purged: list[str] = []
        for pid, person in list(self._active_persons.items()):
            if person.case_status == CaseStatus.RESOLVED and person.created_at < cutoff:
                del self._active_persons[pid]
                self._log("record_purged", "system", pid)
                purged.append(pid)
        return purged

    # ── 3. Audit trail ────────────────────────────────────────────

    def _log(
        self,
        action: str,
        officer_id: str,
        target_person_id: Optional[str] = None,
        details: str = "",
    ) -> AuditEntry:
        entry = AuditEntry(
            action=action,
            officer_id=officer_id,
            target_person_id=target_person_id,
            details=details,
        )
        self._audit_log.append(entry)
        return entry

    def log_action(
        self,
        action: str,
        officer_id: str,
        target_person_id: Optional[str] = None,
        details: str = "",
    ) -> AuditEntry:
        """Public audit logging for any system action."""
        return self._log(action, officer_id, target_person_id, details)

    def get_audit_log(
        self,
        officer_id: Optional[str] = None,
        target_person_id: Optional[str] = None,
    ) -> list[AuditEntry]:
        entries = self._audit_log
        if officer_id:
            entries = [e for e in entries if e.officer_id == officer_id]
        if target_person_id:
            entries = [e for e in entries if e.target_person_id == target_person_id]
        return entries

    # ── 4. State-scoped access (decentralised architecture) ───────

    def get_persons_for_state(self, state: str) -> list[MissingPerson]:
        """Return only persons whose last-seen location matches *state*.

        Enforces the federated model: state police only see their data.
        """
        return [
            p
            for p in self._active_persons.values()
            if state.lower() in p.last_seen_location.lower()
        ]

    # ── 5. Human-in-loop verification ─────────────────────────────

    @staticmethod
    def requires_human_verification() -> bool:
        """Return whether human verification is required before action.

        This is always ``True`` in the current configuration — AI flags,
        human decides.
        """
        return settings.HUMAN_IN_LOOP_REQUIRED
