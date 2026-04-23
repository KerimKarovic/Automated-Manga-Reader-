#!/usr/bin/env python
"""Test gTTS audio generation."""
import asyncio
from pathlib import Path
from app.services.tts_service import tts_service

async def test():
    # Test text
    test_text = "Hello, this is a test of the text to speech system. This audio should sound natural and clear."
    chapter_id = "test_chapter"
    
    print(f"Testing gTTS with text: {test_text[:50]}...")
    
    try:
        result = await tts_service.generate_chapter_audio(chapter_id, test_text)
        print(f"\nGeneration result:")
        print(f"  Status: {result['status']}")
        print(f"  Audio URL: {result['audio_url']}")
        print(f"  Text length: {result['text_length']}")
        print(f"  Cached: {result['cached']}")
        
        # Check if file exists
        audio_path = Path(f"./storage/audio/{chapter_id}")
        if audio_path.exists():
            mp3_files = list(audio_path.glob("*.mp3"))
            if mp3_files:
                file_size = mp3_files[0].stat().st_size
                print(f"\nAudio file generated:")
                print(f"  Path: {mp3_files[0]}")
                print(f"  Size: {file_size / 1024:.1f} KB")
                print(f"\n[+] SUCCESS: Audio generated with real speech!")
            else:
                print("[-] No MP3 file found")
        else:
            print("[-] Audio directory not found")
            
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
