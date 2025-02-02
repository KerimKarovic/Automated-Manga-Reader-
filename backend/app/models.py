# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Manga(Base):
    __tablename__ = "manga"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    comment_thread_id = Column(Integer, nullable=True)
    replies_count = Column(Integer, nullable=True)
    
    # Relationship to chapters
    chapters = relationship("Chapter", back_populates="manga")

class Chapter(Base):
    __tablename__ = "chapter"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    number = Column(Integer)
    manga_id = Column(Integer, ForeignKey("manga.id"))
    
    # Relationship to the parent manga and its pages
    manga = relationship("Manga", back_populates="chapters")
    pages = relationship("Page", back_populates="chapter")

class Page(Base):
    __tablename__ = "page"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapter.id"))
    image_url = Column(String)
    
    # Relationship to the chapter
    chapter = relationship("Chapter", back_populates="pages")
