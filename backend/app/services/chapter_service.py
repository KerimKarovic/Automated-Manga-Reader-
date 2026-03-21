from sqlalchemy.orm import Session

from app.db import models


class ChapterService:
    def get_chapter(self, chapter_id: str, db: Session) -> models.Chapter | None:
        return db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()

    def list_chapters_for_manga(self, manga_id: int, db: Session) -> list[models.Chapter]:
        return (
            db.query(models.Chapter)
            .filter(models.Chapter.manga_id == manga_id)
            .order_by(models.Chapter.chapter_number.asc().nullslast(), models.Chapter.created_at.asc())
            .all()
        )


chapter_service = ChapterService()
