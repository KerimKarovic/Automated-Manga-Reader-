#!/usr/bin/env python
import sys; sys.path.insert(0, 'backend')
import os; os.chdir('d:/Python Projects/AutomatedMangaReader/Automated-Manga-Reader-/backend')
from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()
chapters = db.query(models.Chapter).order_by(models.Chapter.created_at.desc()).limit(3).all()
for ch in chapters:
    print(f'Chapter: {ch.id}')
    page_ids = [p.id for p in ch.pages]
    ocr_records = db.query(models.PageOCR).filter(models.PageOCR.page_id.in_(page_ids)).all()
    print(f'  Total pages: {len(page_ids)}, OCR records: {len(ocr_records)}')
    
    # Check specific pages with text
    pages_with_text = [ocr for ocr in ocr_records if ocr.cleaned_text and len(ocr.cleaned_text) > 0]
    print(f'  Pages with text: {len(pages_with_text)}')
    if pages_with_text:
        for ocr in pages_with_text[:2]:
            print(f'    Page {ocr.page_id}: text_len={len(ocr.cleaned_text)}')
