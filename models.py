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
    
    # Columnas complementarias y de galería que exige el main.py
    imagen_url = Column(String, nullable=True)
    genero = Column(String, nullable=True)
    tipo_tela = Column(String, nullable=True)
    corte = Column(String, nullable=True)
    proveedor = Column(String, nullable=True)
    talla = Column(String, nullable=True)
    costo_indirecto = Column(Float, nullable=True, default=0.0)
    margen = Column(Float, nullable=True, default=0.0)
    codigo_barras = Column(String, nullable=True)
    columna = Column(String, nullable=True)
    caja = Column(String, nullable=True)
    
    historia_ia = Column(String)
    created_at = Column(DateTime, server_default=func.datetime('now', 'localtime'))

# Modelo relacional secundario para la galería múltiple de fotos
class ProductoImagenDB(Base):
    __tablename__ = "producto_imagenes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, index=True)
    imagen_url = Column(String)