from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import MangaCreate, MangaOut
from app.services.manga_service import manga_service

router = APIRouter(prefix="/manga", tags=["manga"])


@router.get("", response_model=list[MangaOut])
def list_manga(db: Session = Depends(get_db)) -> list[MangaOut]:
    return manga_service.list_manga(db)


@router.post("", response_model=MangaOut, status_code=201)
def create_manga(payload: MangaCreate, db: Session = Depends(get_db)) -> MangaOut:
    if payload.mangadex_id:
        existing = manga_service.get_by_mangadex_id(payload.mangadex_id, db)
        if existing:
            raise HTTPException(status_code=409, detail={"message": "Manga with this mangadex_id already exists", "manga_id": existing.id})
    return manga_service.create_manga(payload=payload, db=db)


@router.get("/{manga_id}", response_model=MangaOut)
def get_manga(manga_id: int, db: Session = Depends(get_db)) -> MangaOut:
    manga = manga_service.get_manga(manga_id=manga_id, db=db)
    if not manga:
        raise HTTPException(status_code=404, detail={"message": "Manga not found"})
    return manga
