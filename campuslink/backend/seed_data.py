import json
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
import models
from auth import hash_password
from ai_engine import AIEngine

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data for fresh seed if needed
    db.query(models.Document).delete()
    db.query(models.Notification).delete()
    db.query(models.Offer).delete()
    db.query(models.Interview).delete()
    db.query(models.Application).delete()
    db.query(models.PlacementDrive).delete()
    db.query(models.Job).delete()
    db.query(models.Recruiter).delete()
    db.query(models.Student).delete()
    db.query(models.User).delete()
    db.query(models.Venue).delete()
    db.query(models.InterviewPanel).delete()
    db.commit()

    print("Seeding Venues and Panels...")
    venues = [
        models.Venue(name="Seminar Hall 1", capacity=150, location="Academic Block A - 2nd Floor"),
        models.Venue(name="Auditorium A", capacity=300, location="Central Campus Complex"),
        models.Venue(name="Conference Room B", capacity=60, location="Placement Cell Wing"),
        models.Venue(name="Lab 301", capacity=80, location="Computer Science Block"),
    ]
    db.add_all(venues)

    panels = [
        models.InterviewPanel(name="Panel A - Technical", department="CSE / Placement Cell", members="Prof. Sharma, Dr. Rao"),
        models.InterviewPanel(name="Panel B - Cloud", department="IT / Cloud Center", members="Prof. Kulkarni, Er. Nambiar"),
        models.InterviewPanel(name="Panel C - AI", department="Data Science Labs", members="Dr. Anita Roy, Prof. Nair"),
        models.InterviewPanel(name="Panel D - Hardware", department="ECE / Embedded Lab", members="Dr. V. Prasad, Prof. Iyer"),
    ]
    db.add_all(panels)
    db.commit()

    print("Seeding Admin User...")
    tpo_user = models.User(
        email="tpo@campuslink.edu",
        password_hash=hash_password("admin123"),
        role="TPO_ADMIN",
        name="Prof. S. K. Verma (TPO Head)"
    )
    db.add(tpo_user)
    db.commit()

    print("Seeding Recruiters...")
    recruiters_data = [
        {
            "email": "recruiter@technova.com",
            "password": "password123",
            "company_name": "TechNova Solutions",
            "contact_person": "Vikram Malhotra",
            "phone": "+91 98765 43210",
            "website": "https://technova.example.com",
            "industry": "Enterprise Software & Cloud Services",
            "description": "Leading global digital transformation and SaaS provider serving Fortune 500 enterprises."
        },
        {
            "email": "careers@codesphere.io",
            "password": "password123",
            "company_name": "CodeSphere Technologies",
            "contact_person": "Ananya Sen",
            "phone": "+91 98111 22334",
            "website": "https://codesphere.example.com",
            "industry": "FinTech & Banking Infrastructure",
            "description": "High-frequency transaction processing and next-generation banking APIs."
        },
        {
            "email": "talent@cloudmatrix.net",
            "password": "password123",
            "company_name": "CloudMatrix",
            "contact_person": "David Fernandez",
            "phone": "+91 98222 33445",
            "website": "https://cloudmatrix.example.com",
            "industry": "Cloud Infrastructure & DevOps",
            "description": "Kubernetes orchestration, hybrid cloud architecture, and edge computing platforms."
        },
        {
            "email": "hr@datapulse.ai",
            "password": "password123",
            "company_name": "DataPulse Analytics",
            "contact_person": "Rohan Deshmukh",
            "phone": "+91 98333 44556",
            "website": "https://datapulse.example.com",
            "industry": "Artificial Intelligence & Big Data",
            "description": "Enterprise generative AI applications, deep learning modeling, and predictive intelligence."
        },
        {
            "email": "campus@innovatex.com",
            "password": "password123",
            "company_name": "InnovateX Systems",
            "contact_person": "Kavita Pillai",
            "phone": "+91 98444 55667",
            "website": "https://innovatex.example.com",
            "industry": "IoT, Robotics & Smart Systems",
            "description": "Industrial automation, connected robotics, and embedded electronic systems."
        }
    ]

    recruiter_objs = []
    for r in recruiters_data:
        u = models.User(
            email=r["email"],
            password_hash=hash_password(r["password"]),
            role="RECRUITER",
            name=f"{r['contact_person']} ({r['company_name']})"
        )
        db.add(u)
        db.commit()

        rec = models.Recruiter(
            user_id=u.id,
            company_name=r["company_name"],
            contact_person=r["contact_person"],
            email=r["email"],
            phone=r["phone"],
            website=r["website"],
            industry=r["industry"],
            description=r["description"],
            is_verified=True
        )
        db.add(rec)
        db.commit()
        recruiter_objs.append(rec)

    print("Seeding Job Roles...")
    jobs_data = [
        {
            "recruiter_id": recruiter_objs[0].id,
            "title": "Java Backend Developer",
            "description": "Looking for a high-caliber Java engineer with strong grasp of Java, Spring Boot, MySQL, REST API design, and Git version control. Candidate will develop low-latency microservices.",
            "min_cgpa": 7.0,
            "eligible_branches": ["CSE", "IT"],
            "required_skills": ["Java", "Spring Boot", "SQL", "REST API", "Git"],
            "preferred_skills": ["Docker", "AWS"],
            "required_certifications": ["Oracle Java" , "AWS Cloud Practitioner"],
            "ctc_lpa": 8.5,
            "location": "Bangalore / Hybrid",
            "job_type": "Full Time",
            "deadline": "2026-10-25"
        },
        {
            "recruiter_id": recruiter_objs[1].id,
            "title": "Full Stack Web Engineer",
            "description": "Develop financial dashboards using modern React, Node.js, TypeScript, PostgreSQL, and Git. Understanding of RESTful microservices and agile principles is required.",
            "min_cgpa": 7.5,
            "eligible_branches": ["CSE", "IT", "ECE"],
            "required_skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Git"],
            "preferred_skills": ["Tailwind CSS", "Docker"],
            "required_certifications": ["Full Stack Developer"],
            "ctc_lpa": 10.0,
            "location": "Hyderabad / Remote",
            "job_type": "Full Time",
            "deadline": "2026-10-28"
        },
        {
            "recruiter_id": recruiter_objs[2].id,
            "title": "Cloud & DevOps Engineer",
            "description": "Manage multi-region infrastructure using AWS, Docker, Kubernetes, Linux, and CI/CD pipelines. Automate deployments and ensure high availability.",
            "min_cgpa": 7.0,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "required_skills": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD"],
            "preferred_skills": ["Python", "Terraform"],
            "required_certifications": ["AWS Certified Solutions Architect"],
            "ctc_lpa": 12.0,
            "location": "Pune / Office",
            "job_type": "Full Time",
            "deadline": "2026-10-30"
        },
        {
            "recruiter_id": recruiter_objs[3].id,
            "title": "AI/ML Associate Engineer",
            "description": "Research and deploy deep learning models. Candidate must have strong Python, Machine Learning, Deep Learning, SQL, and Git skills.",
            "min_cgpa": 8.0,
            "eligible_branches": ["CSE", "IT"],
            "required_skills": ["Python", "Machine Learning", "Deep Learning", "SQL", "Git"],
            "preferred_skills": ["Docker", "PyTorch"],
            "required_certifications": ["TensorFlow Developer" , "DeepLearning.AI"],
            "ctc_lpa": 14.5,
            "location": "Bangalore / Office",
            "job_type": "Full Time",
            "deadline": "2026-11-05"
        },
        {
            "recruiter_id": recruiter_objs[3].id,
            "title": "Business Intelligence & Data Analyst",
            "description": "Translate business metrics into visual intelligence. Require Python, SQL, statistical modeling, and data visualization tools.",
            "min_cgpa": 6.5,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE", "ME", "Civil"],
            "required_skills": ["Python", "SQL", "Excel", "Data Science"],
            "preferred_skills": ["PowerBI", "Tableau"],
            "required_certifications": ["Google Data Analytics"],
            "ctc_lpa": 7.0,
            "location": "Mumbai / Hybrid",
            "job_type": "Full Time",
            "deadline": "2026-10-22"
        },
        {
            "recruiter_id": recruiter_objs[4].id,
            "title": "Embedded & IoT Systems Engineer",
            "description": "Develop firmware for smart automation devices. Requires C++, Linux system programming, Git, and hardware interfacing fundamentals.",
            "min_cgpa": 6.8,
            "eligible_branches": ["ECE", "EEE"],
            "required_skills": ["C++", "Linux", "Git", "DSA"],
            "preferred_skills": ["RTOS", "Python"],
            "required_certifications": ["Embedded Systems"],
            "ctc_lpa": 7.5,
            "location": "Chennai / Office",
            "job_type": "Full Time",
            "deadline": "2026-10-26"
        },
        {
            "recruiter_id": recruiter_objs[0].id,
            "title": "QA Automation Engineer",
            "description": "Write automated test suites for web services and backend APIs. Familiarity with Java or Python, SQL, and Git required.",
            "min_cgpa": 6.0,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "required_skills": ["Java", "Python", "SQL", "Git"],
            "preferred_skills": ["Selenium", "Postman"],
            "required_certifications": ["ISTQB"],
            "ctc_lpa": 6.2,
            "location": "Bangalore / Hybrid",
            "job_type": "Full Time",
            "deadline": "2026-10-27"
        },
        {
            "recruiter_id": recruiter_objs[4].id,
            "title": "Graduate Engineering Trainee",
            "description": "Rotational entry-level engineering position across industrial operations, CAD, and automation processes.",
            "min_cgpa": 6.0,
            "eligible_branches": ["ME", "Civil", "EEE"],
            "required_skills": ["Python", "SQL", "Linux"],
            "preferred_skills": ["AutoCAD", "MATLAB"],
            "required_certifications": [],
            "ctc_lpa": 5.0,
            "location": "Coimbatore / Plant",
            "job_type": "Full Time",
            "deadline": "2026-10-29"
        }
    ]

    job_objs = []
    for jd in jobs_data:
        j = models.Job(
            recruiter_id=jd["recruiter_id"],
            title=jd["title"],
            description=jd["description"],
            min_cgpa=jd["min_cgpa"],
            eligible_branches=json.dumps(jd["eligible_branches"]),
            required_skills=json.dumps(jd["required_skills"]),
            preferred_skills=json.dumps(jd["preferred_skills"]),
            required_certifications=json.dumps(jd["required_certifications"]),
            ctc_lpa=jd["ctc_lpa"],
            location=jd["location"],
            job_type=jd["job_type"],
            deadline=jd["deadline"],
            is_active=True,
            extracted_requirements=json.dumps({
                "min_cgpa": jd["min_cgpa"],
                "branches": jd["eligible_branches"],
                "skills": jd["required_skills"]
            })
        )
        db.add(j)
        db.commit()
        job_objs.append(j)

    print("Seeding Placement Drives (including test conflict drives)...")
    drives_data = [
        {
            "job_id": job_objs[0].id,
            "company_name": "TechNova Solutions",
            "role_title": "Java Backend Developer",
            "drive_date": "2026-10-15",
            "start_time": "10:00 AM",
            "end_time": "01:00 PM",
            "venue": "Seminar Hall 1",
            "panel_name": "Panel A - Technical",
            "eligibility_criteria": "CGPA >= 7.0, CSE/IT, Zero Backlogs",
            "status": "SCHEDULED"
        },
        {
            # INTENTIONAL VENUE & PANEL CLASH WITH DRIVE 1 TO DEMO CONFLICT DETECTION!
            "job_id": job_objs[1].id,
            "company_name": "CodeSphere Technologies",
            "role_title": "Full Stack Web Engineer",
            "drive_date": "2026-10-15",
            "start_time": "11:00 AM",
            "end_time": "01:30 PM",
            "venue": "Seminar Hall 1",
            "panel_name": "Panel A - Technical",
            "eligibility_criteria": "CGPA >= 7.5, CSE/IT/ECE",
            "status": "SCHEDULED"
        },
        {
            "job_id": job_objs[2].id,
            "company_name": "CloudMatrix",
            "role_title": "Cloud & DevOps Engineer",
            "drive_date": "2026-10-16",
            "start_time": "09:30 AM",
            "end_time": "12:30 PM",
            "venue": "Auditorium A",
            "panel_name": "Panel B - Cloud",
            "eligibility_criteria": "CGPA >= 7.0, All Tech Branches",
            "status": "SCHEDULED"
        },
        {
            "job_id": job_objs[3].id,
            "company_name": "DataPulse Analytics",
            "role_title": "AI/ML Associate Engineer",
            "drive_date": "2026-10-17",
            "start_time": "10:00 AM",
            "end_time": "01:00 PM",
            "venue": "Conference Room B",
            "panel_name": "Panel C - AI",
            "eligibility_criteria": "CGPA >= 8.0, CSE/IT",
            "status": "SCHEDULED"
        },
        {
            "job_id": job_objs[5].id,
            "company_name": "InnovateX Systems",
            "role_title": "Embedded & IoT Systems Engineer",
            "drive_date": "2026-10-18",
            "start_time": "02:00 PM",
            "end_time": "05:00 PM",
            "venue": "Lab 301",
            "panel_name": "Panel D - Hardware",
            "eligibility_criteria": "CGPA >= 6.8, ECE/EEE",
            "status": "SCHEDULED"
        }
    ]

    drive_objs = []
    for dd in drives_data:
        drv = models.PlacementDrive(
            job_id=dd["job_id"],
            company_name=dd["company_name"],
            role_title=dd["role_title"],
            drive_date=dd["drive_date"],
            start_time=dd["start_time"],
            end_time=dd["end_time"],
            venue=dd["venue"],
            panel_name=dd["panel_name"],
            eligibility_criteria=dd["eligibility_criteria"],
            status=dd["status"]
        )
        db.add(drv)
        db.commit()
        drive_objs.append(drv)

    print("Seeding 32 Students with Realistic Distributions...")
    students_raw = [
        # 1. Rahul Sharma - Primary Showcase Student
        {
            "name": "Rahul Sharma",
            "email": "rahul@campuslink.edu",
            "roll": "CS2024-001",
            "branch": "CSE",
            "cgpa": 8.6,
            "backlogs": 0,
            "tech_skills": ["Java", "SQL", "Git", "REST API", "Spring Boot", "Python"],
            "soft_skills": ["Problem Solving", "Team Leadership", "Communication"],
            "certs": ["Oracle Java SE Certified Associate", "AWS Cloud Practitioner"],
            "projects": [
                {"title": "E-Commerce Microservices", "description": "High-throughput store built with Java, Spring Boot, MySQL, REST API", "tech_stack": "Java, Spring Boot, SQL"},
                {"title": "Distributed Task Scheduler", "description": "Fault-tolerant queue scheduler using Java and Git", "tech_stack": "Java, Git"}
            ],
            "internship": "Backend Engineering Intern at FinTech Labs (3 months)",
            "aptitude": 84.0, "coding": 88.0, "tech_assessment": 85.0, "comm": 78.0, "mock": 82.0
        },
        # 2. Priya Patel - Top Performer
        {
            "name": "Priya Patel",
            "email": "priya@campuslink.edu",
            "roll": "IT2024-002",
            "branch": "IT",
            "cgpa": 9.3,
            "backlogs": 0,
            "tech_skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Git", "AWS", "Docker"],
            "soft_skills": ["Critical Thinking", "Agile", "Presentation"],
            "certs": ["Meta Front-End Developer", "AWS Certified Developer"],
            "projects": [
                {"title": "Collaborative Whiteboard", "description": "Real-time canvas with React, Node.js, TypeScript and WebSockets", "tech_stack": "React, TypeScript, Node.js"},
                {"title": "Cloud Monitoring Dashboard", "description": "Telemetry visualizer with AWS and PostgreSQL", "tech_stack": "AWS, PostgreSQL"}
            ],
            "internship": "Full Stack Intern at SaaSify Inc (6 months)",
            "aptitude": 92.0, "coding": 94.0, "tech_assessment": 90.0, "comm": 88.0, "mock": 91.0
        },
        # 3. Amit Kumar - Primary Showcase AT-RISK Student
        {
            "name": "Amit Kumar",
            "email": "amit@campuslink.edu",
            "roll": "ME2024-003",
            "branch": "ME",
            "cgpa": 6.1,
            "backlogs": 2,
            "tech_skills": ["AutoCAD", "Basic C"],
            "soft_skills": ["Teamwork"],
            "certs": [],
            "projects": [
                {"title": "Gearbox Load Simulation", "description": "Mechanical torque stress analysis", "tech_stack": "AutoCAD"}
            ],
            "internship": "",
            "aptitude": 48.0, "coding": 42.0, "tech_assessment": 45.0, "comm": 52.0, "mock": 46.0
        },
        # 4. Sneha Reddy - AI Specialist
        {
            "name": "Sneha Reddy",
            "email": "sneha@campuslink.edu",
            "roll": "CS2024-004",
            "branch": "CSE",
            "cgpa": 8.9,
            "backlogs": 0,
            "tech_skills": ["Python", "Machine Learning", "Deep Learning", "SQL", "Git", "Docker"],
            "soft_skills": ["Research Writing", "Analytical Reasoning"],
            "certs": ["DeepLearning.AI Specialization", "TensorFlow Certified"],
            "projects": [
                {"title": "Medical Imaging Diagnostic AI", "description": "CNN classifier with 96% accuracy on lung X-rays", "tech_stack": "Python, Deep Learning"},
                {"title": "Customer Churn Prediction", "description": "Ensemble ML pipeline with SQL data integration", "tech_stack": "Python, Machine Learning, SQL"}
            ],
            "internship": "Data Science Research Intern at AI Institute",
            "aptitude": 88.0, "coding": 86.0, "tech_assessment": 90.0, "comm": 82.0, "mock": 85.0
        },
        # 5. Rohan Joshi - Cloud / DevOps
        {
            "name": "Rohan Joshi",
            "email": "rohan.j@campuslink.edu",
            "roll": "IT2024-005",
            "branch": "IT",
            "cgpa": 7.8,
            "backlogs": 0,
            "tech_skills": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "Git", "Python"],
            "soft_skills": ["Incident Management", "Documentation"],
            "certs": ["AWS Solutions Architect Associate"],
            "projects": [
                {"title": "Automated GitOps Pipeline", "description": "Continuous delivery with Kubernetes and Docker", "tech_stack": "Docker, Kubernetes, CI/CD"}
            ],
            "internship": "DevOps Intern at CloudWave",
            "aptitude": 80.0, "coding": 76.0, "tech_assessment": 84.0, "comm": 74.0, "mock": 79.0
        },
        # 6. Anjali Menon - ECE Embedded
        {
            "name": "Anjali Menon",
            "email": "anjali.m@campuslink.edu",
            "roll": "EC2024-006",
            "branch": "ECE",
            "cgpa": 8.1,
            "backlogs": 0,
            "tech_skills": ["C++", "Linux", "Git", "DSA", "Python"],
            "soft_skills": ["Troubleshooting", "Detail Oriented"],
            "certs": ["Embedded Systems Architecture"],
            "projects": [
                {"title": "Smart Greenhouse Controller", "description": "Microcontroller firmware with sensor network in C++", "tech_stack": "C++, Linux"}
            ],
            "internship": "Hardware Firmware Intern at MicroTech",
            "aptitude": 82.0, "coding": 80.0, "tech_assessment": 81.0, "comm": 76.0, "mock": 78.0
        },
        # 7. Vikram Rathore - QA & Automation
        {
            "name": "Vikram Rathore",
            "email": "vikram.r@campuslink.edu",
            "roll": "EE2024-007",
            "branch": "EEE",
            "cgpa": 7.4,
            "backlogs": 0,
            "tech_skills": ["Java", "Python", "SQL", "Git", "Linux"],
            "soft_skills": ["Quality Control", "Communication"],
            "certs": ["ISTQB Foundation Level"],
            "projects": [
                {"title": "API Test Automation Suite", "description": "RestAssured regression automation framework", "tech_stack": "Java, SQL"}
            ],
            "internship": "QA Intern at TestHub",
            "aptitude": 76.0, "coding": 70.0, "tech_assessment": 75.0, "comm": 72.0, "mock": 74.0
        },
        # 8. Neha Gupta - Data Analyst
        {
            "name": "Neha Gupta",
            "email": "neha.g@campuslink.edu",
            "roll": "CS2024-008",
            "branch": "CSE",
            "cgpa": 8.4,
            "backlogs": 0,
            "tech_skills": ["Python", "SQL", "Excel", "Data Science", "Git"],
            "soft_skills": ["Storytelling", "Client Communication"],
            "certs": ["Google Data Analytics Professional"],
            "projects": [
                {"title": "Retail Sales Forecasting", "description": "Interactive analytics report with SQL and Python", "tech_stack": "Python, SQL"}
            ],
            "internship": "BI Intern at RetailSync",
            "aptitude": 85.0, "coding": 78.0, "tech_assessment": 82.0, "comm": 85.0, "mock": 84.0
        },
        # 9. Karthik Nair - High Achiever Placed
        {
            "name": "Karthik Nair",
            "email": "karthik.n@campuslink.edu",
            "roll": "CS2024-009",
            "branch": "CSE",
            "cgpa": 9.4,
            "backlogs": 0,
            "tech_skills": ["Java", "Spring Boot", "SQL", "REST API", "Git", "Docker", "AWS"],
            "soft_skills": ["System Design", "Mentorship"],
            "certs": ["Oracle Certified Professional Java", "AWS Certified Solutions Architect"],
            "projects": [
                {"title": "High Frequency Trading Engine", "description": "Sub-millisecond order book matching in Java", "tech_stack": "Java, Spring Boot"}
            ],
            "internship": "Software Intern at Goldman Sachs (Summer)",
            "aptitude": 94.0, "coding": 96.0, "tech_assessment": 95.0, "comm": 89.0, "mock": 92.0
        },
        # 10. Divya Suresh - ECE
        {
            "name": "Divya Suresh",
            "email": "divya.s@campuslink.edu",
            "roll": "EC2024-010",
            "branch": "ECE",
            "cgpa": 7.6,
            "backlogs": 0,
            "tech_skills": ["Python", "C++", "SQL", "Git", "Linux"],
            "soft_skills": ["Analytical", "Teamwork"],
            "certs": ["Python for Everybody"],
            "projects": [
                {"title": "Digital Signal Filter", "description": "Audio signal frequency noise suppression algorithm", "tech_stack": "Python, C++"}
            ],
            "internship": "",
            "aptitude": 74.0, "coding": 72.0, "tech_assessment": 76.0, "comm": 71.0, "mock": 73.0
        },
        # 11. Manoj Tiwari - At-Risk Student 2
        {
            "name": "Manoj Tiwari",
            "email": "manoj.t@campuslink.edu",
            "roll": "CV2024-011",
            "branch": "Civil",
            "cgpa": 5.9,
            "backlogs": 3,
            "tech_skills": ["AutoCAD"],
            "soft_skills": ["Basic English"],
            "certs": [],
            "projects": [
                {"title": "Concrete Compressive Analysis", "description": "Structural material testing", "tech_stack": "AutoCAD"}
            ],
            "internship": "",
            "aptitude": 44.0, "coding": 35.0, "tech_assessment": 40.0, "comm": 45.0, "mock": 42.0
        },
        # 12. Pooja Deshmukh - Web Dev
        {
            "name": "Pooja Deshmukh",
            "email": "pooja.d@campuslink.edu",
            "roll": "IT2024-012",
            "branch": "IT",
            "cgpa": 8.0,
            "backlogs": 0,
            "tech_skills": ["React", "Node.js", "JavaScript", "HTML", "CSS", "Git", "MongoDB"],
            "soft_skills": ["Creative", "Collaboration"],
            "certs": ["Full Stack MERN Certificate"],
            "projects": [
                {"title": "University Event Portal", "description": "Student clubs and booking platform", "tech_stack": "React, Node.js, MongoDB"}
            ],
            "internship": "Web Intern at CampusClub",
            "aptitude": 78.0, "coding": 80.0, "tech_assessment": 79.0, "comm": 77.0, "mock": 76.0
        },
        # 13. Harish Chandra - EEE
        {
            "name": "Harish Chandra",
            "email": "harish.c@campuslink.edu",
            "roll": "EE2024-013",
            "branch": "EEE",
            "cgpa": 7.2,
            "backlogs": 0,
            "tech_skills": ["Python", "SQL", "Linux", "Git"],
            "soft_skills": ["Punctual", "Adaptable"],
            "certs": [],
            "projects": [
                {"title": "Substation SCADA Logger", "description": "Power grid voltage logging with Python", "tech_stack": "Python, SQL"}
            ],
            "internship": "",
            "aptitude": 71.0, "coding": 68.0, "tech_assessment": 70.0, "comm": 69.0, "mock": 70.0
        },
        # 14. Meera Krishnan - Backend
        {
            "name": "Meera Krishnan",
            "email": "meera.k@campuslink.edu",
            "roll": "CS2024-014",
            "branch": "CSE",
            "cgpa": 8.7,
            "backlogs": 0,
            "tech_skills": ["Java", "Spring Boot", "SQL", "REST API", "Git", "Docker"],
            "soft_skills": ["Leadership", "Communication"],
            "certs": ["Oracle Certified Professional Java"],
            "projects": [
                {"title": "Healthcare EHR API", "description": "FHIR-compliant patient records platform", "tech_stack": "Java, Spring Boot, SQL"}
            ],
            "internship": "Backend Intern at MedTech Solutions",
            "aptitude": 86.0, "coding": 87.0, "tech_assessment": 89.0, "comm": 84.0, "mock": 86.0
        },
        # 15. Arjun Varma - Full Stack
        {
            "name": "Arjun Varma",
            "email": "arjun.v@campuslink.edu",
            "roll": "CS2024-015",
            "branch": "CSE",
            "cgpa": 8.3,
            "backlogs": 0,
            "tech_skills": ["React", "TypeScript", "Node.js", "PostgreSQL", "Git", "Tailwind CSS"],
            "soft_skills": ["UI/UX Sense", "Speed"],
            "certs": ["Frontend Masters React Path"],
            "projects": [
                {"title": "SaaS Billing Dashboard", "description": "Stripe-connected subscription manager", "tech_stack": "React, TypeScript, PostgreSQL"}
            ],
            "internship": "Frontend Intern at PixelLabs",
            "aptitude": 82.0, "coding": 84.0, "tech_assessment": 83.0, "comm": 80.0, "mock": 81.0
        }
    ]

    # Add 17 more students systematically across departments to reach 32 students
    branches_cycle = ["CSE", "IT", "ECE", "EEE", "ME", "Civil"]
    for i in range(16, 33):
        b = branches_cycle[i % len(branches_cycle)]
        cg = round(6.5 + ((i * 7) % 31) * 0.1, 2)
        bl = 1 if (i % 7 == 0) else 0
        sk = ["Java", "SQL", "Git"] if b in ["CSE", "IT"] else (["Python", "C++", "Linux"] if b == "ECE" else ["Python", "SQL", "Excel"])
        st_data = {
            "name": f"Candidate {i:02d} ({b})",
            "email": f"student{i}@campuslink.edu",
            "roll": f"{b[:2].upper()}2024-{i:03d}",
            "branch": b,
            "cgpa": cg,
            "backlogs": bl,
            "tech_skills": sk,
            "soft_skills": ["Communication", "Teamwork"],
            "certs": ["Academic Excellence Cert"] if cg > 8.0 else [],
            "projects": [{"title": f"{b} Capstone Project", "description": f"Applied engineering workflow in {b}", "tech_stack": ", ".join(sk)}],
            "internship": f"Apprenticeship at Industry Partner ({b})" if cg > 7.5 else "",
            "aptitude": round(60.0 + ((i * 13) % 36), 1),
            "coding": round(55.0 + ((i * 11) % 40), 1),
            "tech_assessment": round(60.0 + ((i * 9) % 35), 1),
            "comm": round(65.0 + ((i * 5) % 30), 1),
            "mock": round(62.0 + ((i * 7) % 32), 1)
        }
        students_raw.append(st_data)

    student_objs = []
    for s in students_raw:
        # Create user
        u = models.User(
            email=s["email"],
            password_hash=hash_password("password123"),
            role="STUDENT",
            name=s["name"]
        )
        db.add(u)
        db.commit()

        # Temporary stub to calculate readiness
        class StuStub:
            cgpa = s["cgpa"]
            backlogs = s["backlogs"]
            aptitude_score = s["aptitude"]
            coding_score = s["coding"]
            tech_assessment_score = s["tech_assessment"]
            communication_score = s["comm"]
            mock_interview_score = s["mock"]
            technical_skills = json.dumps(s["tech_skills"])
            projects = json.dumps(s["projects"])

        readiness = AIEngine.calculate_readiness_score(StuStub)

        # Risk calculation
        risk_level = "LOW"
        risk_reasons = []
        if readiness["readiness_score"] < 50 or s["backlogs"] > 0 or s["aptitude"] < 55:
            risk_level = "HIGH" if (readiness["readiness_score"] < 50 and s["backlogs"] > 0) else "MEDIUM"
            if s["backlogs"] > 0:
                risk_reasons.append(f"{s['backlogs']} pending active academic backlog(s)")
            if readiness["readiness_score"] < 50:
                risk_reasons.append(f"Low overall readiness score: {readiness['readiness_score']}/100")
            if s["aptitude"] < 60:
                risk_reasons.append(f"Aptitude score ({int(s['aptitude'])}%) is below standard recruiter cutoffs")

        stu = models.Student(
            user_id=u.id,
            student_id=s["roll"],
            name=s["name"],
            email=s["email"],
            phone=f"+91 99{s['roll'][-3:]} 12345",
            branch=s["branch"],
            semester=7,
            cgpa=s["cgpa"],
            backlogs=s["backlogs"],
            academic_history=json.dumps({"10th": "92%", "12th": "89%", "current_degree": "B.Tech"}),
            technical_skills=json.dumps(s["tech_skills"]),
            soft_skills=json.dumps(s["soft_skills"]),
            certifications=json.dumps(s["certs"]),
            projects=json.dumps(s["projects"]),
            internship_experience=s["internship"],
            aptitude_score=s["aptitude"],
            coding_score=s["coding"],
            tech_assessment_score=s["tech_assessment"],
            communication_score=s["comm"],
            mock_interview_score=s["mock"],
            readiness_score=readiness["readiness_score"],
            readiness_class=readiness["readiness_class"],
            readiness_factors=json.dumps(readiness["positive_factors"]),
            improvement_areas=json.dumps(readiness["improvement_areas"]),
            at_risk_level=risk_level,
            at_risk_reasons=json.dumps(risk_reasons),
            recommendations=json.dumps({
                "prep_tasks": [
                    "Solve 20 LeetCode Medium Java/Python questions",
                    "Complete 10 Quantitative Aptitude mock modules",
                    "Conduct peer interview simulation for technical design"
                ]
            })
        )
        db.add(stu)
        db.commit()
        student_objs.append(stu)

    print("Seeding Applications across Pipeline Stages...")
    # Pipeline stages: APPLIED, ELIGIBLE, AI_SHORTLISTED, ASSESSMENT, INTERVIEW, SELECTED, OFFER_GENERATED, OFFER_ACCEPTED, JOINING_PENDING, JOINED, REJECTED
    # Let's create realistic applications:
    # Rahul Sharma (index 0) -> Applied for TechNova (Drive 1) and CodeSphere (Drive 2)
    # Priya Patel (index 1) -> Offer Accepted for CodeSphere (Drive 2)
    # Karthik Nair (index 8) -> Joined TechNova (Drive 1) with 8.5 LPA
    # Sneha Reddy (index 3) -> Selected for DataPulse (Drive 4)

    # Drive 1 (TechNova - Java Developer) applications
    app_configs = [
        # Student 0 (Rahul) -> Shortlisted for TechNova
        {"stu_idx": 0, "job_idx": 0, "drive_idx": 0, "status": "AI_SHORTLISTED"},
        # Student 0 (Rahul) -> Shortlisted for CodeSphere (triggers candidate clash with Drive 1!)
        {"stu_idx": 0, "job_idx": 1, "drive_idx": 1, "status": "AI_SHORTLISTED"},
        # Student 1 (Priya) -> Offer Accepted for CodeSphere
        {"stu_idx": 1, "job_idx": 1, "drive_idx": 1, "status": "OFFER_ACCEPTED"},
        # Student 8 (Karthik) -> Joined TechNova
        {"stu_idx": 8, "job_idx": 0, "drive_idx": 0, "status": "JOINED"},
        # Student 3 (Sneha) -> Selected for DataPulse AI
        {"stu_idx": 3, "job_idx": 3, "drive_idx": 3, "status": "SELECTED"},
        # Student 4 (Rohan) -> Interview for CloudMatrix
        {"stu_idx": 4, "job_idx": 2, "drive_idx": 2, "status": "INTERVIEW"},
        # Student 5 (Anjali) -> Assessment for InnovateX
        {"stu_idx": 5, "job_idx": 5, "drive_idx": 4, "status": "ASSESSMENT"},
        # Student 13 (Meera) -> Offer Generated for TechNova
        {"stu_idx": 13, "job_idx": 0, "drive_idx": 0, "status": "OFFER_GENERATED"},
        # Student 14 (Arjun) -> Interview for CodeSphere
        {"stu_idx": 14, "job_idx": 1, "drive_idx": 1, "status": "INTERVIEW"},
        # Student 2 (Amit) -> Rejected for TechNova
        {"stu_idx": 2, "job_idx": 0, "drive_idx": 0, "status": "REJECTED"},
        # Student 10 (Manoj) -> Rejected for TechNova
        {"stu_idx": 10, "job_idx": 0, "drive_idx": 0, "status": "REJECTED"},
        # More applications for realistic volume
        {"stu_idx": 7, "job_idx": 4, "drive_idx": None, "status": "SELECTED"}, # Neha Data Analyst
        {"stu_idx": 9, "job_idx": 5, "drive_idx": 4, "status": "INTERVIEW"},
        {"stu_idx": 11, "job_idx": 1, "drive_idx": 1, "status": "AI_SHORTLISTED"},
        {"stu_idx": 15, "job_idx": 0, "drive_idx": 0, "status": "ELIGIBLE"},
        {"stu_idx": 16, "job_idx": 0, "drive_idx": 0, "status": "APPLIED"},
        {"stu_idx": 17, "job_idx": 1, "drive_idx": 1, "status": "APPLIED"},
        {"stu_idx": 18, "job_idx": 2, "drive_idx": 2, "status": "ELIGIBLE"},
        {"stu_idx": 19, "job_idx": 3, "drive_idx": 3, "status": "APPLIED"},
        {"stu_idx": 20, "job_idx": 4, "drive_idx": None, "status": "APPLIED"}
    ]

    for cfg in app_configs:
        stu = student_objs[cfg["stu_idx"]]
        job = job_objs[cfg["job_idx"]]
        drv = drive_objs[cfg["drive_idx"]] if cfg["drive_idx"] is not None else None
        
        match_res = AIEngine.calculate_hybrid_match(stu, job)
        app = models.Application(
            student_id=stu.id,
            job_id=job.id,
            drive_id=drv.id if drv else None,
            status=cfg["status"],
            match_score=match_res["fit_score"],
            match_explanation=json.dumps(match_res)
        )
        db.add(app)
        db.commit()

        # Seed Interviews for relevant statuses
        if cfg["status"] in ["INTERVIEW", "SELECTED", "OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]:
            it_status = "SCHEDULED" if cfg["status"] == "INTERVIEW" else "COMPLETED"
            it_rec = "SELECT" if cfg["status"] != "INTERVIEW" else "PROGRESS"
            interview = models.Interview(
                application_id=app.id,
                student_id=stu.id,
                drive_id=drv.id if drv else None,
                round_name="Technical Round 1" if cfg["status"] == "INTERVIEW" else "Final Technical & HR Round",
                scheduled_time="2026-10-18 10:30 AM" if cfg["status"] == "INTERVIEW" else "2026-10-05 02:00 PM",
                interviewer_panel="Panel A - Technical",
                status=it_status,
                feedback="Candidate demonstrated strong knowledge of core DSA, Spring Boot architecture, and SQL querying." if it_status == "COMPLETED" else "Scheduled for interactive problem-solving round.",
                technical_rating=8.5 if it_status == "COMPLETED" else 7.5,
                comm_rating=8.0 if it_status == "COMPLETED" else 7.0,
                recommendation=it_rec
            )
            db.add(interview)
            db.commit()

        # Seed Offers for relevant statuses
        if cfg["status"] in ["OFFER_GENERATED", "OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"]:
            acceptance = "ACCEPTED" if cfg["status"] in ["OFFER_ACCEPTED", "JOINING_PENDING", "JOINED"] else "PENDING"
            joining = "JOINED" if cfg["status"] == "JOINED" else ("PENDING" if cfg["status"] in ["OFFER_ACCEPTED", "JOINING_PENDING"] else "PENDING")
            doc_status = "VERIFIED" if cfg["status"] == "JOINED" else ("SUBMITTED" if cfg["status"] == "OFFER_ACCEPTED" else "PENDING")
            
            offer = models.Offer(
                application_id=app.id,
                student_id=stu.id,
                recruiter_id=job.recruiter_id,
                job_id=job.id,
                company_name=job.recruiter.company_name,
                role_title=job.title,
                ctc_lpa=job.ctc_lpa,
                offer_date="2026-10-01",
                acceptance_status=acceptance,
                joining_date="2026-12-01",
                joining_status=joining,
                documentation_status=doc_status,
                remarks=f"Official corporate placement offer for {job.title} at {job.ctc_lpa} LPA."
            )
            db.add(offer)
            db.commit()

        # Seed sample notifications for student
        notif = models.Notification(
            user_id=stu.user_id,
            title=f"Application Update: {job.title}",
            message=f"Your application status for {job.title} at {job.recruiter.company_name} is now: {cfg['status'].replace('_', ' ')}.",
            category="SHORTLIST" if "SHORTLIST" in cfg["status"] else "SYSTEM",
            is_read=False
        )
        db.add(notif)
        db.commit()

    # Seed Sample Documents for Student 1 (Rahul)
    sample_docs = [
        {"title": "Rahul_Sharma_Resume_2026.pdf", "type": "RESUME", "status": "VERIFIED"},
        {"title": "Academic_Consolidated_Marksheet.pdf", "type": "ACADEMIC_DOC", "status": "VERIFIED"},
        {"title": "Aadhaar_National_ID.pdf", "type": "ID_PROOF", "status": "VERIFIED"},
        {"title": "Oracle_Java_Associate_Cert.pdf", "type": "CERTIFICATE", "status": "VERIFIED"}
    ]
    for doc in sample_docs:
        d = models.Document(
            student_id=student_objs[0].id,
            doc_type=doc["type"],
            title=doc["title"],
            file_url=f"/uploads/{doc['title']}",
            status=doc["status"],
            verified_by="TPO Office"
        )
        db.add(d)

    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
