from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Cadena de conexión hacia Supabase PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.roqxbebwjtyqxfcxbnos:K1n3t1k2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)

# En PostgreSQL no se usa check_same_thread
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()