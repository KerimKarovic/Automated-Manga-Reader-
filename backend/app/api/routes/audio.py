from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import AudioResponse
from app.services.audio_service import audio_service

router = APIRouter(prefix="/audio", tags=["audio"])


@router.get("/chapter/{chapter_id}", response_model=AudioResponse)
def chapter_audio(chapter_id: str, db: Session = Depends(get_db)) -> AudioResponse:
    response = audio_service.get_chapter_audio_status(chapter_id=chapter_id, db=db)
    return AudioResponse(**response)
