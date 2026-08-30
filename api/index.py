import os
import sys

# Add Back directory to Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
back_dir = os.path.join(parent_dir, "Back")

if back_dir not in sys.path:
    sys.path.insert(0, back_dir)

from app.main import app

# Export app for Vercel Serverless Function handler
# Vercel's @vercel/python automatically adapts ASGI/FastAPI apps
