from fastapi import APIRouter

from app.core.config import settings
from app.db.schemas import DependencyHealthResponse, HealthResponse
from app.services.ocr_service import ocr_service

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get("/health/dependencies", response_model=DependencyHealthResponse)
def dependency_health_check() -> DependencyHealthResponse:
    return DependencyHealthResponse(**ocr_service.get_dependency_status())
