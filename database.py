import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Obtenemos la URL de Supabase desde las variables de entorno de Render
raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.roqxbebwjtyqxfcxbnos:K1n3t1k2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)

if raw_url:
    # Forzamos el uso del driver psycopg2 explícitamente
    if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
        raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)

    # 2. Limpiamos parámetros que psycopg2 no soporta en el DSN (como pgbouncer=true)
    parsed = urlparse(raw_url)
    qsl = parse_qsl(parsed.query)
    # Filtramos cualquier variable que contenga pgbouncer
    filtered_qsl = [(k, v) for k, v in qsl if k.lower() != 'pgbouncer']
    new_query = urlencode(filtered_qsl)
    parsed = parsed._replace(query=new_query)
    SQLALCHEMY_DATABASE_URL = urlunparse(parsed)
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres.roqxbebwjtyqxfcxbnos:K1n3t1k2026!@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# 3. Motor configurado para la nube de Supabase
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()