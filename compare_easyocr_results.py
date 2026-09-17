#!/usr/bin/env python3
"""Compare EasyOCR results with Tesseract results."""

import json
from pathlib import Path

def compare_results():
    """Compare EasyOCR vs Tesseract outputs."""
    tesseract_file = Path("ocr_improved_results.json")
    easyocr_file = Path("ocr_easyocr_results.json")
    
    if not tesseract_file.exists():
        print(f"❌ {tesseract_file} not found")
        return
    
    if not easyocr_file.exists():
        print(f"❌ {easyocr_file} not found")
        return
    
    with tesseract_file.open(encoding='utf-8') as f:
        tesseract_results = json.load(f)
    
    with easyocr_file.open(encoding='utf-8') as f:
        easyocr_results = json.load(f)
    
    print("\n" + "="*90)
    print("OCR COMPARISON: EasyOCR vs Tesseract (Improved)")
    print("="*90)
    
    comparisons = []
    
    for tess_result, easy_result in zip(tesseract_results, easyocr_results):
        page_num = tess_result.get("page_number", "?")
        page_id = tess_result.get("page_id", "?")
        
        tess_length = tess_result.get("text_length", 0)
        easy_length = easy_result.get("text_length", 0)
        
        improvement = easy_length - tess_length
        improvement_pct = (improvement / tess_length * 100) if tess_length > 0 else 0
        ratio = easy_length / tess_length if tess_length > 0 else 0
        
        comparisons.append({
            "page_num": page_num,
            "page_id": page_id,
            "tesseract_chars": tess_length,
            "easyocr_chars": easy_length,
            "improvement": improvement,
            "improvement_pct": improvement_pct,
            "ratio": ratio,
        })
        
        status_icon = "✓" if easy_length >= tess_length * 0.9 else "⚠"
        print(f"\n{status_icon} Page {page_num} (ID: {page_id}):")
        print(f"    Tesseract:  {tess_length:4d} chars")
        print(f"    EasyOCR:    {easy_length:4d} chars  ({ratio:5.1%} of Tesseract)")
        if improvement >= 0:
            print(f"    ✓ Better by +{improvement} chars ({improvement_pct:+.1f}%)")
        else:
            print(f"    ↓ Less by {improvement} chars ({improvement_pct:.1f}%)")
    
    # Summary statistics
    total_tess = sum(c["tesseract_chars"] for c in comparisons)
    total_easy = sum(c["easyocr_chars"] for c in comparisons)
    total_improvement = total_easy - total_tess
    avg_ratio = sum(c["ratio"] for c in comparisons) / len(comparisons)
    
    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)
    print(f"Total characters (Tesseract): {total_tess}")
    print(f"Total characters (EasyOCR):   {total_easy}")
    print(f"Overall ratio: {avg_ratio:.1%} (EasyOCR vs Tesseract)")
    print(f"Overall difference: {total_improvement:+} chars ({total_improvement/total_tess*100:+.1f}%)")
    
    # Count wins/losses
    wins = sum(1 for c in comparisons if c["improvement"] >= 0)
    losses = sum(1 for c in comparisons if c["improvement"] < 0)
    
    print(f"\nPages where EasyOCR is comparable (≥90%): {wins}/{len(comparisons)}")
    print(f"Pages where EasyOCR is less: {losses}/{len(comparisons)}")
    
    # Save comparison to file
    comparison_file = Path("ocr_comparison_easyocr_vs_tesseract.json")
    with comparison_file.open("w", encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tesseract_chars": total_tess,
                "total_easyocr_chars": total_easy,
                "total_difference": total_improvement,
                "difference_percentage": total_improvement/total_tess*100 if total_tess > 0 else 0,
                "average_ratio": avg_ratio,
                "pages_better_or_equal": wins,
                "pages_worse": losses,
            },
            "page_comparisons": comparisons,
        }, f, indent=2)
    
    print(f"\n✅ Detailed comparison saved to {comparison_file}")

if __name__ == "__main__":
    compare_results()
