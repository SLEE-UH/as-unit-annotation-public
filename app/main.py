"""FastAPI routes for the workshop skeleton. No audio is processed or saved."""

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from app.agent import AnalysisResponse, AudioAnalysisRequest

app = FastAPI(title="Automatic AS-unit Annotation Application")
PAGE_FILE = Path(__file__).with_name("page.html")


@app.get("/", response_class=FileResponse)
def show_page() -> FileResponse:
    """Serve the proposal-based upload and result review page."""
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
