from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.schemas import AudioGenerateResponse, AudioStatusResponse
from app.services.chapter_service import chapter_service
from app.services.ocr_service import ocr_service
from app.services.tts_service import tts_service

router = APIRouter(prefix="/audio", tags=["audio"])


class AudioGenerateRequest(BaseModel):
    text: str | None = None  # Optional: if provided, generates audio for this text instead of entire chapter


@router.post("/chapter/{chapter_id}/generate", response_model=AudioGenerateResponse)
async def generate_chapter_audio(chapter_id: str, request: AudioGenerateRequest | None = None, db: Session = Depends(get_db)) -> AudioGenerateResponse:
    chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
    if not chapter:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

    # Use provided text if available, otherwise get entire chapter text
    if request and request.text:
        chapter_text = request.text
    else:
        chapter_text = ocr_service.get_chapter_combined_text(chapter_id=chapter_id, db=db)
    
    result = await tts_service.generate_chapter_audio(chapter_id=chapter_id, chapter_text=chapter_text)
    return AudioGenerateResponse(**result)


@router.get("/chapter/{chapter_id}", response_model=AudioStatusResponse)
def get_chapter_audio_status(chapter_id: str, db: Session = Depends(get_db)) -> AudioStatusResponse:
    chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
    if not chapter:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

    chapter_text = ocr_service.get_chapter_combined_text(chapter_id=chapter_id, db=db)
    result = tts_service.get_chapter_audio_status(chapter_id=chapter_id, chapter_text=chapter_text)
    return AudioStatusResponse(**result)


@router.get("/file/{chapter_id}/{voice}_{text_hash}.mp3")
def serve_audio_file(chapter_id: str, voice: str, text_hash: str):
    from app.core.config import settings
    from pathlib import Path

    audio_path = Path(settings.audio_cache_dir) / chapter_id / f"{voice}_{text_hash}.mp3"
    if not audio_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={"message": "Audio file not found"})

    # Determine media type based on actual file content
    file_size = audio_path.stat().st_size
    
    # Check if it's actually a WAV file (starts with RIFF)
    with open(audio_path, 'rb') as f:
        header = f.read(4)
        if header == b'RIFF':
            media_type = "audio/wav"
        elif header[:2] == b'\xff\xfb' or header[:2] == b'\xff\xfa':  # MP3 sync
            media_type = "audio/mpeg"
        else:
            media_type = "audio/mpeg"  # Default fallback
    
    # Return with proper headers for streaming
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=f"{chapter_id}.mp3",
        headers={"Accept-Ranges": "bytes"}
    )

