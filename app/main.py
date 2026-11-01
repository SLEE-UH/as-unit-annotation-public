"""FastAPI routes for synthetic text and the preserved audio placeholder."""

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.agent import (
    AnalysisResponse,
    AnnotationFailed,
    AnnotationInvalid,
    AnnotationTimedOut,
    AnnotationUnavailable,
    AudioAnalysisRequest,
    TextAnalysisRequest,
    TextAnalysisResponse,
    suggest_as_units,
)

app = FastAPI(title="Automatic AS-unit Annotation Application")
PAGE_FILE = Path(__file__).with_name("page.html")


@app.get("/", response_class=FileResponse)
def show_page() -> FileResponse:
    """Serve synthetic text analysis, review, and the audio placeholder page."""
    return FileResponse(PAGE_FILE, media_type="text/html")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    audio: Annotated[UploadFile, File()],
) -> AnalysisResponse:
    """Accept an upload and return fixed placeholders, without reading the audio."""
    request = AudioAnalysisRequest(filename=audio.filename or "")

    # The request model defines the submitted filename; no audio data is used.
    _ = request

    return AnalysisResponse(
        transcript="[Placeholder transcript — transcription is not implemented.]",
        prosodic_features="[Placeholder prosody — no features extracted.]",
        as_unit_annotation=(
            "[Placeholder AS-unit annotation — no boundaries predicted.]"
        ),
    )


Annotator = Callable[[TextAnalysisRequest], Awaitable[TextAnalysisResponse]]


def get_annotator() -> Annotator:
    return suggest_as_units


@app.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    annotate: Annotated[Annotator, Depends(get_annotator)],
) -> TextAnalysisResponse:
    """Analyze synthetic text; keep all provider configuration server-side."""
    try:
        return await annotate(request)
    except AnnotationUnavailable:
        raise HTTPException(503, "Text analysis is not configured on the server.") from None
    except AnnotationTimedOut:
        raise HTTPException(504, "Text analysis timed out. Please try again.") from None
    except AnnotationInvalid:
        raise HTTPException(502, "The model could not return valid segmentation.") from None
    except AnnotationFailed:
        raise HTTPException(502, "Text analysis is temporarily unavailable.") from None
