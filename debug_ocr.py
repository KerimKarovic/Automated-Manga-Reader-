#!/usr/bin/env python
"""Debug script to check OCR status in database"""
import sys
import os
sys.path.insert(0, 'd:\\Python Projects\\AutomatedMangaReader\\Automated-Manga-Reader-\\backend')

# Change to backend directory so relative paths work
os.chdir('d:\\Python Projects\\AutomatedMangaReader\\Automated-Manga-Reader-\\backend')

from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()
try:
    # Get all chapters with pages
    chapters = db.query(models.Chapter).order_by(models.Chapter.created_at.desc()).limit(3).all()
    
    for chapter in chapters:
        pages = db.query(models.Page).filter(models.Page.chapter_id == chapter.id).order_by(models.Page.page_number).all()
        print(f'\n=== Chapter: {chapter.id[:8]}... ===')
        print(f'Total pages: {len(pages)}\n')
        
        missing_ocr_pages = []
        for page in pages:
            ocr = db.query(models.PageOCR).filter(models.PageOCR.page_id == page.id).first()
            if ocr:
                text_len = len(ocr.cleaned_text) if ocr.cleaned_text else 0
                raw_len = len(ocr.raw_text) if ocr.raw_text else 0
                status = 'OK' if text_len > 0 else 'EMPTY'
                print(f'  Page {page.page_number:2d}: {status:6s} text_len={text_len:5d} raw_len={raw_len:5d} status={ocr.status}')
                if text_len == 0:
                    missing_ocr_pages.append(page.page_number)
            else:
                print(f'  Page {page.page_number:2d}: NO_RECORD')
                missing_ocr_pages.append(page.page_number)
        
        if missing_ocr_pages:
            print(f'\n⚠️  Pages WITHOUT OCR text: {missing_ocr_pages}')
        else:
            print(f'\n✅ All pages have OCR text')
finally:
    db.close()
