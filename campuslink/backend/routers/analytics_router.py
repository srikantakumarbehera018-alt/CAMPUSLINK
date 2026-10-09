from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from database import get_db
import models
from ai_engine import AIEngine

router = APIRouter(prefix="/analytics", tags=["Placement Analytics"])

@router.get("/dashboard")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    recruiters = db.query(models.Recruiter).all()
    drives = db.query(models.PlacementDrive).all()
    offers = db.query(models.Offer).all()

    total_students = len(students)
    placement_ready = sum(1 for s in students if s.readiness_score >= 60.0)
    
    # Placed students (either have accepted offer or status is JOINED)
    placed_student_ids = set()
    for o in offers:
        if o.acceptance_status in ["ACCEPTED"] or o.joining_status == "JOINED":
            placed_student_ids.add(o.student_id)
            
    placed_count = len(placed_student_ids)
    placement_pct = round((placed_count / max(total_students, 1)) * 100, 1)

    # Offers metrics
    ctc_list = [o.ctc_lpa for o in offers if o.ctc_lpa]
    avg_package = round(sum(ctc_list) / max(len(ctc_list), 1), 2) if ctc_list else 0.0
    highest_package = max(ctc_list) if ctc_list else 0.0

    # At risk count
    at_risk_count = sum(1 for s in students if s.at_risk_level in ["HIGH", "MEDIUM"])

    return {
        "total_students": total_students,
        "placement_ready_students": placement_ready,
        "students_needing_improvement": total_students - placement_ready,
        "students_placed": placed_count,
        "students_unplaced": total_students - placed_count,
        "placement_percentage": placement_pct,
        "total_recruiters": len(recruiters),
        "active_drives": len(drives),
        "offers_made": len(offers),
        "offers_accepted": sum(1 for o in offers if o.acceptance_status == "ACCEPTED"),
        "offers_pending": sum(1 for o in offers if o.acceptance_status == "PENDING"),
        "average_package_lpa": avg_package,
        "highest_package_lpa": highest_package,
        "students_at_risk": at_risk_count
    }

@router.get("/branches")
def get_branch_analytics(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    offers = db.query(models.Offer).all()

    placed_ids = set([o.student_id for o in offers if o.acceptance_status == "ACCEPTED" or o.joining_status == "JOINED"])
    
    # Group by branch
    branches = {}
    for s in students:
        b = s.branch
        if b not in branches:
            branches[b] = {"branch": b, "total": 0, "placed": 0, "ctc_sum": 0.0, "offers_count": 0}
        branches[b]["total"] += 1
        if s.id in placed_ids:
            branches[b]["placed"] += 1

    for o in offers:
        if o.student:
            b = o.student.branch
            if b in branches:
                branches[b]["ctc_sum"] += o.ctc_lpa
                branches[b]["offers_count"] += 1

    result = []
    for b, data in branches.items():
        total = data["total"]
        placed = data["placed"]
        pct = round((placed / max(total, 1)) * 100, 1)
        avg_ctc = round(data["ctc_sum"] / max(data["offers_count"], 1), 2) if data["offers_count"] > 0 else 5.5
        result.append({
            "branch": b,
            "total": total,
            "placed": placed,
            "placement_rate": pct,
            "avg_ctc_lpa": avg_ctc
        })

    result.sort(key=lambda x: x["placement_rate"], reverse=True)
    return result

@router.get("/skills")
def get_skill_analytics(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    offers = db.query(models.Offer).all()
    placed_ids = set([o.student_id for o in offers if o.acceptance_status == "ACCEPTED" or o.joining_status == "JOINED"])

    skill_counts = {}
    for s in students:
        try:
            skills = json.loads(s.technical_skills or '[]')
        except Exception:
            skills = []
        is_placed = s.id in placed_ids
        for sk in skills:
            norm = AIEngine.normalize_skill(sk)
            if norm not in skill_counts:
                skill_counts[norm] = {"skill": norm, "student_count": 0, "placed_count": 0}
            skill_counts[norm]["student_count"] += 1
            if is_placed:
                skill_counts[norm]["placed_count"] += 1

    result = []
    for sk, d in skill_counts.items():
        if d["student_count"] >= 2:
            pct = round((d["placed_count"] / max(d["student_count"], 1)) * 100, 1)
            result.append({
                "skill": sk,
                "student_count": d["student_count"],
                "placed_count": d["placed_count"],
                "placement_rate": pct
            })

    result.sort(key=lambda x: x["student_count"], reverse=True)
    return result[:8]

@router.get("/packages")
def get_package_distribution(db: Session = Depends(get_db)):
    offers = db.query(models.Offer).all()
    brackets = {
        "0–5 LPA": 0,
        "5–10 LPA": 0,
        "10–15 LPA": 0,
        "15+ LPA": 0
    }

    for o in offers:
        ctc = o.ctc_lpa
        if ctc < 5.0:
            brackets["0–5 LPA"] += 1
        elif ctc < 10.0:
            brackets["5–10 LPA"] += 1
        elif ctc < 15.0:
            brackets["10–15 LPA"] += 1
        else:
            brackets["15+ LPA"] += 1

    return [{"bracket": k, "count": v} for k, v in brackets.items()]

@router.get("/recruiters")
def get_recruiter_analytics(db: Session = Depends(get_db)):
    recruiters = db.query(models.Recruiter).all()
    result = []
    for r in recruiters:
        job_count = len(r.jobs)
        offers = db.query(models.Offer).filter(models.Offer.recruiter_id == r.id).all()
        ctc_sum = sum(o.ctc_lpa for o in offers)
        avg_ctc = round(ctc_sum / max(len(offers), 1), 2) if offers else 0.0

        result.append({
            "company_name": r.company_name,
            "industry": r.industry,
            "jobs_posted": job_count,
            "offers_made": len(offers),
            "avg_package_lpa": avg_ctc,
            "is_repeat_recruiter": True if len(offers) >= 1 else False
        })

    return result

@router.get("/trend")
def get_pipeline_funnel(db: Session = Depends(get_db)):
    apps = db.query(models.Application).all()
    offers = db.query(models.Offer).all()

    stages = {
        "Applied": len(apps),
        "AI Shortlisted": sum(1 for a in apps if a.status in ["AI_SHORTLISTED", "ASSESSMENT", "INTERVIEW", "SELECTED", "OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]),
        "Assessments": sum(1 for a in apps if a.status in ["ASSESSMENT", "INTERVIEW", "SELECTED", "OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]),
        "Interviews": sum(1 for a in apps if a.status in ["INTERVIEW", "SELECTED", "OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]),
        "Selected": sum(1 for a in apps if a.status in ["SELECTED", "OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]),
        "Offers Made": len(offers),
        "Joined": sum(1 for o in offers if o.joining_status == "JOINED")
    }

    return [{"stage": k, "count": v} for k, v in stages.items()]

@router.get("/at-risk")
def get_at_risk_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    apps = db.query(models.Application).all()

    apps_by_stu = {}
    for a in apps:
        apps_by_stu.setdefault(a.student_id, []).append(a)

    at_risk_list = AIEngine.evaluate_at_risk_students(students, apps_by_stu)
    return at_risk_list
