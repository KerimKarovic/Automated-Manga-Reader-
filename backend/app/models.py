# backend/app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    # New column for the external MangaDex ID.
    mangadexId = Column(String, nullable=True)
    
    # Relationship: one manga can have many chapters.
    chapters = relationship("Chapter", back_populates="manga")

class Chapter(Base):
    __tablename__ = "chapter"

    # We use the MangaDex chapter ID (UUID string) as the primary key.
    id = Column(String, primary_key=True, index=True)
    manga_id = Column(Integer, ForeignKey("manga.id"))
    volume = Column(String, nullable=True)
    chapter_number = Column(String, nullable=True)
    title = Column(String, nullable=True)
    translated_language = Column(String, nullable=False)
    chapter_hash = Column(String, nullable=False)  # Used for constructing image URLs

    # Relationship: one chapter can have many pages.
    pages = relationship("Page", back_populates="chapter")
    manga = relationship("Manga", back_populates="chapters")

class Page(Base):
    __tablename__ = "page"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(String, ForeignKey("chapter.id"))
    image_url = Column(String, nullable=False)
    quality = Column(String, nullable=False)  # e.g., "data" or "data-saver"
    page_number = Column(Integer)

    chapter = relationship("Chapter", back_populates="pages")
