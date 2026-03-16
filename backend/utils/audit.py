"""Audit utilities shared across DRISHTI modules."""

from __future__ import annotations

from backend.models.schemas import AuditEntry


def format_audit_entry(entry: AuditEntry) -> str:
    """Human-readable representation of an audit entry."""
    parts = [
        f"[{entry.timestamp.isoformat()}]",
        f"action={entry.action}",
        f"officer={entry.officer_id}",
    ]
    if entry.target_person_id:
        parts.append(f"target={entry.target_person_id}")
    if entry.details:
        parts.append(f"details={entry.details}")
    return " | ".join(parts)
