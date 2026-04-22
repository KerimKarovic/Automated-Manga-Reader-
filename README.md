# Automated Manga Reader MVP Foundation

This repository contains a refactored MVP foundation for an automated manga reader. It keeps the original prototype flow (manga metadata -> chapters -> pages -> reader UI) while removing broken assumptions and duplicate logic.

## What Is Implemented

- FastAPI backend with modular route/service architecture
- SQLite database with SQLAlchemy models
- MangaDex integration for:
	- manga search
	- chapter feed
	- chapter image URLs
	- store chapter/page metadata locally
- Reader endpoints for chapter and sorted pages
- Analysis scaffold endpoint with basic panel detection and persisted panel rows
- Real whole-page OCR pipeline with persisted OCR results per page
- Audio status endpoint that uses real OCR availability and keeps an honest fallback when OCR text is missing
- Expo React Native frontend with:
	- local manga list
	- MangaDex search and local import
	- chapter list
	- chapter page reader
	- fullscreen page reading
	- audio status button/message

## Project Structure

backend/
	app/
		main.py
		core/
			config.py
		db/
			database.py
			models.py
			schemas.py
		api/
			routes/
				health.py
				manga.py
				mangadex.py
				reader.py
				analysis.py
				ocr.py
				audio.py
		services/
			mangadex_service.py
			manga_service.py
			chapter_service.py
			page_service.py
			analysis_service.py
			ocr_service.py
			audio_service.py
		utils/
			file_storage.py

frontend/
	src/
		config/
			api.ts
		services/
			api.ts
		types/
			index.ts
		components/
			FullscreenReader.tsx
		screens/
			HomeScreen.tsx
			ChapterListScreen.tsx
			ReaderScreen.tsx
		App.tsx

## Backend Setup

1. Open a terminal in backend/
2. Create and activate a virtual environment
3. Install dependencies:

	 pip install -r requirements.txt

4. Install Tesseract OCR engine (required for real OCR):

	 Windows (recommended):
	 - Install from UB Mannheim build: https://github.com/UB-Mannheim/tesseract/wiki
	 - Default install path is usually:
		 C:\Program Files\Tesseract-OCR\tesseract.exe

	 Configure backend to find Tesseract:
	 - Option A: add Tesseract install folder to PATH
	 - Option B: create backend/.env with:
		 TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

	 Optional cache config in backend/.env:
	 - PAGE_CACHE_DIR=./storage/pages
	 - OCR_ENGINE_NAME=pytesseract

5. Run the API:

	 uvicorn app.main:app --reload

Backend default URL: http://localhost:8000

## Frontend Setup

1. Open a terminal in frontend/
2. Install dependencies:

	 npm install

3. Set API base URL for your environment:

	 - PowerShell example:
		 $env:EXPO_PUBLIC_API_BASE_URL="http://localhost:8000"

	 For a physical device, set this to your machine LAN address.

4. Start Expo:

	 npm run start

## API Endpoints

- GET /health
- GET /manga
- POST /manga
- GET /manga/{id}
- GET /mangadex/search?title=...
- GET /mangadex/{manga_id}/chapters?language=en
- GET /mangadex/chapter/{chapter_id}/images?quality=data
- POST /mangadex/store-chapter/{chapter_id}
- GET /chapters/{chapter_id}
- GET /chapters/{chapter_id}/pages
- POST /analysis/page/{page_id}
- POST /ocr/page/{page_id}
- POST /ocr/chapter/{chapter_id}
- GET /ocr/page/{page_id}
- GET /ocr/chapter/{chapter_id}
- GET /audio/chapter/{chapter_id}

## Notes On OCR/Audio

- OCR is real and runs on full-page images using `pytesseract` + image preprocessing.
- OCR results are persisted per page with statuses: `pending`, `processing`, `completed`, `failed`.
- Chapter OCR retrieval returns ordered page OCR plus concatenated chapter text.
- Audio endpoint remains honest:
	- if no OCR text exists, it returns unavailable scaffold message
	- if OCR text exists, it returns ready status for a future TTS provider layer

## OCR Pipeline Summary

1. Resolve image source from `Page.local_image_path` or `Page.image_url`
2. Cache page image locally under `storage/pages/{chapter_id}`
3. Preprocess image (grayscale, normalization, blur, adaptive threshold, optional upscale)
4. Run OCR with `pytesseract`
5. Normalize text (whitespace + blank-line cleanup)
6. Persist raw/cleaned text and status in `page_ocr`
7. Aggregate chapter text in page order for audio readiness checks

## End-to-End Test Steps

1. Start backend:

	 cd backend
	 uvicorn app.main:app --reload

2. Start frontend:

	 cd frontend
	 npm install
	 npm run start

3. In app:
	 - import/select manga
	 - open a chapter
	 - tap `Run Chapter OCR`

4. Verify OCR endpoints:

	 GET /ocr/chapter/{chapter_id}
	 - confirm page results are ordered by page number
	 - confirm `chapter_text_length` > 0 for text-bearing chapters

5. Verify audio behavior:

	 GET /audio/chapter/{chapter_id}
	 - before OCR: `status=unavailable` with honest placeholder message
	 - after OCR text exists: `status=ready`, `text_available=true`, `chapter_text_length>0`

## MVP Behavior Expectations

- Start backend and frontend locally
- Search MangaDex and import manga locally
- Open imported manga and list chapters
- Store chapter pages in local DB on chapter open
- Run real whole-page OCR and persist results
- Retrieve chapter OCR text in page order
- Read chapter pages including fullscreen view
