import os
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

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CAMPUSLINK API",
    description="AI-Powered Campus-to-Corporate Placement Management & Analytics Platform",
    version=settings.VERSION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

# Static Directories
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def on_startup():
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

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CAMPUSLINK Backend is running. Please check /docs for OpenAPI specifications."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "platform": "CAMPUSLINK", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
