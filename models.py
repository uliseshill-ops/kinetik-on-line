from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    codigo = Column(String, primary_key=True, index=True) # Llave primaria oficial
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
    imagen_url = Column(String, nullable=True)
    historia_ia = Column(String)
    
    # Marca de tiempo universal (Compatible con PostgreSQL y SQLite)
    created_at = Column(DateTime, server_default=func.current_timestamp())

# Modelo relacional secundario para la galería múltiple de fotos
class ProductoImagenDB(Base):
    __tablename__ = "producto_imagenes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, index=True)
    imagen_url = Column(String)