from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Automated Manga Reader API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./manga_reader.db"
    mangadex_base_url: str = "https://api.mangadex.org"
    mangadex_at_home_base_url: str = "https://api.mangadex.org/at-home/server"
    request_timeout_seconds: int = 20
    default_language: str = "en"
    page_cache_dir: str = "./storage/pages"
    ocr_engine_name: str = "pytesseract"
    tesseract_cmd: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
