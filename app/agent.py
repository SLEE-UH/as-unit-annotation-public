"""Request/response schemas; model integration will be added later."""

from pydantic import BaseModel


class AudioAnalysisRequest(BaseModel):
    """Minimal information about the submitted audio file."""

    filename: str


class AnalysisResponse(BaseModel):
    """Structured result fields described in the project proposal."""

    transcript: str
    prosodic_features: str
    as_unit_annotation: str
