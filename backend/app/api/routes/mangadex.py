from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import get_db
from app.db.schemas import ChapterImagesResponse, MangadexChapterSummary, MangadexMangaSummary, StoreChapterResponse
from app.services.mangadex_service import mangadex_service
from app.services.manga_service import manga_service

router = APIRouter(prefix="/mangadex", tags=["mangadex"])


@router.get("/search", response_model=list[MangadexMangaSummary])
def search_manga(title: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)) -> list[MangadexMangaSummary]:
    return [MangadexMangaSummary(**entry) for entry in mangadex_service.search_manga(title=title, limit=limit)]


@router.get("/{manga_id}/chapters", response_model=list[MangadexChapterSummary])
def chapter_feed(manga_id: str, language: str = Query("en", min_length=2, max_length=8)) -> list[MangadexChapterSummary]:
    feed = mangadex_service.get_chapter_feed(manga_id=manga_id, language=language)
    return [MangadexChapterSummary(**item) for item in feed]


@router.get("/chapter/{chapter_id}/images", response_model=ChapterImagesResponse)
def chapter_images(chapter_id: str, quality: str = Query("data")) -> ChapterImagesResponse:
    payload = mangadex_service.get_chapter_images(chapter_id=chapter_id, quality=quality)
    return ChapterImagesResponse(**payload)


@router.post("/store-chapter/{chapter_id}", response_model=StoreChapterResponse)
def store_chapter(chapter_id: str, quality: str = Query("data"), db: Session = Depends(get_db)) -> StoreChapterResponse:
    chapter_metadata = mangadex_service.get_chapter_metadata(chapter_id)
    chapter_data = chapter_metadata.get("data", {})
    if not chapter_data:
        raise HTTPException(status_code=404, detail={"message": "Chapter metadata not found"})

    relationships = chapter_data.get("relationships", [])
    manga_rel = next((rel for rel in relationships if rel.get("type") == "manga"), None)
    if not manga_rel:
        raise HTTPException(status_code=404, detail={"message": "Manga relationship not found for chapter"})

    mangadex_manga_id = manga_rel.get("id")
    manga = manga_service.get_by_mangadex_id(mangadex_manga_id, db)
    if not manga:
        manga_payload = mangadex_service.get_manga(mangadex_manga_id)
        manga_data = manga_payload.get("data", {})
        attrs = manga_data.get("attributes", {})
        title_map = attrs.get("title", {})
        description_map = attrs.get("description", {})

        manga = models.Manga(
            title=title_map.get("en") or next(iter(title_map.values()), "Unknown"),
            author=None,
            mangadex_id=mangadex_manga_id,
            description=description_map.get("en") or next(iter(description_map.values()), None),
            status=attrs.get("status"),
            cover_url=None,
        )
        db.add(manga)
        db.commit()
        db.refresh(manga)

    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    created_chapter = False
    if not chapter:
        attrs = chapter_data.get("attributes", {})
        chapter_images_payload = mangadex_service.get_chapter_images(chapter_id=chapter_id, quality="data")
        chapter = models.Chapter(
            id=chapter_id,
            manga_id=manga.id,
            volume=attrs.get("volume"),
            chapter_number=attrs.get("chapter"),
            title=attrs.get("title"),
            translated_language=attrs.get("translatedLanguage"),
            chapter_hash=chapter_images_payload["chapter_hash"],
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        created_chapter = True

    chapter_images_payload = mangadex_service.get_chapter_images(chapter_id=chapter_id, quality=quality)
    image_urls = chapter_images_payload["image_urls"]

    existing_by_page = {
        page.page_number: page
        for page in db.query(models.Page).filter(models.Page.chapter_id == chapter_id).all()
    }

    pages_created = 0
    for index, image_url in enumerate(image_urls, start=1):
        if index in existing_by_page:
            existing_page = existing_by_page[index]
            if existing_page.image_url != image_url or existing_page.quality != quality:
                existing_page.image_url = image_url
                existing_page.quality = quality
            continue

        db.add(
            models.Page(
                chapter_id=chapter_id,
                page_number=index,
                image_url=image_url,
                quality=quality,
                local_image_path=None,
            )
        )
        pages_created += 1

    db.commit()

    total_pages = db.query(models.Page).filter(models.Page.chapter_id == chapter_id).count()

    return StoreChapterResponse(
        chapter_id=chapter_id,
        manga_id=manga.id,
        created_chapter=created_chapter,
        pages_created=pages_created,
        total_pages=total_pages,
    )
