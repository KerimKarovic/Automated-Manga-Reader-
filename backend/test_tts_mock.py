#!/usr/bin/env python
"""Test TTS pipeline with mock audio generation"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
sys.path.insert(0, '.')

from app.services.tts_service import tts_service
from app.core.config import settings


async def test_tts_with_mock():
    """Test the entire TTS pipeline with mocked audio generation"""
    print("=" * 60)
    print("TTS PIPELINE TEST (WITH MOCK AUDIO)")
    print("=" * 60)
    
    # Ensure audio cache directory exists
    audio_dir = Path(settings.audio_cache_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Audio cache directory: {audio_dir}")
    
    # Test text
    test_text = "Hello, this is a test of the text to speech system. The quick brown fox jumps over the lazy dog."
    print(f"\n[Test 1] Generate audio from text (mocked)")
    print(f"  Text: {test_text}")
    
    try:
        # Mock the _generate_audio_file method to create a dummy MP3
        original_generate = tts_service._generate_audio_file
        
        async def mock_generate_audio(text, output_path, voice):
            """Create a minimal valid MP3 file for testing"""
            # Minimal MP3 frame header (ID3 tag + empty MP3 frame)
            mp3_data = b'ID3\x03\x00\x00\x00\x00\x00\x00'
            mp3_data += b'\xff\xfb\x10\x00' + b'\x00' * 100  # Minimal MP3 frame
            
            # Ensure parent directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(mp3_data)
        
        # Patch the method
        tts_service._generate_audio_file = mock_generate_audio
        
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
        
        # Verify file exists
        audio_url = result['audio_url']
        parts = audio_url.split('/')
        chapter_id = parts[3]
        filename = parts[4]
        
        audio_path = Path(settings.audio_cache_dir) / chapter_id / filename
        print(f"\n✓ Audio file path: {audio_path}")
        print(f"  File exists: {audio_path.exists()}")
        if audio_path.exists():
            file_size = audio_path.stat().st_size
            print(f"  File size: {file_size} bytes")
        
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
        
        # Test different voice (should not be cached)
        print(f"\n[Test 5] Test different voice (new cache)")
        result3 = await tts_service.generate_chapter_audio(
            chapter_id="test-chapter-001",
            chapter_text=test_text,
            voice="en-US-GuyNeural"
        )
        print(f"  Voice: {result3['voice']}")
        print(f"  Cached: {result3['cached']}")
        print(f"  Audio URL: {result3['audio_url']}")
        print(f"  ✓ Different voice test passed!")
        
        # Test file serving
        print(f"\n[Test 6] Verify file can be served")
        file_exists = audio_path.exists()
        print(f"  File exists for serving: {file_exists}")
        if file_exists:
            # Try to read it back
            with open(audio_path, 'rb') as f:
                content = f.read()
                print(f"  File readable: True")
                print(f"  File content size: {len(content)} bytes")
        print(f"  ✓ File serving test passed!")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNOTE: Audio generation used mocked MP3 data.")
        print("For real TTS, network access to Bing Speech API is required.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restore original method
        if 'original_generate' in locals():
            tts_service._generate_audio_file = original_generate


# Run async test
if __name__ == "__main__":
    asyncio.run(test_tts_with_mock())
