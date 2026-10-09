import os
import sys

# Ensure campuslink/backend is in Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "..", "campuslink", "backend")
backend_dir = os.path.abspath(backend_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the FastAPI application instance
from main import app
