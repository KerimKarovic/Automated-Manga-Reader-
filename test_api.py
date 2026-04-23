#!/usr/bin/env python
"""Test the API endpoint to see if ocr_text is being returned"""
import sys
backend_path = r'd:\Python Projects\AutomatedMangaReader\Automated-Manga-Reader-\backend'
sys.path.insert(0, backend_path)
import os
os.chdir(backend_path)

import httpx
from app.db.database import SessionLocal
from app.db import models

# Find a chapter with OCR data
db = SessionLocal()

# Use specific chapter that we know has good OCR
target_chapter = db.query(models.Chapter).filter(models.Chapter.id.like("b5ae762c%")).first()

if not target_chapter:
    chapters = db.query(models.Chapter).all()
    for ch in chapters:
        page_ids = [p.id for p in ch.pages]
        ocr_count = db.query(models.PageOCR).filter(models.PageOCR.page_id.in_(page_ids)).count()
        if ocr_count > 0:
            target_chapter = ch
            break

db.close()

if not target_chapter:
    print("No chapters with OCR data found")
    exit(1)

chapter_id = target_chapter.id
print(f"Testing with chapter: {chapter_id[:8]}...\n")

url = f"http://localhost:8001/chapters/{chapter_id}/pages"

try:
    response = httpx.get(url, timeout=10)
    data = response.json()
    
    # Show first 5 pages
    print("=== First 5 Pages ===\n")
    for page in data[:5]:
        ocr_text = page.get('ocr_text')
        ocr_text_display = repr(ocr_text)[:40] if ocr_text else "None"
        print(f"Page {page.get('page_number'):2d}: ocr_text={ocr_text_display}")
        
except Exception as e:
    print(f"Error: {e}")
