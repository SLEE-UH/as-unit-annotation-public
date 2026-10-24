"""Plain Python rules for the AS-unit annotation application."""

from typing import Any

SAVED_FIELDS = (
    "transcript",
    "prosodic_features",
    "as_unit_annotation",
)


def select_saved_fields(record: dict[str, Any]) -> dict[str, Any]:
    """Select derived analysis fields without retaining original audio."""
    return {
        key: record[key]
        for key in SAVED_FIELDS
        if key in record
    }
