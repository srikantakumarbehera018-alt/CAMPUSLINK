from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db
import models
import schemas
from auth import get_current_user, require_role
from ai_engine import AIEngine

router = APIRouter(prefix="", tags=["Recruiter & Jobs"])

@router.get("/recruiters", response_model=List[schemas.RecruiterOut])
def get_recruiters(db: Session = Depends(get_db)):
    return db.query(models.Recruiter).all()

@router.get("/recruiters/{recruiter_id}", response_model=schemas.RecruiterOut)
def get_recruiter_by_id(recruiter_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Recruiter).filter(models.Recruiter.id == recruiter_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    return rec

@router.post("/jobs", response_model=schemas.JobOut)
def create_job(
    job_in: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    recruiter_id = None
    if current_user.role == "RECRUITER" and current_user.recruiter_profile:
        recruiter_id = current_user.recruiter_profile.id
    else:
        # Default to first recruiter for demo / admin creation
        first_rec = db.query(models.Recruiter).first()
        recruiter_id = first_rec.id if first_rec else 1

    # Extract NLP requirements from job description if description is extensive
    nlp_extracted = AIEngine.extract_job_requirements(job_in.description)
    merged_skills = list(set([AIEngine.normalize_skill(s) for s in (job_in.required_skills + nlp_extracted.get("required_skills", []))]))

    job = models.Job(
        recruiter_id=recruiter_id,
        title=job_in.title,
        description=job_in.description,
        min_cgpa=job_in.min_cgpa,
        eligible_branches=json.dumps(job_in.eligible_branches),
        required_skills=json.dumps(merged_skills),
        preferred_skills=json.dumps([AIEngine.normalize_skill(s) for s in job_in.preferred_skills]),
        required_certifications=json.dumps(job_in.required_certifications),
        ctc_lpa=job_in.ctc_lpa,
        location=job_in.location,
        job_type=job_in.job_type,
        deadline=job_in.deadline,
        is_active=True,
        extracted_requirements=json.dumps({
            "min_cgpa": job_in.min_cgpa,
            "branches": job_in.eligible_branches,
            "skills": merged_skills
        })
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/jobs", response_model=List[schemas.JobOut])
def get_jobs(recruiter_id: Optional[int] = None, is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(models.Job)
    if recruiter_id:
        query = query.filter(models.Job.recruiter_id == recruiter_id)
    if is_active is not None:
        query = query.filter(models.Job.is_active == is_active)
    return query.all()

@router.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/candidates")
def get_ranked_candidates_for_job(
    job_id: int,
    branch: Optional[str] = None,
    min_cgpa: Optional[float] = None,
    skill: Optional[str] = None,
    min_fit: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Ranks candidates for a given job using the hybrid AI matching engine.
    Returns: Fit score, Readiness score, Explainable reasons, Missing skills, and Responsible AI disclaimer.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    students = db.query(models.Student).all()
    results = []

    for s in students:
        # Optional filters
        if branch and branch != "ALL" and s.branch != branch:
            continue
        if min_cgpa is not None and s.cgpa < min_cgpa:
            continue
        if skill and skill.strip():
            try:
                s_skills = [x.lower() for x in json.loads(s.technical_skills or '[]')]
                if skill.strip().lower() not in s_skills:
                    continue
            except Exception:
                continue

        match_info = AIEngine.calculate_hybrid_match(s, job)
        if min_fit is not None and match_info["fit_score"] < min_fit:
            continue

        # Check existing application status if any
        app = db.query(models.Application).filter(
            models.Application.student_id == s.id,
            models.Application.job_id == job.id
        ).first()

        results.append({
            "student_id": s.id,
            "student_roll": s.student_id,
            "name": s.name,
            "email": s.email,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "backlogs": s.backlogs,
            "fit_score": match_info["fit_score"],
            "readiness_score": s.readiness_score,
            "readiness_class": s.readiness_class,
            "is_eligible": match_info["is_eligible"],
            "matched_skills": match_info["matched_skills"],
            "missing_skills": match_info["missing_skills"],
            "positive_reasons": match_info["positive_reasons"],
            "recommendation": match_info["recommendation"],
            "application_status": app.status if app else "NOT_APPLIED",
            "application_id": app.id if app else None
        })

    results.sort(key=lambda x: x["fit_score"], reverse=True)
    return {
        "job_id": job.id,
        "job_title": job.title,
        "company_name": job.recruiter.company_name,
        "total_candidates_analyzed": len(results),
        "candidates": results,
        "responsible_ai_disclaimer": "AI recommendations are decision-support tools and should be reviewed by authorized placement personnel."
    }

@router.post("/jobs/{job_id}/shortlist")
def shortlist_candidates(
    job_id: int,
    payload: dict, # {"student_ids": [1, 2, ...]}
    db: Session = Depends(get_db)
):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student_ids = payload.get("student_ids", [])
    updated_count = 0

    for sid in student_ids:
        stu = db.query(models.Student).filter(models.Student.id == sid).first()
        if not stu:
            continue

        app = db.query(models.Application).filter(
            models.Application.student_id == sid,
            models.Application.job_id == job_id
        ).first()

        if not app:
            match_info = AIEngine.calculate_hybrid_match(stu, job)
            app = models.Application(
                student_id=sid,
                job_id=job_id,
                status="AI_SHORTLISTED",
                match_score=match_info["fit_score"],
                match_explanation=json.dumps(match_info)
            )
            db.add(app)
        else:
            app.status = "AI_SHORTLISTED"

        # In-app notification to student
        notif = models.Notification(
            user_id=stu.user_id,
            title="Shortlisted for Interview Drive!",
            message=f"Congratulations! You have been shortlisted for {job.title} at {job.recruiter.company_name}.",
            category="SHORTLIST"
        )
        db.add(notif)
        updated_count += 1

    db.commit()
    return {"message": f"Successfully shortlisted {updated_count} candidates for {job.title}."}
