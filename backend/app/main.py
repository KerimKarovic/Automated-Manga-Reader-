from fastapi import FastAPI, UploadFile
from fastapi import FastAPI, Depends
from fastapi import FastAPI, File
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.ml.panel_detection import detect_panels
from app.models import Manga
from app.tts.tts_engine import speak_text
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
    # Save the uploaded file locally.
    file_location = f"temp/{uuid.uuid4()}_{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Detect panels using the panel detection logic.
    panels = detect_panels(file_location)
    
    return {
        "message": "File received",
        "file_location": file_location,
        "num_panels": len(panels),
        "panels": panels
    }

@app.post("/tts")
def read_text_aloud(text: str):
    # Use text-to-speech to read the text aloud.
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
