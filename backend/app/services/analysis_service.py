from __future__ import annotations

import tempfile
from pathlib import Path

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.ml.panel_detection import detect_panels
from app.services.page_service import page_service


class AnalysisService:
    def analyze_page(self, page_id: int, db: Session) -> tuple[models.PageAnalysis, int]:
        page = page_service.get_page(page_id=page_id, db=db)
        if not page:
            raise HTTPException(status_code=404, detail={"message": "Page not found"})

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(page.image_url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail={"message": "Failed to download page image for analysis", "error": str(exc)}) from exc

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            temp_image.write(response.content)
            temp_path = Path(temp_image.name)

        try:
            panel_boxes = detect_panels(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

        db.query(models.Panel).filter(models.Panel.page_id == page.id).delete()

        for index, box in enumerate(panel_boxes):
            x, y, width, height = box
            panel = models.Panel(
                page_id=page.id,
                panel_index=index,
                x=int(x),
                y=int(y),
                width=int(width),
                height=int(height),
                extracted_text=None,
                reading_order=index,
            )
            db.add(panel)

        analysis = models.PageAnalysis(
            page_id=page.id,
            status="completed" if panel_boxes else "no_panels_detected",
            raw_text=None,
            source="panel_detection_basic",
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis, len(panel_boxes)


analysis_service = AnalysisService()
