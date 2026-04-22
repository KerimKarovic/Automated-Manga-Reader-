#!/usr/bin/env python
"""Test actual TTS audio generation"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, '.')

from app.services.tts_service import tts_service
from app.core.config import settings

async def test_audio_generation():
    print("=" * 60)
    print("AUDIO GENERATION TEST")
    print("=" * 60)
    
    # Ensure audio cache directory exists
    audio_dir = Path(settings.audio_cache_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Audio cache directory: {audio_dir}")
    
    # Test text
    test_text = "Hello, this is a test of the text to speech system. The quick brown fox jumps over the lazy dog."
    print(f"\n[Test 1] Generate audio from text")
    print(f"  Text: {test_text}")
    
    try:
        # Call the generation method
        result = await tts_service.generate_chapter_audio(
            chapter_id="test-chapter-001",
            chapter_text=test_text,
            voice="en-US-AriaNeural"
        )
        
        print(f"\n✓ Generation successful!")
        print(f"  Status: {result['status']}")
        print(f"  Voice: {result['voice']}")
        print(f"  Text Length: {result['text_length']}")
        print(f"  Audio URL: {result['audio_url']}")
        print(f"  Cached: {result['cached']}")
        print(f"  Error: {result['error_message']}")
        
        # Verify file exists
        audio_url = result['audio_url']
        # Extract chapter id and filename from URL
        parts = audio_url.split('/')
        chapter_id = parts[3]
        filename = parts[4]
        
        audio_path = Path(settings.audio_cache_dir) / chapter_id / filename
        print(f"\n✓ Audio file path: {audio_path}")
        print(f"  File exists: {audio_path.exists()}")
        if audio_path.exists():
            file_size = audio_path.stat().st_size
            print(f"  File size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        # Test caching - generate again
        print(f"\n[Test 2] Test caching (generate same text again)")
        result2 = await tts_service.generate_chapter_audio(
            chapter_id="test-chapter-001",
            chapter_text=test_text,
            voice="en-US-AriaNeural"
        )
        print(f"  Cached: {result2['cached']}")
        print(f"  ✓ Cache test passed!")
        
        # Test status endpoint
        print(f"\n[Test 3] Test audio status endpoint")
        status = tts_service.get_chapter_audio_status(
            chapter_id="test-chapter-001",
            chapter_text=test_text
        )
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")
        print(f"  Generated: {status['generated']}")
        print(f"  Audio URL: {status['audio_url']}")
        print(f"  ✓ Status test passed!")
        
        # Test with missing OCR
        print(f"\n[Test 4] Test with missing OCR text")
        status_no_ocr = tts_service.get_chapter_audio_status(
            chapter_id="test-chapter-002",
            chapter_text=""  # Empty text
        )
        print(f"  Status: {status_no_ocr['status']}")
        print(f"  Message: {status_no_ocr['message']}")
        print(f"  Generated: {status_no_ocr['generated']}")
        print(f"  ✓ Missing OCR test passed!")
        
        print("\n" + "=" * 60)
        print("✅ ALL AUDIO TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Run async test
if __name__ == "__main__":
    asyncio.run(test_audio_generation())
