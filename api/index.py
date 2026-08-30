import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
back_dir = os.path.join(parent_dir, "Back")
vendor_dir = os.path.join(back_dir, "vendor")

if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)
if back_dir not in sys.path:
    sys.path.insert(0, back_dir)

from app.main import app
