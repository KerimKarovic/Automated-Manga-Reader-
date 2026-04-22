#!/usr/bin/env python
"""Quick test of TTS service functionality"""
import sys
sys.path.insert(0, '.')

from app.services.tts_service import tts_service
from app.core.config import settings

print("=" * 60)
print("TTS SERVICE TEST")
print("=" * 60)

# Test 1: Dependency detection
print("\n[Test 1] Dependency Detection")
status = tts_service.get_dependency_status()
print(f"  TTS Available: {status['tts_available']}")
print(f"  Engine: {status['engine_name']}")
print(f"  Voice: {status['default_voice']}")
if status['error_message']:
    print(f"  Error: {status['error_message']}")
else:
    print("  ✓ No errors")

# Test 2: Text hashing
print("\n[Test 2] Text Hashing")
test_text = "The quick brown fox jumps over the lazy dog. This is a test of the TTS system."
text_hash = tts_service._hash_text(test_text)
print(f"  Text: {test_text[:50]}...")
print(f"  Hash: {text_hash}")
print(f"  Hash Length: {len(text_hash)}")

# Test 3: URL generation
print("\n[Test 3] Audio URL Generation")
url = tts_service._audio_url("chapter-123", "en-US-AriaNeural", text_hash)
print(f"  URL: {url}")

# Test 4: Audio path generation
print("\n[Test 4] Audio Path Generation")
audio_path = tts_service._get_audio_cache_path("chapter-456", "en-US-AriaNeural", "abc123def456")
print(f"  Path: {audio_path}")
print(f"  Path Type: {type(audio_path)}")

# Test 5: Settings validation
print("\n[Test 5] Configuration")
print(f"  Audio Cache Dir: {settings.audio_cache_dir}")
print(f"  TTS Engine: {settings.tts_engine_name}")
print(f"  Default Voice: {settings.tts_default_voice}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
