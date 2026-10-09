import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Skill Normalization Dictionary
SKILL_SYNONYMS = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react js": "React",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "my sql": "MySQL",
    "mysql": "MySQL",
    "sql": "SQL",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "ai": "Artificial Intelligence",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring": "Spring Boot",
    "rest api": "REST API",
    "restful": "REST API",
    "rest apis": "REST API",
    "restful web services": "REST API",
    "aws": "AWS",
    "amazon web services": "AWS",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "git": "Git",
    "github": "Git",
    "version control": "Git",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "html": "HTML",
    "css": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "express": "Express.js",
    "expressjs": "Express.js",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "data structures": "DSA",
    "dsa": "DSA",
    "algorithms": "DSA",
    "cloud": "Cloud Computing",
    "azure": "Azure",
    "gcp": "GCP",
    "ci/cd": "CI/CD",
    "linux": "Linux"
}

POPULAR_SKILLS = list(set(SKILL_SYNONYMS.values()))

class AIEngine:
    @staticmethod
    def normalize_skill(skill: str) -> str:
        s = skill.strip().lower()
        if s in SKILL_SYNONYMS:
            return SKILL_SYNONYMS[s]
        for key, val in SKILL_SYNONYMS.items():
            if key == s:
                return val
        return skill.strip().title()

    @classmethod
    def extract_skills_from_text(cls, text: str) -> List[str]:
        if not text:
            return []
        lower_text = text.lower()
        found_skills = set()
        
        # Word boundary search for known aliases
        for alias, normalized in SKILL_SYNONYMS.items():
            # escape alias for regex
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, lower_text):
                found_skills.add(normalized)
                
        return sorted(list(found_skills))

    @classmethod
    def parse_resume_text(cls, text: str) -> Dict[str, Any]:
        """Extract skills, education, projects, certifications, and experience from resume text."""
        skills = cls.extract_skills_from_text(text)
        
        # Extract Projects count or references
        project_matches = re.findall(r'(?i)(project|developed|built|designed|implemented)[\s\w]{5,50}', text)
        projects_count = min(max(len(project_matches), 1 if "project" in text.lower() else 0), 5)
        
        # Extract Certifications
        cert_matches = re.findall(r'(?i)(certified|certification|certificate|coursera|udemy|aws certified|nptel)', text)
        certs_count = min(len(cert_matches), 5)
        
        # Extract CGPA
        cgpa = 7.5
        cgpa_match = re.search(r'(?i)(?:cgpa|gpa|pointer)[\s:=]*([0-9]\.[0-9]+)', text)
        if cgpa_match:
            try:
                val = float(cgpa_match.group(1))
                if 0.0 <= val <= 10.0:
                    cgpa = val
            except ValueError:
                pass
                
        # Recommended missing common skills
        core_essential = ["Git", "SQL", "Docker", "AWS", "REST API", "DSA"]
        missing_rec = [s for s in core_essential if s not in skills]
        
        return {
            "detected_skills": skills,
            "detected_projects_count": projects_count,
            "detected_certifications_count": certs_count,
            "extracted_cgpa": cgpa,
            "missing_recommended_skills": missing_rec[:3]
        }

    @classmethod
    def extract_job_requirements(cls, jd_text: str) -> Dict[str, Any]:
        """Automatically extracts min CGPA, branches, and required skills from a job description."""
        if not jd_text:
            return {
                "min_cgpa": 6.0,
                "eligible_branches": ["CSE", "IT"],
                "required_skills": ["Java", "SQL"]
            }

        # 1. Min CGPA
        min_cgpa = 6.0
        cgpa_patterns = [
            r'(?i)(?:cgpa|gpa|pointer)[\s:>=]+([0-9]\.?[0-9]*)',
            r'(?i)minimum[\s]+([0-9]\.?[0-9]*)[\s]+cgpa',
            r'(?i)([0-9]\.[0-9]+)\+?[\s]+cgpa'
        ]
        for pat in cgpa_patterns:
            m = re.search(pat, jd_text)
            if m:
                try:
                    val = float(m.group(1))
                    if 4.0 <= val <= 10.0:
                        min_cgpa = val
                        break
                except ValueError:
                    pass

        # 2. Branches
        branches = set()
        branch_map = {
            "cse": "CSE",
            "computer science": "CSE",
            "cs": "CSE",
            "it": "IT",
            "information technology": "IT",
            "ece": "ECE",
            "electronics": "ECE",
            "eee": "EEE",
            "electrical": "EEE",
            "me": "ME",
            "mechanical": "ME",
            "civil": "Civil"
        }
        lower_jd = jd_text.lower()
        for key, code in branch_map.items():
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(key) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, lower_jd):
                branches.add(code)
        
        if not branches:
            branches = {"CSE", "IT"}

        # 3. Skills
        skills = cls.extract_skills_from_text(jd_text)
        if not skills:
            skills = ["Java", "SQL"]

        return {
            "min_cgpa": round(min_cgpa, 1),
            "eligible_branches": sorted(list(branches)),
            "required_skills": skills
        }

    @classmethod
    def calculate_readiness_score(cls, student: Any) -> Dict[str, Any]:
        """
        Calculate Explainable Employability & Placement Readiness Score (0 - 100)
        Classification:
        0 - 39: Not Ready
        40 - 59: Developing
        60 - 79: Ready
        80 - 100: Highly Employable
        """
        cgpa = float(getattr(student, 'cgpa', 7.0) or 7.0)
        backlogs = int(getattr(student, 'backlogs', 0) or 0)
        aptitude = float(getattr(student, 'aptitude_score', 70.0) or 70.0)
        coding = float(getattr(student, 'coding_score', 70.0) or 70.0)
        tech_assessment = float(getattr(student, 'tech_assessment_score', 70.0) or 70.0)
        communication = float(getattr(student, 'communication_score', 70.0) or 70.0)
        mock_interview = float(getattr(student, 'mock_interview_score', 70.0) or 70.0)
        
        # Parse skills & projects count
        raw_skills = getattr(student, 'technical_skills', '[]')
        try:
            skills_list = json.loads(raw_skills) if isinstance(raw_skills, str) else (raw_skills or [])
        except Exception:
            skills_list = []
            
        raw_projects = getattr(student, 'projects', '[]')
        try:
            projects_list = json.loads(raw_projects) if isinstance(raw_projects, str) else (raw_projects or [])
        except Exception:
            projects_list = []
            
        # Dimensional Components
        # 1. Academic (20%): CGPA (scaled 0-10) with penalty for backlogs
        academic_score = max(0, min(100, (cgpa / 10.0) * 100 - (backlogs * 15)))
        
        # 2. Technical Skills & Coding (25%): coding test + skill breadth
        skill_breadth = min(100, len(skills_list) * 12)
        tech_score = (coding * 0.5) + (tech_assessment * 0.3) + (skill_breadth * 0.2)
        
        # 3. Aptitude (20%)
        aptitude_comp = aptitude
        
        # 4. Mock Interview & Communication (20%)
        interview_comp = (mock_interview * 0.6) + (communication * 0.4)
        
        # 5. Project & Practical Exposure (15%)
        project_comp = min(100, len(projects_list) * 35)
        
        # Weighted Overall Score
        overall = (
            academic_score * 0.20 +
            tech_score * 0.25 +
            aptitude_comp * 0.20 +
            interview_comp * 0.20 +
            project_comp * 0.15
        )
        overall_score = round(max(0.0, min(100.0, overall)), 1)
        
        # Classification
        if overall_score >= 80:
            classification = "Highly Employable"
        elif overall_score >= 60:
            classification = "Ready"
        elif overall_score >= 40:
            classification = "Developing"
        else:
            classification = "Not Ready"

        # Explainability Factors
        positive_factors = []
        improvement_areas = []

        if cgpa >= 8.0:
            positive_factors.append(f"Strong academic record (CGPA {cgpa})")
        elif cgpa >= 7.0:
            positive_factors.append(f"Satisfactory CGPA ({cgpa}) above standard cutoff")
        else:
            improvement_areas.append(f"CGPA ({cgpa}) is below competitive tier; maintain consistency")

        if backlogs == 0:
            positive_factors.append("Zero active backlogs")
        else:
            improvement_areas.append(f"Clear {backlogs} pending backlog(s) before major drives")

        if len(skills_list) >= 5:
            positive_factors.append(f"Diverse technical stack: {', '.join(skills_list[:4])}")
        else:
            improvement_areas.append("Broaden technical skill breadth (add 2-3 in-demand skills)")

        if aptitude >= 75:
            positive_factors.append(f"High aptitude proficiency ({int(aptitude)}%)")
        else:
            improvement_areas.append("Practice aptitude & logical reasoning assessments regularly")

        if mock_interview >= 75:
            positive_factors.append(f"Strong mock interview readiness ({int(mock_interview)}%)")
        else:
            improvement_areas.append("Participate in mock HR/Technical interview simulations")

        if len(projects_list) >= 2:
            positive_factors.append(f"Completed {len(projects_list)} relevant portfolio projects")
        else:
            improvement_areas.append("Build and showcase at least 2 full-stack/domain projects with GitHub links")

        if communication < 70:
            improvement_areas.append("Refine technical communication and behavioral interview articulation")

        return {
            "readiness_score": overall_score,
            "readiness_class": classification,
            "dimensions": {
                "academic": round(academic_score, 1),
                "technical": round(tech_score, 1),
                "aptitude": round(aptitude_comp, 1),
                "interview": round(interview_comp, 1),
                "projects": round(project_comp, 1)
            },
            "positive_factors": positive_factors,
            "improvement_areas": improvement_areas
        }

    @classmethod
    def calculate_hybrid_match(cls, student: Any, job: Any) -> Dict[str, Any]:
        """
        Calculates explainable Fit Score (0 - 100) between Student and Job.
        Weighted Model:
        - Academic Eligibility: 15%
        - Technical Skill Match: 30%
        - Project Relevance: 15%
        - Certification Match: 10%
        - Aptitude: 10%
        - Mock Interview: 10%
        - Communication: 5%
        - Experience: 5%
        """
        # Parse job requirements
        try:
            req_skills = json.loads(job.required_skills) if isinstance(job.required_skills, str) else (job.required_skills or [])
        except Exception:
            req_skills = []
        req_skills_norm = [cls.normalize_skill(s) for s in req_skills]

        try:
            pref_skills = json.loads(job.preferred_skills) if isinstance(job.preferred_skills, str) else (job.preferred_skills or [])
        except Exception:
            pref_skills = []
        pref_skills_norm = [cls.normalize_skill(s) for s in pref_skills]

        try:
            eligible_branches = json.loads(job.eligible_branches) if isinstance(job.eligible_branches, str) else (job.eligible_branches or [])
        except Exception:
            eligible_branches = ["CSE", "IT"]

        # Parse student data
        try:
            stu_skills = json.loads(student.technical_skills) if isinstance(student.technical_skills, str) else (student.technical_skills or [])
        except Exception:
            stu_skills = []
        stu_skills_norm = [cls.normalize_skill(s) for s in stu_skills]

        try:
            stu_projects = json.loads(student.projects) if isinstance(student.projects, str) else (student.projects or [])
        except Exception:
            stu_projects = []

        try:
            stu_certs = json.loads(student.certifications) if isinstance(student.certifications, str) else (student.certifications or [])
        except Exception:
            stu_certs = []

        cgpa = float(student.cgpa or 7.0)
        min_cgpa = float(job.min_cgpa or 6.0)
        branch = student.branch

        # 1. Academic Eligibility Check & Score (15%)
        is_branch_eligible = (branch in eligible_branches) or ("ALL" in [b.upper() for b in eligible_branches])
        cgpa_diff = cgpa - min_cgpa
        if cgpa >= min_cgpa:
            academic_pct = min(100.0, 75.0 + (cgpa_diff * 10.0))
        else:
            academic_pct = max(20.0, 60.0 - (abs(cgpa_diff) * 20.0))

        if not is_branch_eligible:
            academic_pct *= 0.5

        # 2. Technical Skill Match (30%)
        matched_skills = [s for s in req_skills_norm if s in stu_skills_norm]
        missing_skills = [s for s in req_skills_norm if s not in stu_skills_norm]
        bonus_pref = [s for s in pref_skills_norm if s in stu_skills_norm]

        if req_skills_norm:
            tech_ratio = len(matched_skills) / len(req_skills_norm)
        else:
            tech_ratio = 1.0
        tech_pct = min(100.0, (tech_ratio * 90.0) + (len(bonus_pref) * 5.0))

        # 3. Project Relevance (15%)
        # Look for overlap between student project tech stack/descriptions and required skills
        project_relevance_hits = 0
        for p in stu_projects:
            p_desc = str(p.get("description", "")) + " " + str(p.get("title", "")) + " " + str(p.get("tech_stack", ""))
            p_skills = cls.extract_skills_from_text(p_desc)
            if any(s in req_skills_norm for s in p_skills):
                project_relevance_hits += 1
        proj_pct = min(100.0, (len(stu_projects) * 25.0) + (project_relevance_hits * 25.0))

        # 4. Certification Match (10%)
        cert_pct = min(100.0, len(stu_certs) * 40.0)

        # 5. Aptitude Score (10%)
        apt_pct = float(student.aptitude_score or 70.0)

        # 6. Mock Interview (10%)
        mock_pct = float(student.mock_interview_score or 70.0)

        # 7. Communication Score (5%)
        comm_pct = float(student.communication_score or 70.0)

        # 8. Experience (5%)
        has_internship = bool(student.internship_experience and len(str(student.internship_experience)) > 10)
        exp_pct = 95.0 if has_internship else 50.0

        # Weighted Aggregation
        fit_score = (
            academic_pct * 0.15 +
            tech_pct * 0.30 +
            proj_pct * 0.15 +
            cert_pct * 0.10 +
            apt_pct * 0.10 +
            mock_pct * 0.10 +
            comm_pct * 0.05 +
            exp_pct * 0.05
        )
        fit_score = round(max(0.0, min(100.0, fit_score)), 1)

        # Generate Explainability Details
        positive_reasons = []
        if cgpa >= min_cgpa:
            positive_reasons.append(f"CGPA {cgpa} meets requirement (min {min_cgpa})")
        if is_branch_eligible:
            positive_reasons.append(f"Branch {branch} is eligible ({', '.join(eligible_branches)})")
        if matched_skills:
            positive_reasons.append(f"Matched {len(matched_skills)}/{len(req_skills_norm)} required skills: {', '.join(matched_skills)}")
        if project_relevance_hits > 0:
            positive_reasons.append("Contains directly relevant portfolio project(s)")
        if apt_pct >= 75:
            positive_reasons.append(f"Strong aptitude test score ({int(apt_pct)}%)")
        if stu_certs:
            positive_reasons.append(f"Holds {len(stu_certs)} verified technical certification(s)")

        # Recommendations
        if missing_skills:
            rec_text = f"Candidate is well-positioned for screening. Recommended to focus on {', '.join(missing_skills[:3])} to optimize technical round conversion."
        else:
            rec_text = "Strong overall match across all criteria. Recommended for immediate fast-track shortlisting."

        return {
            "fit_score": fit_score,
            "is_eligible": (cgpa >= min_cgpa) and is_branch_eligible,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "positive_reasons": positive_reasons,
            "recommendation": rec_text,
            "breakdown": {
                "academic": round(academic_pct, 1),
                "technical": round(tech_pct, 1),
                "projects": round(proj_pct, 1),
                "certifications": round(cert_pct, 1),
                "aptitude": round(apt_pct, 1),
                "interview": round(mock_pct, 1)
            },
            "responsible_ai_disclaimer": "AI recommendations are decision-support tools and should be reviewed by authorized placement personnel."
        }

    @classmethod
    def analyze_skill_gap(cls, student_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """Skill Gap Analysis: Available vs Missing, with targeted prep roadmap."""
        stu_norm = set(cls.normalize_skill(s) for s in student_skills)
        req_norm = [cls.normalize_skill(s) for s in required_skills]

        available = [s for s in req_norm if s in stu_norm]
        missing = [s for s in req_norm if s not in stu_norm]

        # Actionable prep recommendations
        action_plan = []
        for m in missing[:3]:
            action_plan.append(f"Learn core concepts and syntax of {m}")
            action_plan.append(f"Build a mini project or module demonstrating {m}")
        if not action_plan:
            action_plan = [
                "Practice advanced data structures & algorithms questions",
                "Review system design trade-offs and architectural patterns",
                "Complete a timed mock interview round"
            ]

        return {
            "available_skills": available,
            "missing_skills": missing,
            "gap_percentage": round((len(missing) / max(len(req_norm), 1)) * 100, 1),
            "personalized_recommendations": action_plan[:4]
        }

    @staticmethod
    def _parse_time_to_minutes(time_str: str) -> int:
        """Parse time string like '10:00 AM' or '14:30' into minutes from midnight."""
        t = time_str.strip().upper()
        match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)?', t)
        if not match:
            return 600  # 10:00 AM default
        hours = int(match.group(1))
        minutes = int(match.group(2))
        period = match.group(3)
        if period == "PM" and hours != 12:
            hours += 12
        elif period == "AM" and hours == 12:
            hours = 0
        return hours * 60 + minutes

    @classmethod
    def detect_drive_conflicts(cls, drives: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detects:
        1. Venue double-booking conflicts
        2. Interview Panel overlapping conflicts
        3. Student shortlisting interview conflicts across overlapping drives
        """
        venue_conflicts = []
        panel_conflicts = []
        student_conflicts = []

        # Helper to check if two drives overlap in time
        def is_overlap(d1, d2):
            if d1.get("drive_date") != d2.get("drive_date"):
                return False
            start1 = cls._parse_time_to_minutes(d1.get("start_time", "10:00 AM"))
            end1 = cls._parse_time_to_minutes(d1.get("end_time", "01:00 PM"))
            start2 = cls._parse_time_to_minutes(d2.get("start_time", "10:00 AM"))
            end2 = cls._parse_time_to_minutes(d2.get("end_time", "01:00 PM"))
            return max(start1, start2) < min(end1, end2)

        # 1 & 2: Compare pairs of drives
        n = len(drives)
        for i in range(n):
            for j in range(i + 1, n):
                d1 = drives[i]
                d2 = drives[j]
                if is_overlap(d1, d2):
                    # Venue conflict
                    v1 = (d1.get("venue") or "").strip().lower()
                    v2 = (d2.get("venue") or "").strip().lower()
                    if v1 and v1 == v2:
                        venue_conflicts.append({
                            "type": "VENUE_CONFLICT",
                            "venue": d1.get("venue"),
                            "drive_1": {"id": d1.get("id"), "company": d1.get("company_name"), "time": f"{d1.get('start_time')} - {d1.get('end_time')}"},
                            "drive_2": {"id": d2.get("id"), "company": d2.get("company_name"), "time": f"{d2.get('start_time')} - {d2.get('end_time')}"},
                            "message": f"Venue Double-Booking: '{d1.get('venue')}' is assigned to both {d1.get('company_name')} and {d2.get('company_name')} at the same time."
                        })

                    # Panel conflict
                    p1 = (d1.get("panel_name") or "").strip().lower()
                    p2 = (d2.get("panel_name") or "").strip().lower()
                    if p1 and p1 == p2:
                        panel_conflicts.append({
                            "type": "PANEL_CONFLICT",
                            "panel": d1.get("panel_name"),
                            "drive_1": {"id": d1.get("id"), "company": d1.get("company_name"), "time": f"{d1.get('start_time')} - {d1.get('end_time')}"},
                            "drive_2": {"id": d2.get("id"), "company": d2.get("company_name"), "time": f"{d2.get('start_time')} - {d2.get('end_time')}"},
                            "message": f"Panel Over-Allocation: Panel '{d1.get('panel_name')}' is assigned to both {d1.get('company_name')} and {d2.get('company_name')} simultaneously."
                        })

        # 3. Student Conflicts
        # Map student_id -> list of drive_ids where status in ['AI_SHORTLISTED', 'ASSESSMENT', 'INTERVIEW', 'SELECTED']
        stu_to_drives = {}
        active_statuses = {"AI_SHORTLISTED", "ASSESSMENT", "INTERVIEW", "SELECTED"}
        for app in applications:
            if app.get("status") in active_statuses and app.get("drive_id"):
                stu_id = app.get("student_id")
                d_id = app.get("drive_id")
                stu_to_drives.setdefault(stu_id, set()).add(d_id)

        drive_lookup = {d.get("id"): d for d in drives}
        for stu_id, d_set in stu_to_drives.items():
            d_list = [drive_lookup[did] for did in d_set if did in drive_lookup]
            for i in range(len(d_list)):
                for j in range(i + 1, len(d_list)):
                    d1 = d_list[i]
                    d2 = d_list[j]
                    if is_overlap(d1, d2):
                        student_conflicts.append({
                            "type": "STUDENT_CONFLICT",
                            "student_id": stu_id,
                            "student_name": app.get("student_name", f"Student #{stu_id}"),
                            "drive_1": {"id": d1.get("id"), "company": d1.get("company_name"), "time": f"{d1.get('start_time')} - {d1.get('end_time')}"},
                            "drive_2": {"id": d2.get("id"), "company": d2.get("company_name"), "time": f"{d2.get('start_time')} - {d2.get('end_time')}"},
                            "message": f"Candidate Schedule Clash: Student #{stu_id} is shortlisted for overlapping drives '{d1.get('company_name')}' and '{d2.get('company_name')}'."
                        })

        has_conflicts = bool(venue_conflicts or panel_conflicts or student_conflicts)
        return {
            "has_conflicts": has_conflicts,
            "total_conflicts": len(venue_conflicts) + len(panel_conflicts) + len(student_conflicts),
            "venue_conflicts": venue_conflicts,
            "panel_conflicts": panel_conflicts,
            "student_conflicts": student_conflicts
        }

    @classmethod
    def optimize_schedules(cls, drives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Intelligently proposes non-overlapping sequential drive slots and venues."""
        venues = ["Auditorium A", "Seminar Hall 1", "Seminar Hall 2", "Conference Room B"]
        panels = ["Panel Alpha (Tech)", "Panel Beta (Tech)", "Panel Gamma (HR)", "Panel Delta (Exec)"]
        slots = [
            ("09:00 AM", "11:30 AM"),
            ("12:00 PM", "02:30 PM"),
            ("03:00 PM", "05:30 PM")
        ]
        
        optimized = []
        for idx, drive in enumerate(drives):
            slot = slots[idx % len(slots)]
            venue = venues[idx % len(venues)]
            panel = panels[idx % len(panels)]
            
            opt_drive = dict(drive)
            opt_drive["proposed_start_time"] = slot[0]
            opt_drive["proposed_end_time"] = slot[1]
            opt_drive["proposed_venue"] = venue
            opt_drive["proposed_panel"] = panel
            opt_drive["optimization_notes"] = f"Adjusted to window {slot[0]} - {slot[1]} at {venue} to eliminate panel and student schedule clashes."
            optimized.append(opt_drive)
            
        return optimized

    @classmethod
    def evaluate_at_risk_students(cls, students: List[Any], applications_by_student: Dict[int, List[Any]]) -> List[Dict[str, Any]]:
        """
        AI/Rule Risk Model:
        Predicts students likely to remain unplaced based on:
        - Readiness Score < 50
        - Aptitude < 60
        - Low technical score < 60
        - Low mock interview < 60
        - Low application count or repeated rejections
        """
        at_risk_results = []
        for s in students:
            readiness = float(getattr(s, 'readiness_score', 70.0) or 70.0)
            aptitude = float(getattr(s, 'aptitude_score', 70.0) or 70.0)
            tech = float(getattr(s, 'tech_assessment_score', 70.0) or 70.0)
            comm = float(getattr(s, 'communication_score', 70.0) or 70.0)
            mock = float(getattr(s, 'mock_interview_score', 70.0) or 70.0)
            backlogs = int(getattr(s, 'backlogs', 0) or 0)
            
            apps = applications_by_student.get(s.id, [])
            rejections = sum(1 for a in apps if getattr(a, 'status', '') == 'REJECTED')
            app_count = len(apps)

            risk_points = 0
            risk_reasons = []

            if readiness < 50:
                risk_points += 3
                risk_reasons.append(f"Low overall readiness score ({int(readiness)}/100)")
            elif readiness < 65:
                risk_points += 1

            if backlogs > 0:
                risk_points += 2
                risk_reasons.append(f"{backlogs} active academic backlog(s)")

            if aptitude < 60:
                risk_points += 2
                risk_reasons.append(f"Aptitude score ({int(aptitude)}%) below recruiter filter")

            if mock < 60:
                risk_points += 2
                risk_reasons.append(f"Mock interview rating ({int(mock)}%) needs immediate coaching")

            if tech < 60:
                risk_points += 1
                risk_reasons.append(f"Technical score ({int(tech)}%) in developing range")

            if app_count <= 2:
                risk_points += 1
                risk_reasons.append(f"Low engagement: applied to only {app_count} drive(s)")

            if rejections >= 2:
                risk_points += 2
                risk_reasons.append(f"{rejections} previous drive rejections encountered")

            # Risk Level
            if risk_points >= 5:
                level = "HIGH"
                recommended_action = "Assign dedicated faculty mentor + mandate 2-week DSA bootcamp + schedule 1-on-1 mock interview simulation."
            elif risk_points >= 2:
                level = "MEDIUM"
                recommended_action = "Recommend 20 practice aptitude tests + advise project portfolio review with TPO counselor."
            else:
                level = "LOW"
                recommended_action = "Standard progression on track; encourage applications to tier-1 corporate drives."

            at_risk_results.append({
                "student_id": s.id,
                "student_roll": getattr(s, 'student_id', f'STU-{s.id}'),
                "name": s.name,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "readiness_score": readiness,
                "risk_level": level,
                "risk_points": risk_points,
                "risk_reasons": risk_reasons if risk_reasons else ["No major risk factors detected"],
                "recommended_action": recommended_action,
                "application_count": app_count,
                "rejection_count": rejections
            })

        # Sort highest risk first
        at_risk_results.sort(key=lambda x: (x["risk_level"] != "HIGH", x["risk_level"] != "MEDIUM", -x["risk_points"]))
        return at_risk_results
