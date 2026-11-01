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


def boundary_offsets(transcript: str, segments: list[str]) -> list[int]:
    """Return internal Unicode UI offsets after exact reconstruction validation."""
    if not segments or any(not segment for segment in segments):
        raise ValueError("Segments must be nonempty.")
    if "".join(segments) != transcript:
        raise ValueError("Segments must reconstruct the original text exactly.")
    offsets: list[int] = []
    position = 0
    for segment in segments[:-1]:
        position += len(segment)
        offsets.append(position)
    return offsets
