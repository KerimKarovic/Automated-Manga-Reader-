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
- Audio scaffold endpoint that honestly reports when OCR text is not available
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
				audio.py
		services/
			mangadex_service.py
			manga_service.py
			chapter_service.py
			page_service.py
			analysis_service.py
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

4. Run the API:

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
- GET /audio/chapter/{chapter_id}

## Notes On OCR/Audio

- OCR is not yet implemented in this MVP.
- The audio endpoint does not fake playback or text extraction.
- If OCR text is unavailable, audio endpoint returns a clean unavailable response.

## MVP Behavior Expectations

- Start backend and frontend locally
- Search MangaDex and import manga locally
- Open imported manga and list chapters
- Store chapter pages in local DB on chapter open
- Read chapter pages including fullscreen view
