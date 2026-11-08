from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Cambiamos SQLite por la URL de PostgreSQL en Supabase (vía PgBouncer puerto 6543)
# Asegúrate de poner tu contraseña real de Supabase donde va [TU-PASSWORD]
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.roqxbebwjtyqxfcxbnos:[TU-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()