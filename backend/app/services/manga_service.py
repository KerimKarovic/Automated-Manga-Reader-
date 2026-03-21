from sqlalchemy.orm import Session

from app.db import models
from app.db.schemas import MangaCreate


class MangaService:
    def list_manga(self, db: Session) -> list[models.Manga]:
        return db.query(models.Manga).order_by(models.Manga.created_at.desc()).all()

    def get_manga(self, manga_id: int, db: Session) -> models.Manga | None:
        return db.query(models.Manga).filter(models.Manga.id == manga_id).first()

    def get_by_mangadex_id(self, mangadex_id: str, db: Session) -> models.Manga | None:
        return db.query(models.Manga).filter(models.Manga.mangadex_id == mangadex_id).first()

    def create_manga(self, payload: MangaCreate, db: Session) -> models.Manga:
        manga = models.Manga(
            title=payload.title,
            author=payload.author,
            mangadex_id=payload.mangadex_id,
            cover_url=payload.cover_url,
            description=payload.description,
            status=payload.status,
        )
        db.add(manga)
        db.commit()
        db.refresh(manga)
        return manga


manga_service = MangaService()
