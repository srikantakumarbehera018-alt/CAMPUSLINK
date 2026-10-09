import os
import sys

# Ensure current backend directory is in sys.path for direct module resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from database import engine, Base, SessionLocal
import models
from seed_data import seed_database

# Import routers
from routers import (
    auth_router,
    student_router,
    recruiter_router,
    admin_router,
    scheduling_router,
    analytics_router,
    notifications_router,
    assistant_router,
    demo_router,
    interview_router,
)

app = FastAPI(
    title="CAMPUSLINK API",
    description="AI-Powered Campus-to-Corporate Placement Management & Analytics Platform",
    version=settings.VERSION
)

# Determine allowed origins for CORS
origins_raw = settings.ALLOWED_ORIGINS.strip()
if origins_raw:
    origins = [orig.strip() for orig in origins_raw.split(",") if orig.strip()]
else:
    # Default allowed origins for local development and production
    origins = [
        "https://campuslink-gamma-neon.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
    ]

# Explicitly guarantee that the production Vercel frontend is always allowed
production_frontend = "https://campuslink-gamma-neon.vercel.app"
if production_frontend not in origins:
    origins.append(production_frontend)

# If wildcard is used, credentials must be False per CORS specification.
has_wildcard = "*" in origins
allow_creds = not has_wildcard

# Support *.vercel.app preview URLs if explicit wildcard is not configured
allow_regex = r"^https:\/\/.*\.vercel\.app$" if not has_wildcard else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_regex,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(student_router.router, prefix="/api")
app.include_router(recruiter_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(scheduling_router.router, prefix="/api")
app.include_router(analytics_router.router, prefix="/api")
app.include_router(notifications_router.router, prefix="/api")
app.include_router(assistant_router.router, prefix="/api")
app.include_router(interview_router.router, prefix="/api")
app.include_router(demo_router.router, prefix="/api")

# Static and Upload directories setup (graceful for serverless / read-only environments)
STATIC_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "static")
UPLOAD_DIR = settings.UPLOAD_DIR

try:
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR, exist_ok=True)
except OSError:
    pass

try:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    pass

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if os.path.isdir(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def on_startup():
    try:
        # Initialize Database Schema if not already present
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            user_count = db.query(models.User).count()
            if user_count == 0:
                print("No users found in database. Auto-seeding realistic placement dataset...")
                seed_database()
            else:
                print(f"Database contains {user_count} users. Ready.")
        finally:
            db.close()
    except Exception as e:
        print(f"Startup database warning / check: {e}")


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "CAMPUSLINK FastAPI backend is running.",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    db_type = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "remote_sql"
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_type,
        "serverless": settings.IS_VERCEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
