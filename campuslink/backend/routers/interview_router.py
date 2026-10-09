from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/interviews", tags=["Interview Tracking & Evaluation"])

@router.get("", response_model=List[schemas.InterviewOut])
def get_interviews(
    student_id: Optional[int] = None,
    application_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Interview)
    if student_id:
        query = query.filter(models.Interview.student_id == student_id)
    if application_id:
        query = query.filter(models.Interview.application_id == application_id)
    if status and status != "ALL":
        query = query.filter(models.Interview.status == status)

    interviews = query.order_by(models.Interview.id.desc()).all()
    results = []
    for it in interviews:
        app = it.application
        student = db.query(models.Student).filter(models.Student.id == it.student_id).first()
        student_name = student.name if student else (app.student.name if (app and app.student) else f"Student #{it.student_id}")
        job_title = app.job.title if (app and app.job) else "Placement Drive Role"
        company_name = app.job.recruiter.company_name if (app and app.job and app.job.recruiter) else "Recruiting Partner"

        results.append(schemas.InterviewOut(
            id=it.id,
            application_id=it.application_id,
            student_id=it.student_id,
            student_name=student_name,
            job_title=job_title,
            company_name=company_name,
            drive_id=it.drive_id,
            round_name=it.round_name,
            scheduled_time=it.scheduled_time,
            interviewer_panel=it.interviewer_panel,
            status=it.status,
            feedback=it.feedback,
            technical_rating=it.technical_rating or 7.0,
            comm_rating=it.comm_rating or 7.0,
            recommendation=it.recommendation or "PROGRESS"
        ))
    return results

@router.get("/{interview_id}", response_model=schemas.InterviewOut)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    it = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Interview not found")

    app = it.application
    student = db.query(models.Student).filter(models.Student.id == it.student_id).first()
    student_name = student.name if student else (app.student.name if (app and app.student) else f"Student #{it.student_id}")
    job_title = app.job.title if (app and app.job) else "Placement Drive Role"
    company_name = app.job.recruiter.company_name if (app and app.job and app.job.recruiter) else "Recruiting Partner"

    return schemas.InterviewOut(
        id=it.id,
        application_id=it.application_id,
        student_id=it.student_id,
        student_name=student_name,
        job_title=job_title,
        company_name=company_name,
        drive_id=it.drive_id,
        round_name=it.round_name,
        scheduled_time=it.scheduled_time,
        interviewer_panel=it.interviewer_panel,
        status=it.status,
        feedback=it.feedback,
        technical_rating=it.technical_rating or 7.0,
        comm_rating=it.comm_rating or 7.0,
        recommendation=it.recommendation or "PROGRESS"
    )

@router.post("", response_model=schemas.InterviewOut)
def schedule_interview(
    interview_in: schemas.InterviewCreate,
    db: Session = Depends(get_db)
):
    app = db.query(models.Application).filter(models.Application.id == interview_in.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    student_id = interview_in.student_id or app.student_id
    drive_id = interview_in.drive_id or app.drive_id

    interview = models.Interview(
        application_id=app.id,
        student_id=student_id,
        drive_id=drive_id,
        round_name=interview_in.round_name,
        scheduled_time=interview_in.scheduled_time,
        interviewer_panel=interview_in.interviewer_panel,
        status=interview_in.status or "SCHEDULED",
        feedback=interview_in.feedback,
        technical_rating=interview_in.technical_rating or 7.0,
        comm_rating=interview_in.comm_rating or 7.0,
        recommendation=interview_in.recommendation or "PROGRESS"
    )
    db.add(interview)

    # Advance application stage to INTERVIEW
    app.status = "INTERVIEW"

    # Send Notification to Student
    company_name = app.job.recruiter.company_name if (app.job and app.job.recruiter) else "Recruiting Partner"
    job_title = app.job.title if app.job else "Campus Drive"
    student = app.student
    if student and student.user_id:
        notif = models.Notification(
            user_id=student.user_id,
            title=f"Interview Scheduled: {interview_in.round_name}",
            message=f"You have an interview scheduled for {job_title} at {company_name} on {interview_in.scheduled_time} ({interview_in.interviewer_panel}).",
            category="SCHEDULE"
        )
        db.add(notif)

    db.commit()
    db.refresh(interview)

    return schemas.InterviewOut(
        id=interview.id,
        application_id=interview.application_id,
        student_id=interview.student_id,
        student_name=student.name if student else f"Student #{student_id}",
        job_title=job_title,
        company_name=company_name,
        drive_id=interview.drive_id,
        round_name=interview.round_name,
        scheduled_time=interview.scheduled_time,
        interviewer_panel=interview.interviewer_panel,
        status=interview.status,
        feedback=interview.feedback,
        technical_rating=interview.technical_rating,
        comm_rating=interview.comm_rating,
        recommendation=interview.recommendation
    )

@router.put("/{interview_id}", response_model=schemas.InterviewOut)
def update_interview_evaluation(
    interview_id: int,
    updates: schemas.InterviewUpdate,
    db: Session = Depends(get_db)
):
    it = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Interview not found")

    if updates.round_name is not None:
        it.round_name = updates.round_name
    if updates.scheduled_time is not None:
        it.scheduled_time = updates.scheduled_time
    if updates.interviewer_panel is not None:
        it.interviewer_panel = updates.interviewer_panel
    if updates.status is not None:
        it.status = updates.status
    if updates.feedback is not None:
        it.feedback = updates.feedback
    if updates.technical_rating is not None:
        it.technical_rating = updates.technical_rating
    if updates.comm_rating is not None:
        it.comm_rating = updates.comm_rating
    if updates.recommendation is not None:
        it.recommendation = updates.recommendation

        # Automatically synchronize Application status based on recommendation
        if it.application:
            if updates.recommendation == "SELECT":
                it.application.status = "SELECTED"
            elif updates.recommendation == "REJECT":
                it.application.status = "REJECTED"

    # Send Notification to Student about evaluation
    app = it.application
    student = db.query(models.Student).filter(models.Student.id == it.student_id).first()
    if student and student.user_id and (updates.feedback or updates.recommendation):
        company_name = app.job.recruiter.company_name if (app and app.job and app.job.recruiter) else "Recruiter"
        rec_status = it.recommendation
        notif = models.Notification(
            user_id=student.user_id,
            title=f"Interview Feedback: {it.round_name}",
            message=f"Evaluation completed for {company_name}. Recommendation: {rec_status}. Ratings: Tech {it.technical_rating}/10, Comm {it.comm_rating}/10.",
            category="SHORTLIST" if rec_status == "SELECT" else "SYSTEM"
        )
        db.add(notif)

    db.commit()
    db.refresh(it)

    student_name = student.name if student else (app.student.name if (app and app.student) else f"Student #{it.student_id}")
    job_title = app.job.title if (app and app.job) else "Placement Drive Role"
    company_name = app.job.recruiter.company_name if (app and app.job and app.job.recruiter) else "Recruiting Partner"

    return schemas.InterviewOut(
        id=it.id,
        application_id=it.application_id,
        student_id=it.student_id,
        student_name=student_name,
        job_title=job_title,
        company_name=company_name,
        drive_id=it.drive_id,
        round_name=it.round_name,
        scheduled_time=it.scheduled_time,
        interviewer_panel=it.interviewer_panel,
        status=it.status,
        feedback=it.feedback,
        technical_rating=it.technical_rating,
        comm_rating=it.comm_rating,
        recommendation=it.recommendation
    )

@router.delete("/{interview_id}")
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    it = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Interview not found")
    db.delete(it)
    db.commit()
    return {"message": f"Interview #{interview_id} successfully cancelled and removed."}
