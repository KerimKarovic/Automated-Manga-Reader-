from fastapi import APIRouter

from app.core.config import settings
from app.db.schemas import DependencyHealthResponse, HealthResponse, TtsHealthResponse
from app.services.ocr_service import ocr_service
from app.services.tts_service import tts_service

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get("/health/dependencies", response_model=DependencyHealthResponse)
def dependency_health_check() -> DependencyHealthResponse:
    return DependencyHealthResponse(**ocr_service.get_dependency_status())


@router.get("/health/tts", response_model=TtsHealthResponse)
def tts_health_check() -> TtsHealthResponse:
    return TtsHealthResponse(**tts_service.get_dependency_status())
