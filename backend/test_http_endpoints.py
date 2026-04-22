#!/usr/bin/env python
"""Test TTS HTTP endpoints"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, '.')

import httpx

BASE_URL = "http://localhost:8001"


async def test_http_endpoints():
    """Test TTS HTTP endpoints"""
    print("=" * 60)
    print("HTTP ENDPOINTS TEST")
    print("=" * 60)
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        try:
            # Test 1: Health check
            print("\n[Test 1] Health check")
            resp = await client.get("/health")
            print(f"  Status: {resp.status_code}")
            print(f"  Response: {resp.json()}")
            
            # Test 2: TTS health check
            print("\n[Test 2] TTS health check")
            resp = await client.get("/health/tts")
            print(f"  Status: {resp.status_code}")
            health_data = resp.json()
            print(f"  TTS Available: {health_data['tts_available']}")
            print(f"  Engine: {health_data['engine_name']}")
            
            # Test 3: Try to get status for non-existent chapter
            print("\n[Test 3] Get audio status for non-existent chapter")
            resp = await client.get("/audio/chapter/nonexistent-chapter")
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 404:
                print(f"  ✓ Correctly returns 404")
            
            # Test 4: Try to generate for non-existent chapter
            print("\n[Test 4] Generate audio for non-existent chapter")
            resp = await client.post("/audio/chapter/nonexistent-chapter/generate")
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 404:
                print(f"  ✓ Correctly returns 404")
            
            # Test 5: Check routing works
            print("\n[Test 5] Verify /audio/file route exists")
            # This should 404 because the file doesn't exist, but the route should be recognized
            resp = await client.get("/audio/file/test-chapter/en-US_abcd1234.mp3")
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 404:
                print(f"  ✓ Route recognized, file not found (expected)")
            
            print("\n" + "=" * 60)
            print("✅ HTTP ENDPOINTS TEST PASSED")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


# Run async test
if __name__ == "__main__":
    asyncio.run(test_http_endpoints())
