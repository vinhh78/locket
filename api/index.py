import os
import sys

# Ensure parent directory is in sys.path so app and other modules can be imported on Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import app
