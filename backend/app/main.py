from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.database import init_db, get_db
from app.ml.panel_detection import detect_panels
from app.models import Manga, Chapter, Page  # Make sure these models include the necessary fields.
from app.api.mangadex_chapters import search_manga_by_title, get_manga_feed, get_chapter_images, construct_image_urls
from app.api.tts_api import router as tts_router  
from typing import Optional
import requests
import os
import uuid

# Initilize the database (create tables if they don't exist)
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





@app.post("/manga")
def create_manga(title: str, author: str, mangadex_id: Optional[str] = None, db: Session = Depends(get_db)):
    new_manga = Manga(title=title, author=author, mangadexId = mangadex_id)
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
    """
    # Fetch image metadata
    base_url, chapter_hash, data_files, _ = get_chapter_images(chapter_id)

    # Fetch full chapter metadata to get the associated manga_id
    chapter_metadata = requests.get(f"https://api.mangadex.org/chapter/{chapter_id}").json()
    relationships = chapter_metadata.get("data", {}).get("relationships", [])
    manga_rel = next((rel for rel in relationships if rel["type"] == "manga"), None)

    if not manga_rel:
        raise HTTPException(status_code=404, detail="Manga relationship not found in chapter metadata")

    mangadex_manga_id = manga_rel["id"]

    # Find the manga in the local DB
    manga_record = db.query(Manga).filter(Manga.mangadexId == mangadex_manga_id).first()
    if not manga_record:
        raise HTTPException(status_code=404, detail="Manga record not found for provided external ID")

    # Check if chapter already exists to avoid duplication
    existing_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if existing_chapter:
        return {"message": f"Chapter {chapter_id} already exists in database"}

    new_chapter = Chapter(
        id=chapter_id,
        manga_id=manga_record.id,
        volume=chapter_metadata["data"]["attributes"].get("volume", ""),
        chapter_number=chapter_metadata["data"]["attributes"].get("chapter", ""),
        title=chapter_metadata["data"]["attributes"].get("title", ""),
        translated_language=chapter_metadata["data"]["attributes"].get("translatedLanguage", "en"),
        chapter_hash=chapter_hash
    )
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)

    for index, filename in enumerate(data_files):
        full_url = f"{base_url}/data/{chapter_hash}/{filename}"
        db.add(Page(
            chapter_id=chapter_id,
            image_url=full_url,
            quality="data",
            page_number=index + 1  # ✅ Add page number
        ))

    db.commit()

    return {"message": "Chapter and pages stored successfully", "chapter": new_chapter.id}

# Include the MangaDex router in your main app.
app.include_router(mangadex_router)
app.include_router(tts_router)  

