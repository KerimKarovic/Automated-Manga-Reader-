#!/usr/bin/env python3
"""Test manga-ocr on the same pages as Tesseract for comparison."""

import json
from pathlib import Path
from manga_ocr import MangaOcr

# Test pages 271-280 (pages 1-10 of the chapter)
TEST_PAGE_IDS = list(range(271, 281))
IMAGE_DIR = Path("storage/pages/4a72fe55-8389-4fb0-9eaa-513f721c9ac2")

# Map page IDs to file numbers
PAGE_ID_TO_FILE = {
    271: "0001.jpg",
    272: "0002.jpg",
    273: "0003.jpg",
    274: "0004.jpg",
    275: "0005.jpg",
    276: "0006.jpg",
    277: "0007.jpg",
    278: "0008.jpg",
    279: "0009.jpg",
    280: "0010.jpg",
}

def test_mangaocr():
    """Test manga-ocr extraction on test pages."""
    print("Initializing manga-ocr...")
    mocr = MangaOcr()
    
    results = []
    
    for page_id in TEST_PAGE_IDS:
        image_file = PAGE_ID_TO_FILE[page_id]
        image_path = IMAGE_DIR / image_file
        
        if not image_path.exists():
            print(f"❌ Page {page_id}: Image not found at {image_path}")
            results.append({
                "page_id": page_id,
                "page_number": page_id - 270,
                "success": False,
                "error": "Image not found",
                "raw_text": None,
                "text_length": 0,
            })
            continue
        
        try:
            print(f"Processing page {page_id} ({image_file})...", end=" ")
            raw_text = mocr(str(image_path))
            text_length = len((raw_text or "").strip())
            print(f"✓ {text_length} chars")
            
            results.append({
                "page_id": page_id,
                "page_number": page_id - 270,
                "success": True,
                "error": None,
                "raw_text": raw_text,
                "text_length": text_length,
                "preview": (raw_text[:100] + "...") if len(raw_text) > 100 else raw_text,
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "page_id": page_id,
                "page_number": page_id - 270,
                "success": False,
                "error": str(e),
                "raw_text": None,
                "text_length": 0,
            })
    
    # Save results
    output_file = Path("ocr_mangaocr_results.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Print summary
    successful = sum(1 for r in results if r["success"])
    total_chars = sum(r["text_length"] for r in results if r["success"])
    avg_chars = total_chars / successful if successful > 0 else 0
    
    print(f"\nSummary:")
    print(f"  Pages processed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(results) - successful}")
    print(f"  Total characters: {total_chars}")
    print(f"  Average per page: {avg_chars:.0f}")

if __name__ == "__main__":
    test_mangaocr()
