from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db
import models
import schemas
from ai_engine import AIEngine

router = APIRouter(prefix="/scheduling", tags=["Scheduling & Conflict Detection"])

@router.get("/drives", response_model=List[schemas.DriveOut])
def get_drives(db: Session = Depends(get_db)):
    return db.query(models.PlacementDrive).order_by(models.PlacementDrive.drive_date.asc()).all()

@router.post("/drives", response_model=schemas.DriveOut)
def create_drive(drive_in: schemas.DriveCreate, db: Session = Depends(get_db)):
    drv = models.PlacementDrive(
        job_id=drive_in.job_id,
        company_name=drive_in.company_name,
        role_title=drive_in.role_title,
        drive_date=drive_in.drive_date,
        start_time=drive_in.start_time,
        end_time=drive_in.end_time,
        venue=drive_in.venue,
        panel_name=drive_in.panel_name,
        eligibility_criteria=drive_in.eligibility_criteria,
        status="SCHEDULED"
    )
    db.add(drv)
    db.commit()
    db.refresh(drv)
    return drv

@router.put("/drives/{drive_id}", response_model=schemas.DriveOut)
def update_drive(drive_id: int, updates: schemas.DriveCreate, db: Session = Depends(get_db)):
    drv = db.query(models.PlacementDrive).filter(models.PlacementDrive.id == drive_id).first()
    if not drv:
        raise HTTPException(status_code=404, detail="Placement drive not found")

    drv.company_name = updates.company_name
    drv.role_title = updates.role_title
    drv.drive_date = updates.drive_date
    drv.start_time = updates.start_time
    drv.end_time = updates.end_time
    drv.venue = updates.venue
    drv.panel_name = updates.panel_name
    if updates.eligibility_criteria:
        drv.eligibility_criteria = updates.eligibility_criteria

    db.commit()
    db.refresh(drv)
    return drv

@router.get("/conflicts")
def check_drive_conflicts(db: Session = Depends(get_db)):
    """
    Intelligent Conflict Detection:
    Detects venue double-booking, panel over-allocation, and student schedule clashes.
    """
    drives = db.query(models.PlacementDrive).all()
    apps = db.query(models.Application).all()

    drives_data = []
    for d in drives:
        drives_data.append({
            "id": d.id,
            "company_name": d.company_name,
            "role_title": d.role_title,
            "drive_date": d.drive_date,
            "start_time": d.start_time,
            "end_time": d.end_time,
            "venue": d.venue,
            "panel_name": d.panel_name
        })

    apps_data = []
    for a in apps:
        apps_data.append({
            "id": a.id,
            "student_id": a.student_id,
            "student_name": a.student.name if a.student else f"Student #{a.student_id}",
            "job_id": a.job_id,
            "drive_id": a.drive_id,
            "status": a.status
        })

    conflict_report = AIEngine.detect_drive_conflicts(drives_data, apps_data)
    return conflict_report

@router.post("/optimize")
def optimize_drive_schedules(db: Session = Depends(get_db)):
    """
    Automatic Scheduling Algorithm:
    Proposes conflict-free staggered time slots and distributed venues to eliminate all clashes.
    """
    drives = db.query(models.PlacementDrive).all()
    drives_data = [{
        "id": d.id,
        "company_name": d.company_name,
        "role_title": d.role_title,
        "drive_date": d.drive_date,
        "start_time": d.start_time,
        "end_time": d.end_time,
        "venue": d.venue,
        "panel_name": d.panel_name
    } for d in drives]

    optimized = AIEngine.optimize_schedules(drives_data)

    return {
        "message": "Optimization completed: Generated non-overlapping drive schedule",
        "optimized_drives": optimized,
        "total_optimized": len(optimized)
    }

@router.post("/apply-optimization")
def apply_optimized_schedules(db: Session = Depends(get_db)):
    """Applies optimized schedule directly to the database drives."""
    drives = db.query(models.PlacementDrive).all()
    drives_data = [{
        "id": d.id,
        "company_name": d.company_name,
        "role_title": d.role_title,
        "drive_date": d.drive_date,
        "start_time": d.start_time,
        "end_time": d.end_time,
        "venue": d.venue,
        "panel_name": d.panel_name
    } for d in drives]

    optimized = AIEngine.optimize_schedules(drives_data)
    for opt in optimized:
        d = db.query(models.PlacementDrive).filter(models.PlacementDrive.id == opt["id"]).first()
        if d:
            d.start_time = opt["proposed_start_time"]
            d.end_time = opt["proposed_end_time"]
            d.venue = opt["proposed_venue"]
            d.panel_name = opt["proposed_panel"]

    db.commit()
    return {"message": "Optimized schedule successfully saved to database. All conflicts resolved!"}
