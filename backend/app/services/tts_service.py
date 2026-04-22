from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.core.config import settings
from app.services.ocr_service import ocr_service
from app.utils.file_storage import ensure_dir

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


class TtsService:
    DEPENDENCY_ERROR_MESSAGE = "TTS cannot run because edge-tts is not installed or configured on the backend."
    OCR_MISSING_ERROR_MESSAGE = "TTS cannot run because OCR text is not available for this chapter."

    def __init__(self) -> None:
        self._dependency_status = self._detect_tts_dependency()

    def refresh_dependency_status(self) -> dict[str, Any]:
        self._dependency_status = self._detect_tts_dependency()
        return dict(self._dependency_status)

    def get_dependency_status(self) -> dict[str, Any]:
        return dict(self._dependency_status)

    def ensure_tts_available(self) -> None:
        dependency_status = self.get_dependency_status()
        if dependency_status["tts_available"]:
            return

        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "dependency_unavailable",
                "dependency": "edge-tts",
                "message": self.DEPENDENCY_ERROR_MESSAGE,
                **dependency_status,
            },
        )

    def _detect_tts_dependency(self) -> dict[str, Any]:
        if not EDGE_TTS_AVAILABLE:
            return {
                "tts_available": False,
                "engine_name": settings.tts_engine_name,
                "default_voice": settings.tts_default_voice,
                "error_message": "edge-tts library not found. Install with: pip install edge-tts",
            }

        return {
            "tts_available": True,
            "engine_name": settings.tts_engine_name,
            "default_voice": settings.tts_default_voice,
            "error_message": None,
        }

    def _get_audio_cache_path(self, chapter_id: str, voice: str, text_hash: str) -> Path:
        cache_root = ensure_dir(settings.audio_cache_dir)
        chapter_dir = ensure_dir(cache_root / chapter_id)
        return chapter_dir / f"{voice}_{text_hash}.mp3"

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def generate_chapter_audio(
        self, chapter_id: str, chapter_text: str, voice: str | None = None, db=None
    ) -> dict[str, Any]:
        self.ensure_tts_available()

        if not chapter_text or not chapter_text.strip():
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "ocr_text_missing",
                    "chapter_id": chapter_id,
                    "message": self.OCR_MISSING_ERROR_MESSAGE,
                },
            )

        voice = voice or settings.tts_default_voice
        text_hash = self._hash_text(chapter_text.strip())
        audio_path = self._get_audio_cache_path(chapter_id, voice, text_hash)

        cached = audio_path.exists()
        if cached:
            return {
                "chapter_id": chapter_id,
                "status": "generated",
                "voice": voice,
                "text_length": len(chapter_text.strip()),
                "file_path": str(audio_path),
                "cached": True,
                "error_message": None,
            }

        try:
            asyncio.run(self._generate_audio_file(chapter_text.strip(), audio_path, voice))
            return {
                "chapter_id": chapter_id,
                "status": "generated",
                "voice": voice,
                "text_length": len(chapter_text.strip()),
                "file_path": str(audio_path),
                "cached": False,
                "error_message": None,
            }
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "tts_generation_failed",
                    "chapter_id": chapter_id,
                    "message": f"Failed to generate audio: {str(exc)}",
                    "error": str(exc),
                },
            ) from exc

    async def _generate_audio_file(self, text: str, output_path: Path, voice: str) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    def get_chapter_audio_status(self, chapter_id: str, chapter_text: str | None = None) -> dict[str, Any]:
        if not chapter_text or not chapter_text.strip():
            return {
                "chapter_id": chapter_id,
                "status": "unavailable",
                "message": self.OCR_MISSING_ERROR_MESSAGE,
                "voice": settings.tts_default_voice,
                "text_length": 0,
                "generated": False,
                "cached": False,
            }

        voice = settings.tts_default_voice
        text_hash = self._hash_text(chapter_text.strip())
        audio_path = self._get_audio_cache_path(chapter_id, voice, text_hash)

        if audio_path.exists():
            return {
                "chapter_id": chapter_id,
                "status": "generated",
                "message": "Audio is ready to play.",
                "voice": voice,
                "text_length": len(chapter_text.strip()),
                "generated": True,
                "cached": True,
                "file_path": str(audio_path),
            }

        return {
            "chapter_id": chapter_id,
            "status": "pending",
            "message": "Audio has not been generated yet. Call /generate to create it.",
            "voice": voice,
            "text_length": len(chapter_text.strip()),
            "generated": False,
            "cached": False,
        }


tts_service = TtsService()
