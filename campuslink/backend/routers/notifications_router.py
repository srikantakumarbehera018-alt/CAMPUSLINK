from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[schemas.NotificationOut])
def get_user_notifications(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs

@router.put("/{notif_id}/read")
def mark_notification_read(notif_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notif_id,
        models.Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.put("/read-all")
def mark_all_notifications_read(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

@router.post("")
def create_custom_notification(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get("user_id")
    title = payload.get("title", "Placement Notice")
    message = payload.get("message", "")
    category = payload.get("category", "SYSTEM")

    notif = models.Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return {"message": "Notification dispatched successfully", "notification_id": notif.id}
