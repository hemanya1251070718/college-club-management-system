import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-vit-cloud-2026")
    
    # Database Settings
    DB_USER = os.environ.get("DB_USER", "root").strip()
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "").strip()
    DB_NAME = os.environ.get("DB_NAME", "trial_club").strip()
    
    # TCP Connection (used locally and for Cloud SQL Auth Proxy)
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    
    # Cloud SQL Unix Socket Connection (used inside Cloud Run runtime)
    # Format: PROJECT-ID:REGION:INSTANCE-NAME
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
    DB_SOCKET_DIR = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
