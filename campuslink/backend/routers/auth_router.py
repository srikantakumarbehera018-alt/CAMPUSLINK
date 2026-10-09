from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from database import get_db
import models
import schemas
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user_role = (user_in.role or "STUDENT").replace("ROLE_", "").upper()
    user_name = (user_in.name or user_in.username or user_in.email.split("@")[0]).strip()

    user = models.User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_role,
        name=user_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile_id = None
    if user.role == "STUDENT":
        # Create student record
        roll = f"STU-{user.id:04d}"
        stu = models.Student(
            user_id=user.id,
            student_id=roll,
            name=user.name,
            email=user.email,
            branch=user_in.branch or "CSE",
            cgpa=user_in.cgpa or 7.0,
            technical_skills=json.dumps(["Java", "SQL", "Git"]),
            soft_skills=json.dumps(["Communication", "Teamwork"]),
            projects=json.dumps([]),
            certifications=json.dumps([])
        )
        db.add(stu)
        db.commit()
        db.refresh(stu)
        profile_id = stu.id

    elif user.role == "RECRUITER":
        rec = models.Recruiter(
            user_id=user.id,
            company_name=user_in.company_name or f"{user.name}'s Corp",
            email=user.email,
            contact_person=user.name
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        profile_id = rec.id

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": token,
        "token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "id": user.id,
        "name": user.name,
        "username": user.name,
        "email": user.email,
        "profile_id": profile_id
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    login_identifier = (login_data.email or login_data.username or "").strip()
    user = db.query(models.User).filter(models.User.email == login_identifier).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    profile_id = None
    if user.role == "STUDENT" and user.student_profile:
        profile_id = user.student_profile.id
    elif user.role == "RECRUITER" and user.recruiter_profile:
        profile_id = user.recruiter_profile.id

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": token,
        "token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "id": user.id,
        "name": user.name,
        "username": user.name,
        "email": user.email,
        "profile_id": profile_id
    }

@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_id = None
    if current_user.role == "STUDENT" and current_user.student_profile:
        profile_id = current_user.student_profile.id
    elif current_user.role == "RECRUITER" and current_user.recruiter_profile:
        profile_id = current_user.recruiter_profile.id

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "profile_id": profile_id
    }
