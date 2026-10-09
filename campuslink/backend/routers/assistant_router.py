from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import re

from database import get_db
import models
import schemas
from ai_engine import AIEngine

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

@router.post("/chat", response_model=schemas.ChatResponse)
def assistant_chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    msg = (request.message or request.prompt or "").strip().lower()
    student_id = request.student_id or 1

    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        student = db.query(models.Student).first()

    jobs = db.query(models.Job).filter(models.Job.is_active == True).all()
    drives = db.query(models.PlacementDrive).all()

    try:
        stu_skills = json.loads(student.technical_skills or '[]')
    except Exception:
        stu_skills = []

    # 1. Eligibility Check (e.g. "Am I eligible for TechNova?" or "Am I eligible for CodeSphere?")
    matched_job = None
    for j in jobs:
        comp_name = (j.recruiter.company_name or "").lower()
        job_title = (j.title or "").lower()
        if any(word in msg for word in comp_name.split()) or any(word in msg for word in job_title.split()):
            matched_job = j
            break

    if "eligible" in msg or "eligibility" in msg:
        if matched_job:
            match_res = AIEngine.calculate_hybrid_match(student, matched_job)
            eligible_str = "Eligible" if match_res["is_eligible"] else "Not Eligible"
            reasons = "; ".join(match_res["positive_reasons"])
            missing = ", ".join(match_res["missing_skills"]) if match_res["missing_skills"] else "None"
            reply = (
                f"**Eligibility Check for {matched_job.title} at {matched_job.recruiter.company_name}:**\n\n"
                f"• **Status:** {eligible_str}\n"
                f"• **Estimated Fit Score:** {match_res['fit_score']}/100\n"
                f"• **Your CGPA:** {student.cgpa} (Cutoff: {matched_job.min_cgpa})\n"
                f"• **Your Branch:** {student.branch}\n"
                f"• **Positive Factors:** {reasons}\n"
                f"• **Missing Skills:** {missing}\n\n"
                f"_{match_res['recommendation']}_"
            )
            return {
                "reply": reply,
                "suggested_actions": [f"Apply to {matched_job.title}", "Review Skill Gaps", "Check Drive Schedule"]
            }
        else:
            # General eligibility
            open_jobs = []
            for j in jobs:
                res = AIEngine.calculate_hybrid_match(student, j)
                if res["is_eligible"]:
                    open_jobs.append(f"{j.title} ({j.recruiter.company_name} - {res['fit_score']}%)")

            reply = (
                f"Based on your profile (CGPA {student.cgpa}, Branch: {student.branch}), you are currently eligible for {len(open_jobs)} active opportunities:\n\n"
                + "\n".join([f"• {x}" for x in open_jobs[:4]])
                + "\n\nWould you like a detailed breakdown for any specific company?"
            )
            return {
                "reply": reply,
                "suggested_actions": ["Am I eligible for TechNova?", "Which drives match my profile?", "How to improve readiness?"]
            }

    # 2. Skill Gaps (e.g. "What skills am I missing for Java Developer?")
    if "missing" in msg or "skill gap" in msg or "skills for" in msg or "need to learn" in msg:
        target_role = "Java Backend Developer"
        req_skills = ["Java", "Spring Boot", "SQL", "REST API", "Git", "Docker"]
        
        # Check if asked about specific role
        if matched_job:
            target_role = matched_job.title
            try:
                req_skills = json.loads(matched_job.required_skills or '[]')
            except Exception:
                pass

        gap = AIEngine.analyze_skill_gap(stu_skills, req_skills)
        reply = (
            f"**Skill Gap Analysis for {target_role}:**\n\n"
            f"✓ **Skills You Have:** {', '.join(gap['available_skills']) if gap['available_skills'] else 'None'}\n\n"
            f"✗ **Missing Requirements:** {', '.join(gap['missing_skills']) if gap['missing_skills'] else 'None'}\n\n"
            f"**Recommended Action Plan:**\n"
            + "\n".join([f"{i+1}. {r}" for i, r in enumerate(gap['personalized_recommendations'])])
        )
        return {
            "reply": reply,
            "suggested_actions": ["Show Recommended Preparation", "Check Job Matches", "Update Resume Skills"]
        }

    # 3. Readiness Improvement (e.g. "How can I improve my readiness score?")
    if "readiness" in msg or "improve" in msg or "score" in msg:
        readiness_info = AIEngine.calculate_readiness_score(student)
        reply = (
            f"**Your Current Placement Readiness Score: {student.readiness_score}/100 ({student.readiness_class})**\n\n"
            f"**Key Strengths:**\n"
            + "\n".join([f"✓ {p}" for p in readiness_info['positive_factors'][:3]])
            + "\n\n**Highest Priority Improvement Areas:**\n"
            + "\n".join([f"• {a}" for a in readiness_info['improvement_areas'][:3]])
            + "\n\n**Recommended 7-Day Plan:**\n"
            f"1. Complete 15 timed aptitude tests on quantitative topics.\n"
            f"2. Add a deployed project link to your resume.\n"
            f"3. Attend a TPO peer mock interview session."
        )
        return {
            "reply": reply,
            "suggested_actions": ["Upload Updated Resume", "Take Practice Assessment", "Check At-Risk Status"]
        }

    # 4. Matching Drives (e.g. "Which drives match my profile?" or "Which companies can I apply to?")
    if "drive" in msg or "match" in msg or "companies" in msg or "apply" in msg:
        matches = []
        for j in jobs:
            m = AIEngine.calculate_hybrid_match(student, j)
            matches.append((j, m))
        matches.sort(key=lambda x: x[1]["fit_score"], reverse=True)

        top_3 = matches[:3]
        lines = []
        for j, m in top_3:
            lines.append(f"• **{j.title}** at **{j.recruiter.company_name}** — **Fit: {m['fit_score']}%** (CTC: ₹{j.ctc_lpa} LPA)")

        reply = (
            f"Here are the top active campus placement drives best matched to your profile:\n\n"
            + "\n".join(lines)
            + "\n\nAll recommendations are based on your CGPA, technical skills, and project relevance."
        )
        return {
            "reply": reply,
            "suggested_actions": ["Apply to Top Match", "Am I eligible for TechNova?", "Analyze My Resume"]
        }

    # Default Helpful Guidance
    reply = (
        f"Hello **{student.name}**! I'm your **CAMPUSLINK AI Assistant**.\n\n"
        f"You can ask me questions such as:\n"
        f"• *'Am I eligible for TechNova?'*\n"
        f"• *'What skills am I missing for a Java Developer?'*\n"
        f"• *'Which drives match my profile?'*\n"
        f"• *'How can I improve my readiness score?'*\n\n"
        f"How can I assist your placement preparation today?"
    )
    return {
        "reply": reply,
        "suggested_actions": ["Am I eligible for TechNova?", "Which drives match my profile?", "How to improve readiness?"]
    }
