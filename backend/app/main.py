from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.analysis import router as analysis_router
from app.api.routes.audio import router as audio_router
from app.api.routes.health import router as health_router
from app.api.routes.manga import router as manga_router
from app.api.routes.mangadex import router as mangadex_router
from app.api.routes.ocr import router as ocr_router
from app.api.routes.reader import router as reader_router
from app.core.config import settings
from app.db.database import init_db
from app.services.ocr_service import ocr_service
from app.services.tts_service import tts_service
from app.utils.file_storage import ensure_dir


app = FastAPI(title=settings.app_name, version=settings.app_version)

# Allow local Expo web/dev origins and LAN access during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:8082",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
    ],
    allow_origin_regex=r"http://192\\.168\\.\\d+\\.\\d+:\\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    ocr_service.refresh_dependency_status()
    tts_service.refresh_dependency_status()
    ensure_dir(settings.audio_cache_dir)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Automated Manga Reader API is running"}


# Mount audio storage as static files for serving MP3s
audio_path = ensure_dir(settings.audio_cache_dir)
app.mount("/audio", StaticFiles(directory=str(audio_path)), name="audio")

app.include_router(health_router)
app.include_router(manga_router)
app.include_router(mangadex_router)
app.include_router(reader_router)
app.include_router(analysis_router)
app.include_router(ocr_router)
app.include_router(audio_router)

