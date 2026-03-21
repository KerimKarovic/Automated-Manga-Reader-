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

    return page_service.list_pages_for_chapter(chapter_id=chapter_id, db=db)
