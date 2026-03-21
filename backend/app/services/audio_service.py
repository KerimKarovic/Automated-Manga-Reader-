from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.services.chapter_service import chapter_service


class AudioService:
    def get_chapter_audio_status(self, chapter_id: str, db: Session) -> dict:
        chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
        if not chapter:
            raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

        analyses = (
            db.query(models.PageAnalysis)
            .join(models.Page, models.Page.id == models.PageAnalysis.page_id)
            .filter(models.Page.chapter_id == chapter_id)
            .all()
        )

        available_text = [analysis.raw_text for analysis in analyses if analysis.raw_text and analysis.raw_text.strip()]

        if not available_text:
            return {
                "chapter_id": chapter_id,
                "status": "unavailable",
                "message": "Audio reading is not available yet for this chapter because OCR text has not been generated.",
            }

        return {
            "chapter_id": chapter_id,
            "status": "ready",
            "message": "OCR text is available. Audio generation can be implemented in a future TTS provider layer.",
        }


audio_service = AudioService()
