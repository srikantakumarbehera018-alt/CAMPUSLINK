import os
import sys

# Support UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in path
backend_dir = os.path.join(os.path.dirname(__file__), "campuslink", "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CAMPUSLINK -- AI-Powered Campus-to-Corporate Placement Platform")
    print("="*70)
    print("Server starting at: http://localhost:8000")
    print("Open your browser and navigate to: http://localhost:8000")
    print("\nDemo Credentials:")
    print("- Student (Rahul Sharma):   rahul@campuslink.edu    / password123")
    print("- Recruiter (TechNova HR):  recruiter@technova.com  / password123")
    print("- TPO Admin (Prof. Verma):  tpo@campuslink.edu      / admin123")
    print("="*70 + "\n")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
