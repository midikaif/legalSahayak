import sys
import os

# Add the current directory (api/) to the Python path
# so Vercel can find the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
