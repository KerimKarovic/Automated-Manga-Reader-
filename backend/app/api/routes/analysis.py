from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import AnalysisResponse
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/page/{page_id}", response_model=AnalysisResponse)
def analyze_page(page_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    analysis, panel_count = analysis_service.analyze_page(page_id=page_id, db=db)
    return AnalysisResponse(
        page_id=analysis.page_id,
        analysis_id=analysis.id,
        status=analysis.status,
        source=analysis.source,
        panel_count=panel_count,
    )
