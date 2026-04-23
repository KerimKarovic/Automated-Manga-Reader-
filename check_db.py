#!/usr/bin/env python
import sys
backend_path = r'd:\Python Projects\AutomatedMangaReader\Automated-Manga-Reader-\backend'
sys.path.insert(0, backend_path)
import os
os.chdir(backend_path)
from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()

# Get chapter b5ae762c which had OCR data from earlier tests
target_id = "b5ae762c-9959-4a8f-86f8-26f7e2f8c8d4"
ch = db.query(models.Chapter).filter(models.Chapter.id.like("b5ae762c%")).first()

if ch:
    print(f'Chapter: {ch.id}')
    # Check page 1
    page = ch.pages[0]
    ocr = db.query(models.PageOCR).filter(models.PageOCR.page_id == page.id).first()
    print(f'Page {page.page_number} (ID={page.id}):')
    print(f'  OCR record exists: {ocr is not None}')
    if ocr:
        print(f'  Status: {ocr.status}')
        print(f'  Raw text len: {len(ocr.raw_text or "")}')
        print(f'  Cleaned text len: {len(ocr.cleaned_text or "")}')
        print(f'  Cleaned text: {repr(ocr.cleaned_text[:50] if ocr.cleaned_text else None)}')
else:
    print("Chapter not found")
    
db.close()
