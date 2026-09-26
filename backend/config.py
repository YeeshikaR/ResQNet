import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'emergency_db')
JWT_SECRET = os.getenv('JWT_SECRET', 'change-this-development-secret')
JWT_ALGORITHM = 'HS256'
GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY', '')
USE_ML_PRIORITY = os.getenv('USE_ML_PRIORITY', 'false').lower() == 'true'
MODEL_PATH = Path(os.getenv('MODEL_PATH', str(Path(__file__).parent / 'ml' / 'priority_model.joblib')))
