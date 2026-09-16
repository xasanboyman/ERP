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
    try:
        import psycopg2
        has_psycopg2 = True
    except ImportError:
        has_psycopg2 = False

    if has_psycopg2:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        elif db_url.startswith("postgresql+pg8000://"):
            db_url = db_url.replace("postgresql+pg8000://", "postgresql://", 1)
        if "sslmode=" not in db_url:
            separator = "&" if "?" in db_url else "?"
            if "127.0.0.1" in db_url or "localhost" in db_url:
                db_url = f"{db_url}{separator}sslmode=disable"
            else:
                db_url = f"{db_url}{separator}sslmode=require"
        connect_args["connect_timeout"] = 10
        connect_args["keepalives"] = 1
        connect_args["keepalives_idle"] = 30
        connect_args["keepalives_interval"] = 10
        connect_args["keepalives_count"] = 5
    else:
        # Fallback to pure Python pg8000 driver for serverless environments
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
        elif db_url.startswith("postgresql://") and "+pg8000" not in db_url and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
        if "?" in db_url:
            base_part, query_part = db_url.split("?", 1)
            db_url = base_part
        ctx = ssl.create_default_context()
        connect_args["ssl_context"] = ctx

engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}
if not is_sqlite:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

