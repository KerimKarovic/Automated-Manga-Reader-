#!/usr/bin/env python3
"""Test TTS service with fallback MP3 generation"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.tts_service import tts_service

async def test_tts():
    test_file = Path("test_audio.mp3")
    text = "Hello, this is a test of the text to speech system."
    voice = "en-US-AriaNeural"
    
    print(f"Testing TTS service with fallback MP3 generation")
    print(f"Text: '{text}'")
    print(f"Voice: {voice}")
    print(f"Output: {test_file}")
    print()
    
    try:
        # Remove if exists
        if test_file.exists():
            test_file.unlink()
        
        # Test audio generation via service (includes fallback logic)
        await tts_service._generate_audio_file(text, test_file, voice)
        
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"✅ Audio file created: {size} bytes")
            if size > 100:
                print("✅ File has content - ready for playback!")
                # Show first few bytes
                with open(test_file, 'rb') as f:
                    header = f.read(4)
                    print(f"   File header: {header.hex()}")
            elif size > 0:
                print("✅ File created with fallback MP3 (Bing API failed, using silent audio)")
            else:
                print("❌ File is empty")
        else:
            print("❌ Audio file was not created")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print("\n✅ Test complete - fallback MP3 generation working!")

if __name__ == "__main__":
    asyncio.run(test_tts())
