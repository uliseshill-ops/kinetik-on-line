import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Obtenemos la URL de Supabase desde las variables de entorno de Render
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Forzamos el uso del driver psycopg2 para que SQLAlchemy no busque 'psycopg' (v3)
if SQLALCHEMY_DATABASE_URL:
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql://") and not SQLALCHEMY_DATABASE_URL.startswith("postgresql+"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    # Respaldo directo en caso de emergencia local
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres.roqxbebwjtyqxfcxbnos:K1n3t1k2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# 3. Motor configurado para la nube de Supabase
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()