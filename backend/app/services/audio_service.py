from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.chapter_service import chapter_service
from app.services.ocr_service import ocr_service


class AudioService:
    def get_chapter_audio_status(self, chapter_id: str, db: Session) -> dict:
        chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
        if not chapter:
            raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

        chapter_text = ocr_service.get_chapter_combined_text(chapter_id=chapter_id, db=db)
        if not chapter_text.strip():
            return {
                "chapter_id": chapter_id,
                "status": "unavailable",
                "message": "Audio reading is not available yet for this chapter because OCR text has not been generated.",
                "text_available": False,
                "chapter_text_length": 0,
            }

        return {
            "chapter_id": chapter_id,
            "status": "ready",
            "message": "OCR text is available. Audio generation can be implemented in a future TTS provider layer.",
            "text_available": True,
            "chapter_text_length": len(chapter_text),
        }


audio_service = AudioService()
