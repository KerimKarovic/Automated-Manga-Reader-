# backend/app/api/mangadex_api.py

import requests
from fastapi import HTTPException

def fetch_mangadex_statistics(manga_id: str):
    url = f"https://api.mangadex.org/statistics/manga/{manga_id}"
    headers = {
        "User-Agent": "manga_reader_app/1.0"  # Replace with your app's name/version.
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch MangaDex statistics")
    return response.json()

def parse_comments_from_stats(stats_json: dict, manga_id: str):
    statistics = stats_json.get("statistics", {})
    manga_stats = statistics.get(manga_id, {})
    comments = manga_stats.get("comments")
    return comments
