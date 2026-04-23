#!/usr/bin/env python
"""Test pronunciation improvements on character names"""
import httpx

chapter_id = "b5ae762c-6a57-410c-a35f-bc443959b9f5"

# Test with text containing character names that should be capitalized
test_texts = [
    ("gourry is here", "Should capitalize 'Gourry'"),
    ("lina and zelgadis", "Should capitalize character names"),
    ("amelia helps philia", "Should handle multiple names"),
]

url = f"http://localhost:8001/audio/chapter/{chapter_id}/generate"

for page_text, description in test_texts:
    try:
        print(f"\nTesting: {description}")
        print(f"Text: {repr(page_text)}")
        response = httpx.post(url, json={"text": page_text}, timeout=30)
        data = response.json()
        
        if data.get("status") == "generated":
            file_response = httpx.get(f"http://localhost:8001{data['audio_url']}", timeout=10)
            print(f"✓ Audio generated: {len(file_response.content)} bytes")
        else:
            print(f"✗ Generation failed: {data.get('error_message')}")
            
    except Exception as e:
        print(f"Error: {e}")
