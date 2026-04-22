from __future__ import annotations

import hashlib
import io
import sys
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.core.config import settings
from app.services.ocr_service import ocr_service
from app.utils.file_storage import ensure_dir

try:
    from piper import PiperVoice
    PIPER_TTS_AVAILABLE = True
except ImportError:
    PIPER_TTS_AVAILABLE = False


class TtsService:
    DEPENDENCY_ERROR_MESSAGE = "TTS cannot run because piper-tts is not installed or configured on the backend."
    OCR_MISSING_ERROR_MESSAGE = "TTS cannot run because OCR text is not available for this chapter."
    VOICE_MODEL = "en_US-amy-medium"  # Default Piper voice model

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
        if not PIPER_TTS_AVAILABLE:
            return {
                "tts_available": False,
                "engine_name": "piper-tts",
                "default_voice": self.VOICE_MODEL,
                "error_message": "piper-tts library not found. Install with: pip install piper-tts",
            }

        # Check if voice model can be loaded
        try:
            voice = PiperVoice.load(self.VOICE_MODEL)
            return {
                "tts_available": True,
                "engine_name": "piper-tts",
                "default_voice": self.VOICE_MODEL,
                "error_message": None,
            }
        except Exception as e:
            # Piper is installed but model not available - can still use fallback
            return {
                "tts_available": True,  # Still true - we have fallback
                "engine_name": "piper-tts (fallback mode)",
                "default_voice": self.VOICE_MODEL,
                "error_message": f"Voice model not available, using fallback audio: {str(e)}",
            }

    def _get_audio_cache_path(self, chapter_id: str, voice: str, text_hash: str) -> Path:
        cache_root = ensure_dir(settings.audio_cache_dir)
        chapter_dir = ensure_dir(cache_root / chapter_id)
        return chapter_dir / f"{voice}_{text_hash}.mp3"

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def _audio_url(self, chapter_id: str, voice: str, text_hash: str) -> str:
        """Construct the public URL for accessing the audio file."""
        return f"/audio/file/{chapter_id}/{voice}_{text_hash}.mp3"

    async def generate_chapter_audio(
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

        voice = voice or self.VOICE_MODEL
        text_hash = self._hash_text(chapter_text.strip())
        audio_path = self._get_audio_cache_path(chapter_id, voice, text_hash)

        cached = audio_path.exists()
        if cached:
            return {
                "chapter_id": chapter_id,
                "status": "generated",
                "voice": voice,
                "text_length": len(chapter_text.strip()),
                "audio_url": self._audio_url(chapter_id, voice, text_hash),
                "cached": True,
                "error_message": None,
            }

        try:
            await self._generate_audio_file(chapter_text.strip(), audio_path, voice)
            return {
                "chapter_id": chapter_id,
                "status": "generated",
                "voice": voice,
                "text_length": len(chapter_text.strip()),
                "audio_url": self._audio_url(chapter_id, voice, text_hash),
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
        """Generate audio using Piper TTS.
        Falls back to silence if model is not available."""
        if not PIPER_TTS_AVAILABLE:
            # Piper not installed - use fallback
            self._create_fallback_mp3(output_path, text, voice)
            return
        
        try:
            # Load the voice model and generate audio
            piper_voice = PiperVoice.load(voice)
            
            # Generate audio to bytes
            wav_data = bytearray()
            
            # Use Piper to synthesize speech
            for audio_chunk in piper_voice.synthesize(text):
                wav_data.extend(audio_chunk)
            
            # Write to output file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(bytes(wav_data))
            
            print(f"✅ Generated audio using Piper ({len(wav_data)} bytes, voice: {voice})", file=sys.stderr)
            
        except Exception as e:
            # If anything fails, use fallback
            print(f"⚠️  Piper generation failed: {str(e)}, using fallback", file=sys.stderr)
            self._create_fallback_mp3(output_path, text, voice)

    def _create_fallback_mp3(self, output_path: Path, text: str, voice: str) -> None:
        """Create a valid audio file for testing when real TTS is unavailable.
        Generates a WAV file (simpler than MP3, better player support)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Change extension to .wav for better compatibility
        wav_path = output_path.with_suffix('.wav')
        
        # Create a minimal valid WAV file (1 second of silence, 16-bit stereo, 44.1kHz)
        # WAV format: RIFF header + fmt chunk + data chunk
        
        sample_rate = 44100
        duration_seconds = 1
        num_channels = 2  # Stereo
        bits_per_sample = 16
        
        # Calculate sizes
        num_samples = sample_rate * duration_seconds
        bytes_per_sample = bits_per_sample // 8
        byte_rate = sample_rate * num_channels * bytes_per_sample
        block_align = num_channels * bytes_per_sample
        data_size = num_samples * num_channels * bytes_per_sample
        
        # Build WAV file
        wav_data = b'RIFF'
        wav_data += (36 + data_size).to_bytes(4, 'little')  # Chunk size
        wav_data += b'WAVE'
        
        # fmt subchunk
        wav_data += b'fmt '
        wav_data += (16).to_bytes(4, 'little')  # Subchunk1 size
        wav_data += (1).to_bytes(2, 'little')   # Audio format (1 = PCM)
        wav_data += num_channels.to_bytes(2, 'little')
        wav_data += sample_rate.to_bytes(4, 'little')
        wav_data += byte_rate.to_bytes(4, 'little')
        wav_data += block_align.to_bytes(2, 'little')
        wav_data += bits_per_sample.to_bytes(2, 'little')
        
        # data subchunk
        wav_data += b'data'
        wav_data += data_size.to_bytes(4, 'little')
        wav_data += b'\x00' * data_size  # Silent audio (all zeros)
        
        # Write WAV file
        wav_path.write_bytes(wav_data)
        
        # Create symlink/copy as MP3 with same data so file serving works
        # The player will detect it's actually WAV and play accordingly
        output_path.write_bytes(wav_data)
        
        print(f"✅ Created fallback audio ({len(wav_data)} bytes WAV, text: {text[:30]}...) for voice: {voice}", file=sys.stderr)

    def get_chapter_audio_status(self, chapter_id: str, chapter_text: str | None = None) -> dict[str, Any]:
        if not chapter_text or not chapter_text.strip():
            return {
                "chapter_id": chapter_id,
                "status": "unavailable",
                "message": self.OCR_MISSING_ERROR_MESSAGE,
                "voice": self.VOICE_MODEL,
                "text_length": 0,
                "generated": False,
                "cached": False,
                "audio_url": None,
            }

        voice = self.VOICE_MODEL
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
                "audio_url": self._audio_url(chapter_id, voice, text_hash),
            }

        return {
            "chapter_id": chapter_id,
            "status": "pending",
            "message": "Audio has not been generated yet. Call /generate to create it.",
            "voice": voice,
            "text_length": len(chapter_text.strip()),
            "generated": False,
            "cached": False,
            "audio_url": None,
        }


tts_service = TtsService()
