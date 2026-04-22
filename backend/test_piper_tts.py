#!/usr/bin/env python
"""Test Piper TTS integration."""
import sys
from pathlib import Path

# Test 1: Check if Piper is installed
try:
    from piper import PiperVoice
    print("✅ Piper TTS package is installed")
except ImportError as e:
    print(f"❌ Piper TTS not installed: {e}")
    sys.exit(1)

# Test 2: Try to load a voice model
voice_model = "en_US-amy-medium"
print(f"\n📦 Attempting to load voice model: {voice_model}")

try:
    voice = PiperVoice.load(voice_model)
    print(f"✅ Voice model loaded successfully")
except FileNotFoundError as e:
    print(f"⚠️  Voice model not available locally: {e}")
    print("   (This is expected if the model hasn't been downloaded yet)")
    print(f"   To download manually, you can run:")
    print(f"   python -m piper.download --language en --quality medium")
    sys.exit(0)  # Not a fatal error - fallback will work
except Exception as e:
    print(f"❌ Error loading voice: {e}")
    sys.exit(1)

# Test 3: Try to generate audio
print(f"\n🎙️  Testing audio generation...")
test_text = "Hello, this is a test of Piper text to speech."

try:
    wav_data = bytearray()
    for audio_chunk in voice.synthesize(test_text):
        wav_data.extend(audio_chunk)
    
    print(f"✅ Audio generated successfully!")
    print(f"   Audio size: {len(wav_data)} bytes")
    
    # Save test audio
    test_output = Path(__file__).parent / "test_piper_output.wav"
    test_output.write_bytes(bytes(wav_data))
    print(f"   Saved to: {test_output}")
    
except Exception as e:
    print(f"❌ Error generating audio: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n✅ Piper TTS is ready to use!")
