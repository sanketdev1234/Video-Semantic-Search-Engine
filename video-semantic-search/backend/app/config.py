from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application configuration"""

    # API Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DEBUG: bool = True

    # File Paths
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    TEMP_DIR: str = "temp"

    # Models
    WHISPER_MODEL: str = "base"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    DEVICE: str = "cpu"

    # Processing
    FRAME_INTERVAL_SECONDS: int = 2
    MAX_VIDEO_SIZE_MB: int = 200
    BATCH_SIZE: int = 16

    # Search
    TOP_K_RESULTS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def setup_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    for dir_path in [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        settings.TEMP_DIR,
    ]:
        os.makedirs(dir_path, exist_ok=True)
