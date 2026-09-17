import httpx
import json
from pathlib import Path

results = []
for page_id in range(271, 281):
    try:
        response = httpx.get(f"http://localhost:8000/ocr/page/{page_id}")
        if response.status_code == 200:
            data = response.json()
            results.append(data)
            print(f"Page {data['page_number']}: {data['text_length']} characters")
    except Exception as e:
        print(f"Error fetching page {page_id}: {e}")

# Save results
output_path = Path("../ocr_improved_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved {len(results)} improved OCR results to {output_path}")
