import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# Database
MONGO_URL = os.environ.get('MONGO_URL', '')
DB_NAME = os.environ.get('DB_NAME', '')

# JWT and Security
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# AI Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
