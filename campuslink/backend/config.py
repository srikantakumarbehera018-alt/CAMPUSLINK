import os

class Settings:
    PROJECT_NAME: str = "CAMPUSLINK"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Environment detection
    IS_VERCEL: bool = os.getenv("VERCEL") is not None or os.getenv("VERCEL_ENV") is not None

    # Database Configuration
    # Defaults to local SQLite file for development.
    # On Vercel, if no external database is configured, falls back to /tmp/campuslink.db
    # (temporary in serverless). For persistent production data, provide DATABASE_URL (e.g. Neon PostgreSQL).
    _default_db = "/tmp/campuslink.db" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "campuslink.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_default_db}")

    # JWT Authentication
    # Read from environment variables, fallback to local dev secret
    SECRET_KEY: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or "super-secret-campuslink-jwt-token-key-2026-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Uploads directory
    # On Vercel (read-only filesystem), /tmp is the only writable directory.
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        "/tmp/uploads" if IS_VERCEL else os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    )

    # Allowed CORS Origins (comma-separated URLs)
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS") or os.getenv("FRONTEND_URL") or "https://campuslink-gamma-neon.vercel.app"

settings = Settings()

try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
except OSError:
    pass
