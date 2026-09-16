import os
from dotenv import load_dotenv

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_base_dir, ".env"))
load_dotenv(os.path.join(os.path.dirname(_base_dir), ".env.local"))

DEFAULT_ORACLE_DB = "postgresql://admin:xusanboyman@127.0.0.1:5432/erp_db?sslmode=disable"

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-that-is-hard-to-guess")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    BASE_DIR = _base_dir
    
    _raw_db_url = os.getenv("DATABASE_URL", DEFAULT_ORACLE_DB)
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    if "channel_binding=require" in _raw_db_url:
        _raw_db_url = _raw_db_url.replace("&channel_binding=require", "").replace("channel_binding=require", "")
    DATABASE_URL: str = _raw_db_url

    AWS_ENDPOINT_URL_S3: str = os.getenv("AWS_ENDPOINT_URL_S3", "https://br-snowy-king-a5r6m9o9.storage.c-1.us-east-2.aws.neon.tech")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "nak_live_3fcb23e96014402c8f51b7dad1948b5f")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "nsk_live_f38b3b6f1c7628e89639b594c862e16ff25394bcbc653ea8d2ff32ee501e1c1f")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "uploads")

settings = Settings()
