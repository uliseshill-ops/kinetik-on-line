from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    codigo = Column(String, primary_key=True, index=True) # Tu llave primaria real
    prenda = Column(String)
    descripcion_original = Column(String)
    precio_costo = Column(Float)
    precio_venta = Column(Float)
    color = Column(String)
    precio_mayoreo = Column(Float)
    departamento = Column(String)
    existencia = Column(Integer, default=0)
    inventario_minimo = Column(Integer, default=0)
    inventario_maximo = Column(Integer, default=0)
    historia_ia = Column(String)
    # Cambiado a func.current_timestamp() para que funcione perfecto en PostgreSQL y SQLite
    created_at = Column(DateTime, server_default=func.current_timestamp())