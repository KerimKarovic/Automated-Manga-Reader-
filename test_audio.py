#!/usr/bin/env python
"""Test audio generation with page-specific text"""
import httpx

chapter_id = "b5ae762c-6a57-410c-a35f-bc443959b9f5"

# Test page 4 which has more text
page_text = "THANKS TO\n* FINALLY LIVE"

url = f"http://localhost:8001/audio/chapter/{chapter_id}/generate"

try:
    # Generate audio for the page text
    print(f"Generating audio for: {repr(page_text)}")
    response = httpx.post(url, json={"text": page_text}, timeout=30)
    data = response.json()
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response:")
    for key, value in data.items():
        if key == "audio_url":
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    
    # Test serving the audio file
    if data.get("audio_url"):
        file_response = httpx.get(f"http://localhost:8001{data['audio_url']}", timeout=10)
        print(f"\nAudio file served: {file_response.status_code}")
        print(f"Content-Type: {file_response.headers.get('content-type')}")
        print(f"File size: {len(file_response.content)} bytes")
            
except Exception as e:
    print(f"Error: {e}")
