import os
import json
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pypdf import PdfReader

from database import get_db
import models
import schemas
from auth import get_current_user
from ai_engine import AIEngine
from config import settings

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[schemas.StudentOut])
def get_students(
    branch: Optional[str] = None,
    min_cgpa: Optional[float] = None,
    readiness_class: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Student)
    if branch and branch != "ALL":
        query = query.filter(models.Student.branch == branch)
    if min_cgpa is not None:
        query = query.filter(models.Student.cgpa >= min_cgpa)
    if readiness_class and readiness_class != "ALL":
        query = query.filter(models.Student.readiness_class == readiness_class)
    return query.order_by(models.Student.cgpa.desc()).all()

@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    updates: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "STUDENT" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot edit another student's profile")

    if updates.phone is not None: student.phone = updates.phone
    if updates.branch is not None: student.branch = updates.branch
    if updates.cgpa is not None: student.cgpa = updates.cgpa
    if updates.backlogs is not None: student.backlogs = updates.backlogs
    if updates.technical_skills is not None:
        student.technical_skills = json.dumps([AIEngine.normalize_skill(s) for s in updates.technical_skills])
    if updates.soft_skills is not None:
        student.soft_skills = json.dumps(updates.soft_skills)
    if updates.certifications is not None:
        student.certifications = json.dumps(updates.certifications)
    if updates.projects is not None:
        student.projects = json.dumps(updates.projects)
    if updates.internship_experience is not None:
        student.internship_experience = updates.internship_experience

    # Recalculate readiness
    readiness = AIEngine.calculate_readiness_score(student)
    student.readiness_score = readiness["readiness_score"]
    student.readiness_class = readiness["readiness_class"]
    student.readiness_factors = json.dumps(readiness["positive_factors"])
    student.improvement_areas = json.dumps(readiness["improvement_areas"])

    db.commit()
    db.refresh(student)
    return student

@router.post("/{student_id}/resume")
async def upload_resume(
    student_id: int,
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    extracted_text = ""
    file_url = None

    if file and file.filename:
        content = await file.read()
        filename = f"resume_{student.id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        file_url = f"/uploads/{filename}"

        if file.filename.lower().endswith(".pdf"):
            try:
                reader = PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    extracted_text += (page.extract_text() or "") + "\n"
            except Exception as e:
                extracted_text = f"Resume file uploaded: {file.filename}"
        else:
            try:
                extracted_text = content.decode("utf-8", errors="ignore")
            except Exception:
                extracted_text = "Resume document content"

    elif raw_text:
        extracted_text = raw_text

    if not extracted_text:
        raise HTTPException(status_code=400, detail="Please provide a valid resume PDF file or resume text.")

    # NLP Analysis
    nlp_results = AIEngine.parse_resume_text(extracted_text)
    student.resume_text = extracted_text
    if file_url:
        student.resume_url = file_url

    # Merge newly detected skills with existing skills
    try:
        current_skills = set(json.loads(student.technical_skills or '[]'))
    except Exception:
        current_skills = set()

    for s in nlp_results["detected_skills"]:
        current_skills.add(s)

    student.technical_skills = json.dumps(sorted(list(current_skills)))

    # Recalculate readiness
    readiness = AIEngine.calculate_readiness_score(student)
    student.readiness_score = readiness["readiness_score"]
    student.readiness_class = readiness["readiness_class"]
    student.readiness_factors = json.dumps(readiness["positive_factors"])
    student.improvement_areas = json.dumps(readiness["improvement_areas"])

    # Record Document
    doc = models.Document(
        student_id=student.id,
        doc_type="RESUME",
        title=file.filename if (file and file.filename) else "Uploaded_Resume_Text.txt",
        file_url=file_url or "/uploads/text_resume.txt",
        status="VERIFIED"
    )
    db.add(doc)

    # Add notification
    notif = models.Notification(
        user_id=student.user_id,
        title="Resume Audited & Skills Updated",
        message=f"AI extracted {len(nlp_results['detected_skills'])} technical skills from your resume. Readiness score updated to {student.readiness_score}.",
        category="SKILL_GAP"
    )
    db.add(notif)

    db.commit()
    db.refresh(student)

    return {
        "message": "Resume parsed and profile updated successfully",
        "nlp_results": nlp_results,
        "updated_skills": list(current_skills),
        "readiness_score": student.readiness_score,
        "readiness_class": student.readiness_class
    }

@router.get("/{student_id}/readiness")
def get_readiness_profile(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    readiness = AIEngine.calculate_readiness_score(student)
    return {
        "student_id": student.id,
        "student_name": student.name,
        "cgpa": student.cgpa,
        "readiness_score": readiness["readiness_score"],
        "readiness_class": readiness["readiness_class"],
        "dimensions": readiness["dimensions"],
        "positive_factors": readiness["positive_factors"],
        "improvement_areas": readiness["improvement_areas"],
        "assessment_scores": {
            "aptitude": student.aptitude_score,
            "coding": student.coding_score,
            "tech_assessment": student.tech_assessment_score,
            "communication": student.communication_score,
            "mock_interview": student.mock_interview_score
        }
    }

@router.get("/{student_id}/skill-gaps")
def get_skill_gaps(student_id: int, job_id: Optional[int] = None, role_name: Optional[str] = None, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        stu_skills = json.loads(student.technical_skills or '[]')
    except Exception:
        stu_skills = []

    if job_id:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        try:
            req_skills = json.loads(job.required_skills or '[]')
        except Exception:
            req_skills = ["Java", "SQL"]
        target_role = job.title
    else:
        req_skills = ["Java", "Spring Boot", "SQL", "REST API", "Git", "Docker"]
        target_role = role_name or "Software Developer"

    gap_analysis = AIEngine.analyze_skill_gap(stu_skills, req_skills)
    gap_analysis["target_role"] = target_role
    gap_analysis["student_name"] = student.name
    return gap_analysis

@router.get("/{student_id}/recommendations")
def get_personalized_recommendations(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    jobs = db.query(models.Job).filter(models.Job.is_active == True).all()
    recommendations = []

    for job in jobs:
        match_info = AIEngine.calculate_hybrid_match(student, job)
        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company_name": job.recruiter.company_name,
            "ctc_lpa": job.ctc_lpa,
            "location": job.location,
            "min_cgpa": job.min_cgpa,
            "fit_score": match_info["fit_score"],
            "is_eligible": match_info["is_eligible"],
            "matched_skills": match_info["matched_skills"],
            "missing_skills": match_info["missing_skills"],
            "recommendation": match_info["recommendation"],
            "positive_reasons": match_info["positive_reasons"]
        })

    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)

    # Preparation tasks
    prep_tasks = [
        {"task": "Solve 20 LeetCode Medium coding questions (focus: Arrays & Trees)", "category": "Coding"},
        {"task": "Review 10 relational SQL query join optimization problems", "category": "Database"},
        {"task": "Schedule 1 mock interview simulation for behavioral rounds", "category": "Interview"},
        {"task": "Add GitHub links and live demos to portfolio projects", "category": "Resume"}
    ]

    return {
        "student_id": student.id,
        "recommended_jobs": recommendations[:5],
        "top_skills_to_improve": ["Spring Boot", "Docker", "AWS", "REST API"] if "Spring Boot" not in (student.technical_skills or "") else ["Kubernetes", "GraphQL", "CI/CD"],
        "recommended_preparation": prep_tasks
    }

@router.get("/{student_id}/applications")
def get_student_applications(student_id: int, db: Session = Depends(get_db)):
    apps = db.query(models.Application).filter(models.Application.student_id == student_id).all()
    result = []
    for a in apps:
        exp = json.loads(a.match_explanation or "{}") if a.match_explanation else {}
        result.append({
            "id": a.id,
            "job_id": a.job_id,
            "job_title": a.job.title,
            "company_name": a.job.recruiter.company_name,
            "ctc_lpa": a.job.ctc_lpa,
            "drive_id": a.drive_id,
            "status": a.status,
            "match_score": a.match_score,
            "applied_at": a.applied_at,
            "explanation": exp
        })
    return result

@router.get("/{student_id}/offers")
def get_student_offers(student_id: int, db: Session = Depends(get_db)):
    offers = db.query(models.Offer).filter(models.Offer.student_id == student_id).all()
    return offers

@router.get("/{student_id}/documents")
def get_student_documents(student_id: int, db: Session = Depends(get_db)):
    docs = db.query(models.Document).filter(models.Document.student_id == student_id).all()
    return docs

@router.post("/{student_id}/apply")
def apply_to_job(
    student_id: int,
    app_in: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    job = db.query(models.Job).filter(models.Job.id == app_in.job_id).first()
    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or Job not found")

    existing = db.query(models.Application).filter(
        models.Application.student_id == student_id,
        models.Application.job_id == app_in.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    match_info = AIEngine.calculate_hybrid_match(student, job)
    status_assigned = "ELIGIBLE" if match_info["is_eligible"] else "APPLIED"
    if match_info["fit_score"] >= 80:
        status_assigned = "AI_SHORTLISTED"

    app = models.Application(
        student_id=student.id,
        job_id=job.id,
        drive_id=app_in.drive_id,
        status=status_assigned,
        match_score=match_info["fit_score"],
        match_explanation=json.dumps(match_info)
    )
    db.add(app)

    notif = models.Notification(
        user_id=student.user_id,
        title=f"Application Submitted: {job.title}",
        message=f"Application received for {job.title} at {job.recruiter.company_name}. Initial match score: {match_info['fit_score']}% ({status_assigned}).",
        category="SHORTLIST" if status_assigned == "AI_SHORTLISTED" else "SYSTEM"
    )
    db.add(notif)

    db.commit()
    db.refresh(app)

    return {
        "message": f"Successfully applied for {job.title}",
        "application_id": app.id,
        "status": app.status,
        "match_score": app.match_score,
        "match_details": match_info
    }

@router.post("/{student_id}/offers/{offer_id}/respond")
def respond_to_offer(
    student_id: int,
    offer_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id, models.Offer.student_id == student_id).first()
    if not student or not offer:
        raise HTTPException(status_code=404, detail="Student or Offer not found")

    action = payload.get("action", "").upper()
    if action not in ["ACCEPT", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be ACCEPT or REJECT")

    remarks = payload.get("remarks")
    if action == "ACCEPT":
        offer.acceptance_status = "ACCEPTED"
        offer.joining_status = "PENDING"
        if offer.application:
            offer.application.status = "OFFER_ACCEPTED"
        msg = f"Congratulations! You accepted the offer from {offer.company_name} for ₹{offer.ctc_lpa} LPA."
    else:
        offer.acceptance_status = "REJECTED"
        if offer.application:
            offer.application.status = "WITHDRAWN"
        msg = f"You declined the offer from {offer.company_name}."

    if remarks:
        offer.remarks = remarks

    # Notification
    notif = models.Notification(
        user_id=student.user_id,
        title=f"Offer Response Recorded: {offer.company_name}",
        message=msg,
        category="OFFER"
    )
    db.add(notif)
    db.commit()
    db.refresh(offer)

    return {
        "message": msg,
        "offer_id": offer.id,
        "acceptance_status": offer.acceptance_status,
        "joining_status": offer.joining_status
    }


@router.post("/chatbot/ask", response_model=schemas.ChatResponse)
def student_chatbot_ask(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    from routers.assistant_router import assistant_chat
    return assistant_chat(request=request, db=db)

