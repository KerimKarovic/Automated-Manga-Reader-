from fastapi.responses import FileResponse
from app.database import get_db
from fastapi import APIRouter, Depends
from app.models import Chapter
import pyttsx3
import tempfile
import os

router = APIRouter()

@router.get("/tts/{chapter_id}")
def tts_for_chapter(chapter_id: str, db=Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        return {"error": "Chapter not found"}

    text = chapter.title or "No text available for this chapter"

    # Use a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        file_path = tmp.name

    engine = pyttsx3.init()
    engine.save_to_file(text, file_path)
    engine.runAndWait()

    # Confirm file exists and is not empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {"error": "Failed to generate valid TTS audio"}

    return FileResponse(path=file_path, media_type="audio/wav", filename=os.path.basename(file_path))
