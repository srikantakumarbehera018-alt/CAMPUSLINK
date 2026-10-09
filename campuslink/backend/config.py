import os

class Settings:
    PROJECT_NAME: str = "CAMPUSLINK"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database Configuration (defaults to zero-friction local SQLite, easily switchable to MySQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./campuslink.db"
    )
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-campuslink-jwt-token-key-2026-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Uploads
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
