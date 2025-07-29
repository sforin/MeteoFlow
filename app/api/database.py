from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger
import os

logger = get_logger("api_database")

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_database_url():
    DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "meteo_data")
    DB_USER = os.getenv("POSTGRES_USER", "meteo_user")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "meteo_password")

    logger.debug(f"[DEBUG] Connecting to DB {DB_NAME} on {DB_HOST}:{DB_PORT} as {DB_USER}")

    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


