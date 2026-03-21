from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class MangaDexService:
    def __init__(self) -> None:
        self.base_url = settings.mangadex_base_url
        self.at_home_base_url = settings.mangadex_at_home_base_url
        self.timeout = settings.request_timeout_seconds

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": "automated-manga-reader-mvp/0.1"}) as client:
                response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.json() if exc.response.headers.get("content-type", "").startswith("application/json") else {"message": exc.response.text}
            raise HTTPException(status_code=exc.response.status_code, detail={"message": "MangaDex request failed", "error": detail}) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail={"message": "Unable to reach MangaDex", "error": str(exc)}) from exc

    def search_manga(self, title: str, limit: int = 10) -> list[dict[str, Any]]:
        params = {
            "title": title,
            "limit": min(max(limit, 1), 50),
            "includes[]": ["cover_art"],
            "availableTranslatedLanguage[]": [settings.default_language],
        }
        payload = self._get("/manga", params=params)

        results: list[dict[str, Any]] = []
        for item in payload.get("data", []):
            attributes = item.get("attributes", {})
            title_map = attributes.get("title", {})
            description_map = attributes.get("description", {})
            relationships = item.get("relationships", [])

            cover_file = None
            for rel in relationships:
                if rel.get("type") == "cover_art":
                    cover_file = rel.get("attributes", {}).get("fileName")
                    break

            cover_url = None
            if cover_file:
                cover_url = f"https://uploads.mangadex.org/covers/{item['id']}/{cover_file}.256.jpg"

            results.append(
                {
                    "id": item["id"],
                    "title": title_map.get("en") or next(iter(title_map.values()), "Unknown"),
                    "description": description_map.get("en") or next(iter(description_map.values()), None),
                    "status": attributes.get("status"),
                    "cover_url": cover_url,
                }
            )

        return results

    def get_manga(self, manga_id: str) -> dict[str, Any]:
        return self._get(f"/manga/{manga_id}")

    def get_chapter_feed(self, manga_id: str, language: str = "en", limit: int = 100) -> list[dict[str, Any]]:
        params = {
            "translatedLanguage[]": [language],
            "order[chapter]": "asc",
            "limit": min(max(limit, 1), 500),
        }
        payload = self._get(f"/manga/{manga_id}/feed", params=params)

        chapters: list[dict[str, Any]] = []
        for chapter in payload.get("data", []):
            attributes = chapter.get("attributes", {})
            chapters.append(
                {
                    "id": chapter["id"],
                    "volume": attributes.get("volume"),
                    "chapter_number": attributes.get("chapter"),
                    "title": attributes.get("title"),
                    "translated_language": attributes.get("translatedLanguage"),
                }
            )
        return chapters

    def get_chapter_metadata(self, chapter_id: str) -> dict[str, Any]:
        return self._get(f"/chapter/{chapter_id}")

    def get_chapter_images(self, chapter_id: str, quality: str = "data") -> dict[str, Any]:
        if quality not in {"data", "data-saver"}:
            raise HTTPException(status_code=422, detail={"message": "Invalid quality. Use 'data' or 'data-saver'."})

        url = f"{self.at_home_base_url}/{chapter_id}"
        try:
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": "automated-manga-reader-mvp/0.1"}) as client:
                response = client.get(url)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail={"message": "Failed to fetch chapter image metadata"}) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail={"message": "Unable to reach MangaDex at-home server", "error": str(exc)}) from exc

        base_url = payload.get("baseUrl")
        chapter = payload.get("chapter", {})
        chapter_hash = chapter.get("hash")
        files = chapter.get("data", []) if quality == "data" else chapter.get("dataSaver", [])

        if not base_url or not chapter_hash:
            raise HTTPException(status_code=502, detail={"message": "Invalid chapter image metadata from MangaDex"})

        image_urls = [f"{base_url}/{quality}/{chapter_hash}/{filename}" for filename in files]
        return {
            "chapter_id": chapter_id,
            "quality": quality,
            "chapter_hash": chapter_hash,
            "image_urls": image_urls,
        }


mangadex_service = MangaDexService()
