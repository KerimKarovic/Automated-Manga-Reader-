from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.ml.panel_detection import detect_panels
from app.models import Manga, Chapter, Page  # Make sure these models include the necessary fields.
from app.tts.tts_engine import speak_text
from app.api.mangadex_chapters import search_manga_by_title, get_manga_feed, get_chapter_images, construct_image_urls
import os
import uuid

# Initialize the database (create tables if they don't exist)
init_db()

# Create the FastAPI app instance.
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Manga Reader Backend!"}

@app.post("/upload-page")
async def upload_page(file: UploadFile = File(...)):
    file_location = f"temp/{uuid.uuid4()}_{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    panels = detect_panels(file_location)
    return {
        "message": "File received",
        "file_location": file_location,
        "num_panels": len(panels),
        "panels": panels
    }

@app.post("/tts")
def read_text_aloud_endpoint(text: str):
    speak_text(text)
    return {"message": f"Reading text: {text}"}

# Dependency for obtaining a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/manga")
def create_manga(title: str, author: str, db: Session = Depends(get_db)):
    new_manga = Manga(title=title, author=author)
    db.add(new_manga)
    db.commit()
    db.refresh(new_manga)
    return new_manga

@app.get("/manga")
def list_manga(db: Session = Depends(get_db)):
    return db.query(Manga).all()

# ----- MangaDex Integration Endpoints -----

mangadex_router = APIRouter()

@mangadex_router.get("/mangadex/search")
def search_manga(title: str):
    """
    Search for a manga by title. For example, use "ONE PUNCH MAN".
    """
    result = search_manga_by_title(title)
    # Return a simplified list of manga IDs and titles from the result.
    mangas = [{"id": m["id"], "title": m["attributes"].get("title", {}).get("en", "Unknown")} for m in result.get("data", [])]
    return {"mangas": mangas}

@mangadex_router.get("/mangadex/{manga_id}/chapters")
def get_chapters(manga_id: str, language: str = "en"):
    """
    Retrieve the chapter feed for a specific manga, filtered by language.
    """
    result = get_manga_feed(manga_id, translated_languages=[language])
    chapters = [{"id": c["id"], "chapter": c["attributes"].get("chapter"), "volume": c["attributes"].get("volume")} for c in result.get("data", [])]
    return {"chapters": chapters}

@mangadex_router.get("/mangadex/chapter/{chapter_id}/images")
def get_chapter_image_urls(chapter_id: str, quality: str = "data"):
    """
    Retrieve the image URLs for a given chapter.
    Quality can be "data" for original or "data-saver" for compressed images.
    """
    base_url, chapter_hash, data_files, data_saver_files = get_chapter_images(chapter_id)
    filenames = data_files if quality == "data" else data_saver_files
    urls = construct_image_urls(base_url, chapter_hash, filenames, quality)
    return {"chapter_id": chapter_id, "quality": quality, "image_urls": urls}

@mangadex_router.post("/mangadex/store-chapter/{chapter_id}")
def store_chapter(chapter_id: str, db: Session = Depends(get_db)):
    """
    Fetch chapter image metadata from MangaDex and store chapter and pages in the database.
    (For this example, we assume that the chapter metadata includes minimal fields.)
    """
    # Retrieve chapter image metadata from MangaDex
    base_url, chapter_hash, data_files, _ = get_chapter_images(chapter_id)
    
    # Look up the manga record in our local database using the external MangaDex ID.
    # For example, for "One-Punch Man", we expect mangadexId to be 'd8a959f7-648e-4c8d-8f23-f1f3f8e129f3'
    manga_record = db.query(Manga).filter(Manga.mangadexId == 'd8a959f7-648e-4c8d-8f23-f1f3f8e129f3').first()
    if not manga_record:
        raise HTTPException(status_code=404, detail="Manga record not found for provided external ID")
    
    new_chapter = Chapter(
        id=chapter_id,
        manga_id=manga_record.id,  # Link to the found manga record.
        volume="1",
        chapter_number="1",
        title="Example Chapter",
        translated_language="en",
        chapter_hash=chapter_hash
    )
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    
    # Create Page records for each image in original quality.
    for filename in data_files:
        full_url = f"{base_url}/data/{chapter_hash}/{filename}"
        new_page = Page(
            chapter_id=chapter_id,
            image_url=full_url,
            quality="data"
        )
        db.add(new_page)
    db.commit()
    return {"message": "Chapter and pages stored successfully", "chapter": new_chapter.id}

# Include the MangaDex router in your main app.
app.include_router(mangadex_router)
