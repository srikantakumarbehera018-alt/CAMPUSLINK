import urllib.request
import urllib.parse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body
            return status, parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return e.code, parsed
    except Exception as e:
        return 0, str(e)

def run_tests():
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("CAMPUSLINK COMPREHENSIVE END-TO-END VERIFICATION")
    print("="*70)

    # 1. Landing page & Static HTML check
    st, html = request("GET", "/")
    if st == 200 and "student-profile-modal" in html and "schedule-interview-modal" in html and "interview-feedback-modal" in html and "create-drive-modal" in html and "create-offer-modal" in html:
        print("[PASS] 1. Static HTML serves all 5 modals correctly")
        passed += 1
    else:
        print(f"[FAIL] 1. Static HTML check failed (status: {st})")
        failed += 1

    # 2. Static JS check
    st, js = request("GET", "/static/js/app.js")
    if st == 200 and "openStudentProfileModal" in js and "openScheduleInterviewModal" in js and "respondToOffer" in js and "openCreateOfferModal" in js and "openCreateDriveModal" in js:
        print("[PASS] 2. Static JS serves all interactive modal and action handlers")
        passed += 1
    else:
        print(f"[FAIL] 2. Static JS check failed (status: {st})")
        failed += 1

    # 3. Student Rahul login
    st, res = request("POST", "/api/auth/login", {"email": "rahul@campuslink.edu", "password": "password123"})
    if st == 200 and "access_token" in res and res.get("role") == "STUDENT":
        student_token = res["access_token"]
        student_user_id = res["user_id"]
        print(f"[PASS] 3. Student Rahul authenticated successfully (user_id: {student_user_id})")
        passed += 1
    else:
        print(f"[FAIL] 3. Student login failed: {res}")
        failed += 1
        return

    # 4. Fetch Student Profile and Readiness
    student_id = res["profile_id"]
    st, me = request("GET", f"/api/students/{student_id}", token=student_token)
    if st == 200 and me.get("id"):
        print(f"[PASS] 4. Student profile retrieved for ID {student_id} ({me.get('full_name')})")
        passed += 1
    else:
        print(f"[FAIL] 4. Student profile fetch failed: {me}")
        failed += 1

    # 5. Student Readiness Score (5-factor model)
    st, readiness = request("GET", f"/api/students/{student_id}/readiness", token=student_token)
    if st == 200 and "readiness_score" in readiness and "dimensions" in readiness:
        print(f"[PASS] 5. Readiness score: {readiness['readiness_score']}% (Dimensions: {list(readiness['dimensions'].keys())})")
        passed += 1
    else:
        print(f"[FAIL] 5. Readiness score fetch failed: {readiness}")
        failed += 1

    # 6. Student Edit Profile
    orig_bio = me.get("bio") or ""
    test_bio = orig_bio + " [Certified Cloud Enthusiast]" if "[Certified Cloud Enthusiast]" not in orig_bio else orig_bio
    st, updated_student = request("PUT", f"/api/students/{student_id}", {"bio": test_bio, "phone": "+91-9876543219"}, token=student_token)
    if st == 200 and "+91-9876543219" in updated_student.get("phone", ""):
        print("[PASS] 6. Student profile updated successfully via PUT /api/students/{id}")
        passed += 1
    else:
        print(f"[FAIL] 6. Student profile update failed: {updated_student}")
        failed += 1

    # 7. Student Interviews Retrieval
    st, student_interviews = request("GET", f"/api/interviews?student_id={student_id}", token=student_token)
    if st == 200 and isinstance(student_interviews, list):
        print(f"[PASS] 7. Student interviews retrieved ({len(student_interviews)} rounds found)")
        passed += 1
    else:
        print(f"[FAIL] 7. Student interviews retrieval failed: {student_interviews}")
        failed += 1

    # 8. Recruiter Login
    st, res = request("POST", "/api/auth/login", {"email": "recruiter@technova.com", "password": "password123"})
    if st == 200 and "access_token" in res and res.get("role") == "RECRUITER":
        recruiter_token = res["access_token"]
        print("[PASS] 8. Recruiter authenticated successfully (TechNova HR)")
        passed += 1
    else:
        print(f"[FAIL] 8. Recruiter login failed: {res}")
        failed += 1
        return

    # 9. Recruiter Candidate Ranking for Job 1
    st, candidates_res = request("GET", "/api/jobs/1/candidates", token=recruiter_token)
    cand_list = candidates_res.get("candidates", []) if isinstance(candidates_res, dict) else candidates_res
    if st == 200 and isinstance(cand_list, list) and len(cand_list) > 0:
        first_cand = cand_list[0]
        print(f"[PASS] 9. AI Candidate Ranking verified: {len(cand_list)} ranked candidates (Top: {first_cand.get('name', first_cand.get('student_name'))} with fit score {first_cand.get('fit_score')}%)")
        passed += 1
    else:
        print(f"[FAIL] 9. Candidate ranking failed: {candidates_res}")
        failed += 1

    # 10. Recruiter Schedule New Interview
    # Check applications for job 1
    st, apps = request("GET", "/api/applications?job_id=1", token=recruiter_token)
    target_app_id = apps[0]["id"] if (st == 200 and len(apps) > 0) else 1
    st, new_interview = request("POST", "/api/interviews", {
        "application_id": target_app_id,
        "round_number": 2,
        "round_type": "Technical Round 2 - System Architecture",
        "scheduled_time": "2026-10-15T14:30:00",
        "duration_minutes": 45,
        "venue": "Virtual Link (Google Meet)",
        "interviewer_names": "Alex Turner, Principal Architect"
    }, token=recruiter_token)
    if st in [200, 201] and new_interview.get("id"):
        created_int_id = new_interview["id"]
        print(f"[PASS] 10. Recruiter scheduled interview #{created_int_id} (Round 2)")
        passed += 1
    else:
        print(f"[FAIL] 10. Recruiter interview schedule failed: {new_interview}")
        failed += 1
        created_int_id = None

    # 11. Recruiter Submit Evaluation Feedback
    if created_int_id:
        st, feedback_res = request("PUT", f"/api/interviews/{created_int_id}", {
            "technical_rating": 8.5,
            "comm_rating": 8.0,
            "feedback": "Strong algorithmic thinking, solid distributed systems knowledge.",
            "recommendation": "SELECT",
            "status": "COMPLETED"
        }, token=recruiter_token)
        if st == 200 and feedback_res.get("technical_rating") == 8.5:
            print("[PASS] 11. Recruiter submitted evaluation feedback successfully")
            passed += 1
        else:
            print(f"[FAIL] 11. Interview feedback submission failed: {feedback_res}")
            failed += 1

    # 12. TPO Admin Login
    st, res = request("POST", "/api/auth/login", {"email": "tpo@campuslink.edu", "password": "admin123"})
    if st == 200 and "access_token" in res and res.get("role") == "TPO_ADMIN":
        tpo_token = res["access_token"]
        print("[PASS] 12. TPO Admin authenticated successfully (Prof. Verma)")
        passed += 1
    else:
        print(f"[FAIL] 12. TPO login failed: {res}")
        failed += 1
        return

    # 13. TPO Drive Creation & Conflict Check
    st, drive_res = request("POST", "/api/scheduling/drives", {
        "company_name": "Atlassian",
        "role_title": "Cloud Reliability Engineer",
        "drive_date": "2026-10-25",
        "start_time": "10:00 AM",
        "end_time": "02:00 PM",
        "venue": "Seminar Hall A",
        "panel_name": "Cloud Panel 1"
    }, token=tpo_token)
    if st in [200, 201] and drive_res.get("id"):
        created_drive_id = drive_res["id"]
        print(f"[PASS] 13. TPO created placement drive #{created_drive_id} (Conflict check passed)")
        passed += 1
    else:
        print(f"[FAIL] 13. TPO drive creation failed: {drive_res}")
        failed += 1

    # 14. TPO Create Offer
    st, offer_res = request("POST", "/api/admin/offers", {
        "student_id": student_id,
        "company_name": "TechNova",
        "role_title": "Full Stack Engineer",
        "ctc_lpa": 14.5,
        "offer_date": "2026-10-10",
        "joining_date": "2027-07-01"
    }, token=tpo_token)
    if st in [200, 201] and offer_res.get("id"):
        created_offer_id = offer_res["id"]
        print(f"[PASS] 14. TPO created job offer #{created_offer_id} for student {student_id}")
        passed += 1
    else:
        print(f"[FAIL] 14. TPO offer creation failed: {offer_res}")
        failed += 1
        created_offer_id = None

    # 15. Student Accept Offer
    if created_offer_id:
        st, accept_res = request("POST", f"/api/students/{student_id}/offers/{created_offer_id}/respond", {
            "action": "ACCEPT"
        }, token=student_token)
        if st == 200 and accept_res.get("acceptance_status") == "ACCEPTED":
            print(f"[PASS] 15. Student responded to offer #{created_offer_id} with ACCEPT (Status: {accept_res.get('acceptance_status')})")
            passed += 1
        else:
            print(f"[FAIL] 15. Student offer response failed: {accept_res}")
            failed += 1

    # 16. Analytics Dashboard KPIs
    st, kpis = request("GET", "/api/analytics/dashboard", token=tpo_token)
    if st == 200 and "total_students" in kpis and "placement_percentage" in kpis and "offers_made" in kpis:
        print(f"[PASS] 16. Placement Analytics KPIs: {kpis['placement_percentage']}% placed, Avg Package: {kpis['average_package_lpa']} LPA, Total Offers: {kpis['offers_made']}")
        passed += 1
    else:
        print(f"[FAIL] 16. Analytics KPIs failed: {kpis}")
        failed += 1

    # 17. At-Risk / Skill Gap Recommendations
    st, at_risk = request("GET", "/api/analytics/at-risk", token=tpo_token)
    if st == 200 and isinstance(at_risk, list) and len(at_risk) > 0:
        print(f"[PASS] 17. At-Risk analysis identified {len(at_risk)} students with tailored recovery recommendations")
        passed += 1
    else:
        print(f"[FAIL] 17. At-Risk analysis failed: {at_risk}")
        failed += 1

    # 18. In-App Notifications check
    st, notifs = request("GET", "/api/notifications", token=student_token)
    if st == 200 and isinstance(notifs, list) and len(notifs) > 0:
        print(f"[PASS] 18. Notifications engine confirmed ({len(notifs)} notifications for student, latest: '{notifs[0].get('title')}')")
        passed += 1
    else:
        print(f"[FAIL] 18. Notifications check failed: {notifs}")
        failed += 1

    # 19. AI Assistant Chat Query
    st, ai_res = request("POST", "/api/assistant/chat", {
        "message": "What are the key technical skills needed for Cloud Engineer roles?",
        "student_id": student_id
    }, token=student_token)
    if st == 200 and "reply" in ai_res and len(ai_res["reply"]) > 20:
        print(f"[PASS] 19. AI Placement Assistant reply: '{ai_res['reply'][:60]}...'")
        passed += 1
    else:
        print(f"[FAIL] 19. AI Assistant chat failed: {ai_res}")
        failed += 1

    print("\n" + "="*70)
    print(f"VERIFICATION RESULTS: {passed} PASSED, {failed} FAILED")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_tests()
