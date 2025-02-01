from sqlalchemy import Column, Integer, String
from app.database import Base

class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)

    # Add additional fields later (e.g., description, cover_image, etc.)
