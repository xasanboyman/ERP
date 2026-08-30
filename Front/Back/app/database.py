from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

from sqlalchemy.engine import Engine
from sqlalchemy import event

import ssl

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

db_url = settings.DATABASE_URL
connect_args = {}

if is_sqlite:
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
        except Exception:
            pass
    connect_args["check_same_thread"] = False
else:
    # Use pure Python pg8000 driver for 100% serverless compatibility
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgresql://") and "+pg8000" not in db_url and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    
    # Strip any parameters unsupported by pg8000 query string
    if "?" in db_url:
        base_part, query_part = db_url.split("?", 1)
        db_url = base_part
    ctx = ssl.create_default_context()
    connect_args["ssl_context"] = ctx

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

