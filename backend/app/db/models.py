from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Manga(Base):
    __tablename__ = "manga"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mangadex_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chapters: Mapped[list["Chapter"]] = relationship("Chapter", back_populates="manga", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("manga.id", ondelete="CASCADE"), nullable=False, index=True)
    volume: Mapped[str | None] = mapped_column(String(32), nullable=True)
    chapter_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    translated_language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    chapter_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    manga: Mapped[Manga] = relationship("Manga", back_populates="chapters")
    pages: Mapped[list["Page"]] = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "page"
    __table_args__ = (
        UniqueConstraint("chapter_id", "page_number", name="uq_page_chapter_page_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    quality: Mapped[str] = mapped_column(String(16), nullable=False, default="data")
    local_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chapter: Mapped[Chapter] = relationship("Chapter", back_populates="pages")
    panels: Mapped[list["Panel"]] = relationship("Panel", back_populates="page", cascade="all, delete-orphan")
    analyses: Mapped[list["PageAnalysis"]] = relationship("PageAnalysis", back_populates="page", cascade="all, delete-orphan")


class Panel(Base):
    __tablename__ = "panel"
    __table_args__ = (
        UniqueConstraint("page_id", "panel_index", name="uq_panel_page_index"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"), nullable=False, index=True)
    panel_index: Mapped[int] = mapped_column(Integer, nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    page: Mapped[Page] = relationship("Page", back_populates="panels")


class PageAnalysis(Base):
    __tablename__ = "page_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="none")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    page: Mapped[Page] = relationship("Page", back_populates="analyses")
