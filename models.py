from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    codigo = Column(String, primary_key=True, index=True) # Tu llave primaria real
    prenda = Column(String)[cite: 15]
    descripcion_original = Column(String)[cite: 15]
    precio_costo = Column(Float)[cite: 15]
    precio_venta = Column(Float)[cite: 15]
    color = Column(String)[cite: 15]
    precio_mayoreo = Column(Float)[cite: 15]
    departamento = Column(String)[cite: 15]
    existencia = Column(Integer, default=0)[cite: 15]
    inventario_minimo = Column(Integer, default=0)[cite: 15]
    inventario_maximo = Column(Integer, default=0)[cite: 15]
    
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
    
    historia_ia = Column(String)[cite: 15]
    created_at = Column(DateTime, server_default=func.datetime('now', 'localtime'))[cite: 15]

# Modelo relacional secundario para la galería múltiple de fotos
class ProductoImagenDB(Base):
    __tablename__ = "producto_imagenes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, index=True)
    imagen_url = Column(String)