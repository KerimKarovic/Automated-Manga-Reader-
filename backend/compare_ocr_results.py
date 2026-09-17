#!/usr/bin/env python3
"""Compare manga-ocr results with Tesseract results."""

import json
from pathlib import Path

def compare_results():
    """Compare manga-ocr vs Tesseract outputs."""
    tesseract_file = Path("ocr_improved_results.json")
    mangaocr_file = Path("ocr_mangaocr_results.json")
    
    if not tesseract_file.exists():
        print(f"❌ {tesseract_file} not found")
        return
    
    if not mangaocr_file.exists():
        print(f"❌ {mangaocr_file} not found - manga-ocr test may still be running")
        return
    
    with tesseract_file.open(encoding='utf-8') as f:
        tesseract_results = json.load(f)
    
    with mangaocr_file.open(encoding='utf-8') as f:
        mangaocr_results = json.load(f)
    
    print("\n" + "="*80)
    print("OCR COMPARISON: manga-ocr vs Tesseract (Improved)")
    print("="*80)
    
    comparisons = []
    
    for tess_result, mocr_result in zip(tesseract_results, mangaocr_results):
        page_num = tess_result.get("page_number", "?")
        page_id = tess_result.get("page_id", "?")
        
        tess_length = tess_result.get("text_length", 0)
        mocr_length = mocr_result.get("text_length", 0)
        
        improvement = mocr_length - tess_length
        improvement_pct = (improvement / tess_length * 100) if tess_length > 0 else 0
        
        comparisons.append({
            "page_num": page_num,
            "page_id": page_id,
            "tesseract_chars": tess_length,
            "mangaocr_chars": mocr_length,
            "improvement": improvement,
            "improvement_pct": improvement_pct,
        })
        
        print(f"\nPage {page_num} (ID: {page_id}):")
        print(f"  Tesseract (Improved): {tess_length} chars")
        print(f"  manga-ocr:           {mocr_length} chars")
        if improvement >= 0:
            print(f"  ✓ Improvement: +{improvement} chars ({improvement_pct:+.1f}%)")
        else:
            print(f"  ↓ Regression: {improvement} chars ({improvement_pct:.1f}%)")
    
    # Summary statistics
    total_tess = sum(c["tesseract_chars"] for c in comparisons)
    total_mocr = sum(c["mangaocr_chars"] for c in comparisons)
    total_improvement = total_mocr - total_tess
    avg_improvement_pct = sum(c["improvement_pct"] for c in comparisons) / len(comparisons)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total characters (Tesseract): {total_tess}")
    print(f"Total characters (manga-ocr): {total_mocr}")
    print(f"Overall improvement: {total_improvement:+} chars ({total_improvement/total_tess*100:+.1f}%)")
    print(f"Average improvement per page: {avg_improvement_pct:+.1f}%")
    
    # Count wins/losses
    wins = sum(1 for c in comparisons if c["improvement"] > 0)
    losses = sum(1 for c in comparisons if c["improvement"] < 0)
    ties = sum(1 for c in comparisons if c["improvement"] == 0)
    
    print(f"\nPages where manga-ocr is better: {wins}")
    print(f"Pages where Tesseract is better: {losses}")
    print(f"Pages with same length: {ties}")
    
    # Save comparison to file
    comparison_file = Path("ocr_comparison_mangaocr_vs_tesseract.json")
    with comparison_file.open("w", encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tesseract_chars": total_tess,
                "total_mangaocr_chars": total_mocr,
                "total_improvement": total_improvement,
                "improvement_percentage": total_improvement/total_tess*100 if total_tess > 0 else 0,
                "avg_improvement_per_page": avg_improvement_pct,
                "pages_better": wins,
                "pages_worse": losses,
                "pages_equal": ties,
            },
            "page_comparisons": comparisons,
        }, f, indent=2)
    
    print(f"\n✅ Detailed comparison saved to {comparison_file}")

if __name__ == "__main__":
    compare_results()
