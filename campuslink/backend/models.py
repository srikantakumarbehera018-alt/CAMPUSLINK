from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # STUDENT, RECRUITER, TPO_ADMIN
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    recruiter_profile = relationship("Recruiter", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "CS2024-001"
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    branch = Column(String(50), nullable=False)  # CSE, ECE, EEE, ME, Civil, IT
    semester = Column(Integer, default=7)
    cgpa = Column(Float, nullable=False, default=7.0)
    backlogs = Column(Integer, default=0)
    
    academic_history = Column(Text, nullable=True)  # JSON or text
    technical_skills = Column(Text, nullable=True)  # JSON array of strings
    soft_skills = Column(Text, nullable=True)       # JSON array of strings
    certifications = Column(Text, nullable=True)     # JSON array of strings/objects
    projects = Column(Text, nullable=True)           # JSON array of project objects
    internship_experience = Column(Text, nullable=True) # JSON or text
    
    resume_url = Column(String(500), nullable=True)
    resume_text = Column(Text, nullable=True)
    
    # Assessment Scores (0 - 100)
    aptitude_score = Column(Float, default=70.0)
    coding_score = Column(Float, default=70.0)
    tech_assessment_score = Column(Float, default=70.0)
    communication_score = Column(Float, default=70.0)
    mock_interview_score = Column(Float, default=70.0)
    
    # AI Calculated Readiness Metrics
    readiness_score = Column(Float, default=70.0)
    readiness_class = Column(String(50), default="Ready")  # Not Ready, Developing, Ready, Highly Employable
    readiness_factors = Column(Text, nullable=True)  # JSON array of positive points
    improvement_areas = Column(Text, nullable=True)  # JSON array of improvement items
    
    # At-Risk Prediction
    at_risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    at_risk_reasons = Column(Text, nullable=True)      # JSON array
    recommendations = Column(Text, nullable=True)      # JSON object / recommendations

    # Relationships
    user = relationship("User", back_populates="student_profile")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="student", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="student", cascade="all, delete-orphan")


class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), default="Information Technology")
    description = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="recruiter_profile")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="recruiter")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    min_cgpa = Column(Float, default=6.0)
    eligible_branches = Column(Text, default='["CSE","IT"]') # JSON array
    required_skills = Column(Text, default='["Java","SQL"]') # JSON array
    preferred_skills = Column(Text, default='[]')           # JSON array
    required_certifications = Column(Text, default='[]')    # JSON array
    ctc_lpa = Column(Float, default=6.5)
    location = Column(String(255), default="Bangalore / Hybrid")
    job_type = Column(String(100), default="Full Time")
    deadline = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    extracted_requirements = Column(Text, nullable=True)    # JSON NLP extracted

    # Relationships
    recruiter = relationship("Recruiter", back_populates="jobs")
    drives = relationship("PlacementDrive", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    company_name = Column(String(255), nullable=False)
    role_title = Column(String(255), nullable=False)
    drive_date = Column(String(50), nullable=False)  # YYYY-MM-DD
    start_time = Column(String(20), nullable=False)  # HH:MM e.g. 10:00 AM
    end_time = Column(String(20), nullable=False)    # HH:MM e.g. 01:00 PM
    venue = Column(String(255), default="Seminar Hall 1")
    panel_name = Column(String(255), default="Panel A - Technical")
    eligibility_criteria = Column(Text, nullable=True)
    status = Column(String(50), default="SCHEDULED") # UPCOMING, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="drives")
    applications = relationship("Application", back_populates="drive")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    drive_id = Column(Integer, ForeignKey("placement_drives.id"), nullable=True)
    
    # Pipeline stages: APPLIED, ELIGIBLE, AI_SHORTLISTED, ASSESSMENT, INTERVIEW, SELECTED, OFFER_GENERATED, OFFER_ACCEPTED, JOINING_PENDING, JOINED, REJECTED, WITHDRAWN
    status = Column(String(50), default="APPLIED")
    
    match_score = Column(Float, default=0.0)
    match_explanation = Column(Text, nullable=True) # JSON: reasons, missing_skills, recommendations
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    drive = relationship("PlacementDrive", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    offer = relationship("Offer", back_populates="application", uselist=False)


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    student_id = Column(Integer, nullable=False)
    drive_id = Column(Integer, nullable=True)
    round_name = Column(String(100), default="Technical Round 1")
    scheduled_time = Column(String(50), nullable=False)
    interviewer_panel = Column(String(255), default="Panel A")
    status = Column(String(50), default="SCHEDULED") # SCHEDULED, COMPLETED, CANCELLED
    feedback = Column(Text, nullable=True)
    technical_rating = Column(Float, default=7.0)
    comm_rating = Column(Float, default=7.0)
    recommendation = Column(String(50), default="PROGRESS") # PROGRESS, REJECT, SELECT

    # Relationships
    application = relationship("Application", back_populates="interviews")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    company_name = Column(String(255), nullable=False)
    role_title = Column(String(255), nullable=False)
    ctc_lpa = Column(Float, nullable=False)
    offer_date = Column(String(50), nullable=False)
    offer_letter_url = Column(String(500), nullable=True)
    
    # Statuses: PENDING, ACCEPTED, REJECTED, WITHDRAWN
    acceptance_status = Column(String(50), default="PENDING")
    
    joining_date = Column(String(50), nullable=True)
    
    # Statuses: PENDING, JOINED, DECLINED
    joining_status = Column(String(50), default="PENDING")
    
    # Statuses: SUBMITTED, VERIFIED, PENDING, REJECTED
    documentation_status = Column(String(50), default="PENDING")
    remarks = Column(Text, nullable=True)

    # Relationships
    application = relationship("Application", back_populates="offer")
    student = relationship("Student", back_populates="offers")
    recruiter = relationship("Recruiter", back_populates="offers")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    doc_type = Column(String(50), nullable=False) # RESUME, ID_PROOF, ACADEMIC_DOC, CERTIFICATE, OFFER_LETTER, JOINING_DOC
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    status = Column(String(50), default="PENDING") # SUBMITTED, PENDING, VERIFIED, REJECTED
    verified_by = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="documents")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="SYSTEM") # SHORTLIST, SCHEDULE, DEADLINE, OFFER, SKILL_GAP, SYSTEM
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    capacity = Column(Integer, default=100)
    location = Column(String(255), default="Main Academic Block")
    is_available = Column(Boolean, default=True)


class InterviewPanel(Base):
    __tablename__ = "interview_panels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    department = Column(String(100), default="CSE / Placement Cell")
    members = Column(Text, default="Prof. Sharma, Dr. Rao")
    max_parallel_drives = Column(Integer, default=1)
