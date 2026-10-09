from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: str
    email: str
    profile_id: Optional[int] = None

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    email: str
    name: str
    role: str

class UserCreate(UserBase):
    password: str
    branch: Optional[str] = "CSE"
    cgpa: Optional[float] = 7.0
    company_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class StudentOut(BaseModel):
    id: int
    user_id: int
    student_id: str
    name: str
    email: str
    phone: Optional[str] = None
    branch: str
    semester: int
    cgpa: float
    backlogs: int
    academic_history: Optional[str] = None
    technical_skills: Optional[str] = None
    soft_skills: Optional[str] = None
    certifications: Optional[str] = None
    projects: Optional[str] = None
    internship_experience: Optional[str] = None
    resume_url: Optional[str] = None
    aptitude_score: float
    coding_score: float
    tech_assessment_score: float
    communication_score: float
    mock_interview_score: float
    readiness_score: float
    readiness_class: str
    readiness_factors: Optional[str] = None
    improvement_areas: Optional[str] = None
    at_risk_level: str
    at_risk_reasons: Optional[str] = None
    recommendations: Optional[str] = None

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    phone: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    backlogs: Optional[int] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    internship_experience: Optional[str] = None

class RecruiterOut(BaseModel):
    id: int
    company_name: str
    contact_person: Optional[str] = None
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    description: str
    min_cgpa: float = 6.0
    eligible_branches: List[str] = ["CSE", "IT"]
    required_skills: List[str] = ["Java", "SQL"]
    preferred_skills: List[str] = []
    required_certifications: List[str] = []
    ctc_lpa: float = 6.5
    location: str = "Bangalore / Hybrid"
    job_type: str = "Full Time"
    deadline: Optional[str] = None

class JobOut(BaseModel):
    id: int
    recruiter_id: int
    title: str
    description: str
    min_cgpa: float
    eligible_branches: str
    required_skills: str
    preferred_skills: str
    required_certifications: str
    ctc_lpa: float
    location: str
    job_type: str
    deadline: Optional[str] = None
    is_active: bool
    extracted_requirements: Optional[str] = None

    class Config:
        from_attributes = True

class DriveCreate(BaseModel):
    job_id: Optional[int] = None
    company_name: str
    role_title: str
    drive_date: str # YYYY-MM-DD
    start_time: str # HH:MM e.g. "10:00 AM"
    end_time: str   # HH:MM e.g. "01:00 PM"
    venue: str = "Seminar Hall 1"
    panel_name: str = "Panel A"
    eligibility_criteria: Optional[str] = None

class DriveOut(BaseModel):
    id: int
    job_id: Optional[int] = None
    company_name: str
    role_title: str
    drive_date: str
    start_time: str
    end_time: str
    venue: str
    panel_name: str
    eligibility_criteria: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_id: int
    drive_id: Optional[int] = None

class ApplicationUpdateStatus(BaseModel):
    status: str

class ApplicationOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    drive_id: Optional[int] = None
    status: str
    match_score: float
    match_explanation: Optional[str] = None
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OfferCreate(BaseModel):
    application_id: Optional[int] = None
    student_id: int
    recruiter_id: Optional[int] = None
    job_id: Optional[int] = None
    company_name: str
    role_title: str
    ctc_lpa: float
    offer_date: str
    offer_letter_url: Optional[str] = None
    joining_date: Optional[str] = None
    remarks: Optional[str] = None

class OfferUpdate(BaseModel):
    acceptance_status: Optional[str] = None
    joining_status: Optional[str] = None
    documentation_status: Optional[str] = None
    joining_date: Optional[str] = None
    remarks: Optional[str] = None

class OfferOut(BaseModel):
    id: int
    application_id: Optional[int] = None
    student_id: int
    company_name: str
    role_title: str
    ctc_lpa: float
    offer_date: str
    offer_letter_url: Optional[str] = None
    acceptance_status: str
    joining_date: Optional[str] = None
    joining_status: str
    documentation_status: str
    remarks: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    category: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    student_id: int
    doc_type: str
    title: str
    file_url: str
    status: str
    verified_by: Optional[str] = None
    remarks: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    student_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str] = []

class InterviewCreate(BaseModel):
    application_id: int
    student_id: Optional[int] = None
    drive_id: Optional[int] = None
    round_name: str = "Technical Round 1"
    scheduled_time: str # e.g. "2026-10-15 10:30 AM"
    interviewer_panel: str = "Panel A - Technical"
    status: str = "SCHEDULED"
    feedback: Optional[str] = None
    technical_rating: Optional[float] = 7.0
    comm_rating: Optional[float] = 7.0
    recommendation: Optional[str] = "PROGRESS"

class InterviewUpdate(BaseModel):
    round_name: Optional[str] = None
    scheduled_time: Optional[str] = None
    interviewer_panel: Optional[str] = None
    status: Optional[str] = None
    feedback: Optional[str] = None
    technical_rating: Optional[float] = None
    comm_rating: Optional[float] = None
    recommendation: Optional[str] = None

class InterviewOut(BaseModel):
    id: int
    application_id: int
    student_id: int
    student_name: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    drive_id: Optional[int] = None
    round_name: str
    scheduled_time: str
    interviewer_panel: str
    status: str
    feedback: Optional[str] = None
    technical_rating: float
    comm_rating: float
    recommendation: str

    class Config:
        from_attributes = True

