from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import cv2
import httpx
import numpy as np
import pytesseract
from fastapi import HTTPException
from pytesseract.pytesseract import TesseractNotFoundError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import models
from app.services.chapter_service import chapter_service
from app.services.page_service import page_service
from app.utils.file_storage import ensure_dir


class OcrService:
    VALID_STATUSES = {"pending", "processing", "completed", "failed"}
    DEPENDENCY_ERROR_MESSAGE = "OCR cannot run because Tesseract OCR is not installed/configured on the backend."

    def __init__(self) -> None:
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        self._dependency_status = self._detect_tesseract_dependency()

    def refresh_dependency_status(self) -> dict[str, Any]:
        self._dependency_status = self._detect_tesseract_dependency()
        return dict(self._dependency_status)

    def get_dependency_status(self) -> dict[str, Any]:
        return dict(self._dependency_status)

    def ensure_tesseract_available(self) -> None:
        dependency_status = self.get_dependency_status()
        if dependency_status["tesseract_available"]:
            return

        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "dependency_unavailable",
                "dependency": "tesseract",
                "message": self.DEPENDENCY_ERROR_MESSAGE,
                **dependency_status,
            },
        )

    def run_page_ocr(self, page_id: int, db: Session) -> models.PageOCR:
        self.ensure_tesseract_available()
        page = page_service.get_page(page_id=page_id, db=db)
        if not page:
            raise HTTPException(status_code=404, detail={"message": "Page not found"})

        ocr = db.query(models.PageOCR).filter(models.PageOCR.page_id == page.id).first()
        if not ocr:
            ocr = models.PageOCR(page_id=page.id, status="pending", engine_name=settings.ocr_engine_name)
            db.add(ocr)
            db.commit()
            db.refresh(ocr)

        ocr.status = "processing"
        ocr.error_message = None
        db.commit()

        try:
            image_path = self._resolve_local_image(page=page, db=db)
            raw_text = self._extract_raw_text_from_image(image_path=image_path)
            cleaned_text = self._normalize_text(raw_text)

            ocr.status = "completed"
            ocr.raw_text = raw_text
            ocr.cleaned_text = cleaned_text
            ocr.engine_name = settings.ocr_engine_name
            ocr.error_message = None
            db.commit()
            db.refresh(ocr)
            return ocr
        except HTTPException as exc:
            ocr.status = "failed"
            ocr.raw_text = None
            ocr.cleaned_text = None
            ocr.engine_name = settings.ocr_engine_name
            error_message = "Unable to resolve image for OCR"
            if isinstance(exc.detail, dict):
                error_message = exc.detail.get("message", error_message)
            elif isinstance(exc.detail, str):
                error_message = exc.detail
            ocr.error_message = error_message
            db.commit()
            db.refresh(ocr)
            return ocr
        except Exception as exc:
            ocr.status = "failed"
            ocr.raw_text = None
            ocr.cleaned_text = None
            ocr.engine_name = settings.ocr_engine_name
            ocr.error_message = str(exc)
            db.commit()
            db.refresh(ocr)
            return ocr

    def run_chapter_ocr(self, chapter_id: str, db: Session) -> dict[str, int]:
        self.ensure_tesseract_available()
        chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
        if not chapter:
            raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

        pages = page_service.list_pages_for_chapter(chapter_id=chapter_id, db=db)
        pages_processed = 0
        success_count = 0
        failure_count = 0

        for page in pages:
            pages_processed += 1
            result = self.run_page_ocr(page_id=page.id, db=db)
            if result.status == "completed":
                success_count += 1
            elif result.status == "failed":
                failure_count += 1

        return {
            "chapter_id": chapter_id,
            "pages_processed": pages_processed,
            "success_count": success_count,
            "failure_count": failure_count,
            "completed_count": success_count,
        }

    def get_page_ocr(self, page_id: int, db: Session) -> tuple[models.Page, models.PageOCR | None]:
        page = page_service.get_page(page_id=page_id, db=db)
        if not page:
            raise HTTPException(status_code=404, detail={"message": "Page not found"})

        ocr = db.query(models.PageOCR).filter(models.PageOCR.page_id == page.id).first()
        return page, ocr

    def get_chapter_ocr(self, chapter_id: str, db: Session) -> dict:
        chapter = chapter_service.get_chapter(chapter_id=chapter_id, db=db)
        if not chapter:
            raise HTTPException(status_code=404, detail={"message": "Chapter not found"})

        pages = page_service.list_pages_for_chapter(chapter_id=chapter_id, db=db)
        page_ids = [page.id for page in pages]
        ocr_by_page_id = {
            ocr.page_id: ocr
            for ocr in db.query(models.PageOCR).filter(models.PageOCR.page_id.in_(page_ids)).all()
        } if page_ids else {}

        page_results: list[dict] = []
        chapter_parts: list[str] = []
        completed_count = 0
        failed_count = 0
        processing_count = 0
        pending_count = 0

        for page in pages:
            ocr = ocr_by_page_id.get(page.id)
            status = ocr.status if ocr else "pending"
            cleaned_text = ocr.cleaned_text if ocr else None
            raw_text = ocr.raw_text if ocr else None
            engine_name = ocr.engine_name if ocr else settings.ocr_engine_name
            error_message = ocr.error_message if ocr else None

            if status == "completed":
                completed_count += 1
                if cleaned_text and cleaned_text.strip():
                    chapter_parts.append(cleaned_text.strip())
            elif status == "failed":
                failed_count += 1
            elif status == "processing":
                processing_count += 1
            else:
                pending_count += 1

            text_length = len((cleaned_text or "").strip())
            page_results.append(
                {
                    "page_id": page.id,
                    "page_number": page.page_number,
                    "status": status,
                    "engine_name": engine_name,
                    "raw_text": raw_text,
                    "cleaned_text": cleaned_text,
                    "text_length": text_length,
                    "error_message": error_message,
                }
            )

        chapter_text = "\n\n".join(chapter_parts).strip()
        overall_status = "completed"
        if failed_count > 0 and completed_count == 0:
            overall_status = "failed"
        elif processing_count > 0:
            overall_status = "processing"
        elif pending_count > 0 and completed_count == 0:
            overall_status = "pending"
        elif pending_count > 0 or failed_count > 0:
            overall_status = "partial"

        return {
            "chapter_id": chapter_id,
            "status": overall_status,
            "pages_total": len(pages),
            "completed_count": completed_count,
            "failed_count": failed_count,
            "processing_count": processing_count,
            "pending_count": pending_count,
            "chapter_text": chapter_text,
            "chapter_text_length": len(chapter_text),
            "page_results": page_results,
        }

    def get_chapter_combined_text(self, chapter_id: str, db: Session) -> str:
        chapter_ocr = self.get_chapter_ocr(chapter_id=chapter_id, db=db)
        return chapter_ocr["chapter_text"]

    def _resolve_local_image(self, page: models.Page, db: Session) -> Path:
        if page.local_image_path:
            local_path = Path(page.local_image_path)
            if local_path.exists() and local_path.is_file():
                return local_path

        cache_root = ensure_dir(settings.page_cache_dir)
        chapter_dir = ensure_dir(cache_root / page.chapter_id)
        extension = self._guess_image_extension(page.image_url)
        local_path = chapter_dir / f"{page.page_number:04d}{extension}"

        if local_path.exists() and local_path.is_file():
            page.local_image_path = str(local_path)
            db.commit()
            return local_path

        try:
            with httpx.Client(timeout=max(settings.request_timeout_seconds, 30)) as client:
                response = client.get(page.image_url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail={"message": "Failed to download page image", "error": str(exc)}) from exc

        local_path.write_bytes(response.content)
        page.local_image_path = str(local_path)
        db.commit()
        return local_path

    def _extract_raw_text_from_image(self, image_path: Path) -> str:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Unable to load image for OCR: {image_path}")

        processed = self._preprocess_image(image)
        # Use PSM 6 (assume single block of text) for better manga text recognition
        custom_config = r'--psm 6 --oem 3'
        raw_text = pytesseract.image_to_string(processed, config=custom_config)
        return raw_text or ""

    def _detect_tesseract_dependency(self) -> dict[str, Any]:
        tesseract_cmd = str(pytesseract.pytesseract.tesseract_cmd)

        try:
            pytesseract.get_tesseract_version()
            return {
                "tesseract_available": True,
                "tesseract_cmd": tesseract_cmd,
                "error_message": None,
            }
        except TesseractNotFoundError as exc:
            return {
                "tesseract_available": False,
                "tesseract_cmd": tesseract_cmd,
                "error_message": str(exc),
            }
        except Exception as exc:
            return {
                "tesseract_available": False,
                "tesseract_cmd": tesseract_cmd,
                "error_message": f"Unexpected Tesseract validation error: {exc}",
            }

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Advanced preprocessing for manga OCR with improved text clarity."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Deskew the image to handle rotated text
        gray = self._deskew_image(gray)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply Gaussian blur to reduce noise
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Apply bilateral filter to preserve edges while reducing noise
        bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        # Adaptive thresholding for better text/background separation
        thresholded = cv2.adaptiveThreshold(
            bilateral,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  # Reduced block size for better small text detection
            2,   # Reduced constant for better sensitivity
        )
        
        # Upscale small images more aggressively for better OCR
        height, width = thresholded.shape
        if max(height, width) < 1400:
            scale_factor = max(2.0, 2000 / max(height, width))  # Scale to at least 2000px
            thresholded = cv2.resize(thresholded, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        return thresholded
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Deskew image to correct rotation for better OCR."""
        try:
            # Calculate image moments
            coords = np.column_stack(np.where(image > 0))
            if len(coords) < 4:
                return image
            
            # Fit line to the white pixels
            angle = cv2.fitLine(coords, cv2.DIST_L2, 0, 0.01, 0.01)
            angle_rad = np.arctan2(angle[1], angle[0])
            angle_deg = np.degrees(angle_rad)
            
            # Only correct if angle is significant (> 0.5 degrees)
            if abs(angle_deg) > 0.5:
                h, w = image.shape
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
                rotated = cv2.warpAffine(image, rotation_matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
                return rotated
        except Exception:
            pass
        
        return image

    def _normalize_text(self, text: str) -> str:
        """Normalize OCR text with encoding cleanup and mojibake detection."""
        if not text:
            return ""

        # Fix line endings
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Clean up encoding issues (mojibake)
        cleaned = self._cleanup_mojibake(cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        
        # Normalize multiple newlines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        
        # Remove trailing spaces before newlines
        cleaned = re.sub(r"[^\S\n]+\n", "\n", cleaned)
        
        # Process lines
        lines = [line.strip() for line in cleaned.split("\n")]
        
        # Filter out lines that are mostly symbols or gibberish
        non_empty_lines = [line for line in lines if self._is_valid_text_line(line)]
        
        return "\n".join(non_empty_lines).strip()
    
    def _cleanup_mojibake(self, text: str) -> str:
        """Clean up mojibake (garbled text from encoding issues)."""
        # List of common mojibake patterns to remove or fix
        mojibake_patterns = [
            (r"Â\\*", ""),  # Remove standalone Â followed by backslashes
            (r"~â", ""),     # Remove ~â pattern
            (r"[Â°]+", ""),   # Remove degree symbols
            (r"Â·", "·"),      # Fix middle dot
        ]
        
        for pattern, replacement in mojibake_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Remove control characters and other problematic Unicode
        cleaned = ""
        for char in text:
            # Keep printable ASCII, common punctuation, and valid Unicode
            try:
                if ord(char) < 32 and char not in "\n\t":
                    continue  # Skip control characters except newline and tab
                if ord(char) == 127:  # DEL character
                    continue
                # Check if it's valid Unicode
                unicodedata.category(char)
                cleaned += char
            except (ValueError, TypeError):
                continue
        
        return cleaned
    
    def _is_valid_text_line(self, line: str) -> bool:
        """Check if a line contains valid text (not just symbols/garbage)."""
        if not line:
            return False
        
        # Remove common symbols and special characters temporarily
        text_only = re.sub(r"[^a-zA-Z0-9\s]", "", line)
        
        # If there are at least 2 alphanumeric characters, consider it valid text
        if len(text_only) >= 2:
            return True
        
        # Allow single-character lines if they're letters
        if len(line) == 1 and line.isalpha():
            return True
        
        # Allow lines with punctuation if they have some alphanumeric content
        if len(text_only) == 1 and len(line) > 1:
            return True
        
        return False

    def _guess_image_extension(self, image_url: str) -> str:
        lowered = image_url.lower()
        if lowered.endswith(".png"):
            return ".png"
        if lowered.endswith(".webp"):
            return ".webp"
        return ".jpg"


ocr_service = OcrService()
