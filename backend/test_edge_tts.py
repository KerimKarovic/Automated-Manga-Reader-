#!/usr/bin/env python3
"""Test edge-tts audio generation"""

import asyncio
import os
from pathlib import Path

async def test_tts():
    try:
        import edge_tts
    except ImportError:
        print("❌ edge-tts not installed")
        return
    
    test_file = Path("test_audio.mp3")
    text = "Hello, this is a test of the text to speech system."
    voice = "en-US-AriaNeural"
    
    print(f"Testing edge-tts with text: '{text}'")
    print(f"Voice: {voice}")
    print(f"Output: {test_file}")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(test_file))
        
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"✅ Audio file created: {size} bytes")
            if size > 0:
                print("✅ File has content - TTS is working!")
            else:
                print("❌ File is empty - TTS returned no data")
                print("   This likely means Bing Speech API call failed")
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
            print("Cleaned up test file")

if __name__ == "__main__":
    asyncio.run(test_tts())
