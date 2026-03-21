from sqlalchemy.orm import Session

from app.db import models


class PageService:
    def get_page(self, page_id: int, db: Session) -> models.Page | None:
        return db.query(models.Page).filter(models.Page.id == page_id).first()

    def list_pages_for_chapter(self, chapter_id: str, db: Session) -> list[models.Page]:
        return (
            db.query(models.Page)
            .filter(models.Page.chapter_id == chapter_id)
            .order_by(models.Page.page_number.asc())
            .all()
        )


page_service = PageService()
