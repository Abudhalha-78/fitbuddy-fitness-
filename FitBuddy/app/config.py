import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "FitBuddy")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    secret_key: str = os.getenv("SECRET_KEY", "development-only-secret")

settings = Settings()
