from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import OcrChapterResultResponse, OcrChapterRunResponse, OcrPageResult, OcrPageRunResponse
from app.services.ocr_service import ocr_service

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/page/{page_id}", response_model=OcrPageRunResponse)
def ocr_page(page_id: int, db: Session = Depends(get_db)) -> OcrPageRunResponse:
    ocr = ocr_service.run_page_ocr(page_id=page_id, db=db)
    page, _ = ocr_service.get_page_ocr(page_id=page_id, db=db)
    text_length = len((ocr.cleaned_text or "").strip())
    return OcrPageRunResponse(
        page_id=page_id,
        chapter_id=page.chapter_id,
        status=ocr.status,
        text_length=text_length,
        engine_name=ocr.engine_name,
        error_message=ocr.error_message,
    )


@router.post("/chapter/{chapter_id}", response_model=OcrChapterRunResponse)
def ocr_chapter(chapter_id: str, db: Session = Depends(get_db)) -> OcrChapterRunResponse:
    result = ocr_service.run_chapter_ocr(chapter_id=chapter_id, db=db)
    return OcrChapterRunResponse(**result)


@router.get("/page/{page_id}", response_model=OcrPageResult)
def get_page_ocr(page_id: int, db: Session = Depends(get_db)) -> OcrPageResult:
    page, ocr = ocr_service.get_page_ocr(page_id=page_id, db=db)

    if not ocr:
        return OcrPageResult(
            page_id=page.id,
            page_number=page.page_number,
            status="pending",
            engine_name="pytesseract",
            raw_text=None,
            cleaned_text=None,
            text_length=0,
            error_message=None,
        )

    cleaned_text = ocr.cleaned_text or ""
    return OcrPageResult(
        page_id=page.id,
        page_number=page.page_number,
        status=ocr.status,
        engine_name=ocr.engine_name,
        raw_text=ocr.raw_text,
        cleaned_text=ocr.cleaned_text,
        text_length=len(cleaned_text.strip()),
        error_message=ocr.error_message,
    )


@router.get("/chapter/{chapter_id}", response_model=OcrChapterResultResponse)
def get_chapter_ocr(chapter_id: str, db: Session = Depends(get_db)) -> OcrChapterResultResponse:
    result = ocr_service.get_chapter_ocr(chapter_id=chapter_id, db=db)
    return OcrChapterResultResponse(**result)
