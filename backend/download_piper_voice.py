#!/usr/bin/env python
"""Download Piper voice model from HuggingFace."""
import urllib.request
import urllib.error
from pathlib import Path
import json

# Model information
voice_name = "en_US-amy-medium"
model_dir = Path.home() / ".local" / "share" / "piper_tts"
model_dir.mkdir(parents=True, exist_ok=True)

# HuggingFace URLs for the model files
# Try multiple possible paths
urls_to_try = [
    # (model_url, config_url, description)
    (
        f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/{voice_name}.onnx",
        f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/{voice_name}.json",
        "Root en directory"
    ),
    (
        f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{voice_name}/{voice_name}.onnx",
        f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{voice_name}/{voice_name}.json",
        "Voice name directory"
    ),
]

model_url = None
config_url = None

for m_url, c_url, desc in urls_to_try:
    print(f"\nTrying {desc}...")
    try:
        # Quick head request to test if URL exists
        import urllib.request
        req = urllib.request.Request(m_url, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"  [+] Found!")
            model_url = m_url
            config_url = c_url
            break
    except Exception as e:
        print(f"  [-] Not found: {type(e).__name__}")

if not model_url:
    print("\n[-] Could not find model files on HuggingFace")
    print("[*] Alternative: The service will use fallback audio (silent WAV)")
    import sys
    sys.exit(0)

print(f"\nDownloading Piper voice model: {voice_name}")
print(f"Destination: {model_dir}")

# Download model file
model_file = model_dir / f"{voice_name}.onnx"
config_file = model_dir / f"{voice_name}.json"

print(f"\n1. Downloading model file...")
try:
    urllib.request.urlretrieve(model_url, model_file)
    print(f"   [+] Downloaded: {model_file} ({model_file.stat().st_size / 1024 / 1024:.1f} MB)")
except urllib.error.URLError as e:
    print(f"   [-] Failed to download model: {e}")
    print(f"   URL: {model_url}")
except Exception as e:
    print(f"   [-] Error: {e}")

# Download config file
print(f"\n2. Downloading config file...")
try:
    urllib.request.urlretrieve(config_url, config_file)
    print(f"   [+] Downloaded: {config_file}")
    # Verify config is valid JSON
    with open(config_file) as f:
        config_data = json.load(f)
    print(f"   Config loaded successfully")
except urllib.error.URLError as e:
    print(f"   [-] Failed to download config: {e}")
    print(f"   URL: {config_url}")
except Exception as e:
    print(f"   [-] Error: {e}")

# Verify both files exist
if model_file.exists() and config_file.exists():
    print(f"\n[+] Voice model downloaded successfully!")
    print(f"   Model: {model_file}")
    print(f"   Config: {config_file}")
else:
    print(f"\n[*] Some files are missing. Please check the URLs or download manually.")
