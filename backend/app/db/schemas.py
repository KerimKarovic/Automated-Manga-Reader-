from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class MangaCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str | None = None
    mangadex_id: str | None = None
    cover_url: str | None = None
    description: str | None = None
    status: str | None = None


class MangaOut(BaseModel):
    id: int
    title: str
    author: str | None
    mangadex_id: str | None
    cover_url: str | None
    description: str | None
    status: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterOut(BaseModel):
    id: str
    manga_id: int
    volume: str | None
    chapter_number: str | None
    title: str | None
    translated_language: str | None
    chapter_hash: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PageOut(BaseModel):
    id: int
    chapter_id: str
    page_number: int
    image_url: str
    quality: str
    local_image_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MangadexMangaSummary(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str | None = None
    cover_url: str | None = None


class MangadexChapterSummary(BaseModel):
    id: str
    volume: str | None = None
    chapter_number: str | None = None
    title: str | None = None
    translated_language: str | None = None


class ChapterImagesResponse(BaseModel):
    chapter_id: str
    quality: str
    chapter_hash: str
    image_urls: list[str]


class StoreChapterResponse(BaseModel):
    chapter_id: str
    manga_id: int
    created_chapter: bool
    pages_created: int
    total_pages: int


class PanelOut(BaseModel):
    id: int
    panel_index: int
    x: int
    y: int
    width: int
    height: int
    extracted_text: str | None
    reading_order: int | None

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    page_id: int
    analysis_id: int
    status: str
    source: str
    panel_count: int


class AudioResponse(BaseModel):
    chapter_id: str
    status: str
    message: str
