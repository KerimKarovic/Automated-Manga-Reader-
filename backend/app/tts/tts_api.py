from fastapi.responses import FileResponse
from app.database import get_db
from fastapi import APIRouter, Depends
from app.models import Chapter
import pyttsx3
import os

router = APIRouter()

@router.get("/tts/{chapter_id}")
def tts_for_chapter(chapter_id: str, db=Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        return {"error": "Chapter not found"}

    text = chapter.title or "No text available for this chapter"

    file_path = f"temp_tts_{chapter_id}.wav"

    # Save to file
    
    engine = pyttsx3.init()
    engine.save_to_file(text, file_path)
    engine.runAndWait()

    if not os.path.exists(file_path):
        return {"error": "Failed to generate TTS audio"}

    return FileResponse(path=file_path, media_type="audio/wav", filename=file_path)
