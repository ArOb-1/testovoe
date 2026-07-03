import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """Настройки приложения"""

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./employees.db")

    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    MAX_UPLOAD_SIZE = 200 * 1024
    UPLOAD_DIR = "static/uploads"

    PAGE_SIZE = 8


config = Config()
