import os

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "erp-super-secret-key-123456")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    _raw_db_url = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'erp.db')}")
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL: str = _raw_db_url

settings = Settings()
