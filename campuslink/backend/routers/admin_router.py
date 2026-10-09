from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db
import models
import schemas
from auth import get_current_user, require_role, hash_password
from ai_engine import AIEngine

router = APIRouter(prefix="/admin", tags=["Placement Cell & TPO Admin"])

@router.get("/applications")
def get_all_applications(status: Optional[str] = None, job_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Application)
    if status and status != "ALL":
        query = query.filter(models.Application.status == status)
    if job_id:
        query = query.filter(models.Application.job_id == job_id)

    apps = query.order_by(models.Application.updated_at.desc()).all()
    results = []
    for a in apps:
        exp = json.loads(a.match_explanation or "{}") if a.match_explanation else {}
        results.append({
            "id": a.id,
            "student_id": a.student_id,
            "student_name": a.student.name if a.student else "Unknown",
            "student_roll": a.student.student_id if a.student else "",
            "branch": a.student.branch if a.student else "",
            "cgpa": a.student.cgpa if a.student else 0.0,
            "job_id": a.job_id,
            "job_title": a.job.title if a.job else "Unknown",
            "company_name": a.job.recruiter.company_name if (a.job and a.job.recruiter) else "Unknown",
            "drive_id": a.drive_id,
            "status": a.status,
            "match_score": a.match_score,
            "applied_at": a.applied_at,
            "explanation": exp
        })
    return results

@router.put("/applications/{app_id}/status")
def update_application_status(app_id: int, payload: dict, db: Session = Depends(get_db)):
    """Advances candidate through the placement pipeline."""
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing status")

    app.status = new_status
    
    # Notify student
    notif = models.Notification(
        user_id=app.student.user_id,
        title=f"Application Status Updated: {app.job.title}",
        message=f"Your application status for {app.job.title} at {app.job.recruiter.company_name} is now: {new_status.replace('_', ' ')}.",
        category="SHORTLIST" if "SHORTLIST" in new_status else ("OFFER" if "OFFER" in new_status else "SYSTEM")
    )
    db.add(notif)
    db.commit()

    return {"message": f"Application status updated to {new_status}", "application_id": app.id, "status": app.status}

@router.get("/offers", response_model=List[schemas.OfferOut])
def get_all_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).order_by(models.Offer.id.desc()).all()

@router.post("/offers", response_model=schemas.OfferOut)
def create_offer(offer_in: schemas.OfferCreate, db: Session = Depends(get_db)):
    stu = db.query(models.Student).filter(models.Student.id == offer_in.student_id).first()
    if not stu:
        raise HTTPException(status_code=404, detail="Student not found")

    offer = models.Offer(
        application_id=offer_in.application_id,
        student_id=offer_in.student_id,
        recruiter_id=offer_in.recruiter_id,
        job_id=offer_in.job_id,
        company_name=offer_in.company_name,
        role_title=offer_in.role_title,
        ctc_lpa=offer_in.ctc_lpa,
        offer_date=offer_in.offer_date,
        offer_letter_url=offer_in.offer_letter_url or f"/uploads/Offer_{stu.name.replace(' ', '_')}.pdf",
        acceptance_status="PENDING",
        joining_date=offer_in.joining_date or "2026-12-01",
        joining_status="PENDING",
        documentation_status="PENDING",
        remarks=offer_in.remarks or "Congratulations on your selection!"
    )
    db.add(offer)

    # Notify student
    notif = models.Notification(
        user_id=stu.user_id,
        title=f"Official Placement Offer: {offer_in.company_name}",
        message=f"Congratulations! You have received an offer for {offer_in.role_title} with CTC ₹{offer_in.ctc_lpa} LPA. Please review and accept.",
        category="OFFER"
    )
    db.add(notif)

    # Update application status if linked
    if offer_in.application_id:
        app = db.query(models.Application).filter(models.Application.id == offer_in.application_id).first()
        if app:
            app.status = "OFFER_GENERATED"

    db.commit()
    db.refresh(offer)
    return offer

@router.put("/offers/{offer_id}", response_model=schemas.OfferOut)
def update_offer(offer_id: int, updates: schemas.OfferUpdate, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if updates.acceptance_status is not None:
        offer.acceptance_status = updates.acceptance_status
    if updates.joining_status is not None:
        offer.joining_status = updates.joining_status
    if updates.documentation_status is not None:
        offer.documentation_status = updates.documentation_status
    if updates.joining_date is not None:
        offer.joining_date = updates.joining_date
    if updates.remarks is not None:
        offer.remarks = updates.remarks

    # If linked to application, reflect status
    if offer.application:
        if offer.acceptance_status == "ACCEPTED":
            offer.application.status = "OFFER_ACCEPTED"
        if offer.joining_status == "JOINED":
            offer.application.status = "JOINED"

    db.commit()
    db.refresh(offer)
    return offer

@router.get("/documents", response_model=List[schemas.DocumentOut])
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.id.desc()).all()

@router.put("/documents/{doc_id}/status")
def update_document_status(doc_id: int, payload: dict, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    status_val = payload.get("status", "VERIFIED")
    doc.status = status_val
    doc.verified_by = payload.get("verified_by", "TPO Office")
    if "remarks" in payload:
        doc.remarks = payload["remarks"]

    db.commit()
    return {"message": f"Document status updated to {status_val}", "document_id": doc.id}

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    stu = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not stu:
        raise HTTPException(status_code=404, detail="Student not found")

    user_id = stu.user_id
    db.delete(stu)
    usr = db.query(models.User).filter(models.User.id == user_id).first()
    if usr:
        db.delete(usr)

    db.commit()
    return {"message": f"Student #{student_id} successfully deleted"}
