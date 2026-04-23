from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import ChapterOut, PageOut
from app.services.chapter_service import chapter_service
from app.services.page_service import page_service

router = APIRouter(tags=["reader"])


@router.get("/chapters/{chapter_id}", response_model=ChapterOut)
def get_chapter(chapter_id: str, db: Session = Depends(get_db)) -> ChapterOut:
    chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
    if not chapter:
        raise HTTPException(status_code=404, detail={"message": "Chapter not found"})
    return chapter


@router.get("/chapters/{chapter_id}/pages", response_model=list[PageOut])
def get_chapter_pages(chapter_id: str, db: Session = Depends(get_db)) -> list[PageOut]:
    chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
    if not chapter:
        raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

    pages = page_service.list_pages_for_chapter(chapter_id=chapter_id, db=db)
    
    # Map pages to PageOut and include OCR text from relationship
    result = []
    for page in pages:
        page_dict = {
            "id": page.id,
            "chapter_id": page.chapter_id,
            "page_number": page.page_number,
            "image_url": page.image_url,
            "quality": page.quality,
            "local_image_path": page.local_image_path,
            "created_at": page.created_at,
            "ocr_text": page.ocr_result.cleaned_text if page.ocr_result else None
        }
        result.append(PageOut(**page_dict))
    
    return result
