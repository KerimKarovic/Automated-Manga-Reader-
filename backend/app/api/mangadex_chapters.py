# backend/app/api/mangadex_chapters.py

import requests
from fastapi import HTTPException

BASE_URL = "https://api.mangadex.org"

def search_manga_by_title(title: str):
    """
    Search for a manga by title.
    (This is a simplified example. Check the MangaDex API docs for the exact parameters.)
    """
    params = {
        "title": title
    }
    response = requests.get(f"{BASE_URL}/manga", params=params, headers={"User-Agent": "YourAppName/1.0"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Manga search failed")
    return response.json()

def get_manga_feed(manga_id: str, translated_languages: list = None):
    """
    Retrieve the chapter feed for a given manga.
    Optionally filter by languages (e.g., ["en"] for English).
    """
    params = {}
    if translated_languages:
        # MangaDex expects query parameters in an array format
        for lang in translated_languages:
            params.setdefault("translatedLanguage[]", []).append(lang)
    response = requests.get(f"{BASE_URL}/manga/{manga_id}/feed", params=params, headers={"User-Agent": "YourAppName/1.0"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve manga feed")
    return response.json()

def get_chapter_images(chapter_id: str):
    """
    Retrieve image delivery metadata for a chapter from the MangaDex @Home endpoint.
    Returns a tuple of (base_url, chapter_hash, data, data_saver).
    """
    response = requests.get(f"{BASE_URL.replace('mangadex.org', 'mangadex.org')}/at-home/server/{chapter_id}", headers={"User-Agent": "YourAppName/1.0"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve chapter images")
    data = response.json()
    base_url = data.get("baseUrl")
    chapter = data.get("chapter", {})
    chapter_hash = chapter.get("hash")
    data_quality = chapter.get("data", [])
    data_saver = chapter.get("dataSaver", [])
    return base_url, chapter_hash, data_quality, data_saver

def construct_image_urls(base_url: str, chapter_hash: str, filenames: list, quality: str = "data"):
    """
    Construct full image URLs given the base URL, chapter hash, filenames and quality.
    Quality should be "data" for original or "data-saver" for compressed images.
    """
    return [f"{base_url}/{quality}/{chapter_hash}/{filename}" for filename in filenames]
