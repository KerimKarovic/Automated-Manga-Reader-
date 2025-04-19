from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
import pyttsx3
import os

from app.database import get_db
from app.models import Chapter, Page  # Adjust if your models are in another module

router = APIRouter()

@router.get("/tts/{chapter_id}")
def tts_for_chapter(chapter_id: str, db: Session = Depends(get_db)):
    # Fetch chapter and its pages
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    pages = db.query(Page).filter(Page.chapter_id == chapter_id).order_by(Page.page_number).all()
    if not pages:
        raise HTTPException(status_code=404, detail="No pages found for this chapter")

    # Combine text from all pages
    combined_text = " ".join(page.text for page in pages if page.text)

    if not combined_text.strip():
        raise HTTPException(status_code=400, detail="No text content available for TTS")

    # Generate TTS using pyttsx3
    temp_filename = "temp_audio.mp3"
    engine = pyttsx3.init()
    engine.save_to_file(combined_text, temp_filename)
    engine.runAndWait()

    # Stream the audio
    def iterfile():
        with open(temp_filename, mode="rb") as file_like:
            yield from file_like
        os.remove(temp_filename)

    return StreamingResponse(iterfile(), media_type="audio/mpeg")
