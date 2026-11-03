from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    # Llave primaria oficial y estricta
    codigo = Column(String, primary_key=True, index=True) 
    imagen_url = Column(String, nullable=True) # Mantener para retrocompatibilidad
    prenda = Column(String)
    descripcion_original = Column(String)
    precio_costo = Column(Float)
    precio_venta = Column(Float)
    color = Column(String)
    precio_mayoreo = Column(Float, default=0.0)
    departamento = Column(String, default="GENERAL")
    existencia = Column(Integer, default=0)
    inventario_minimo = Column(Integer, default=0)
    inventario_maximo = Column(Integer, default=0)
    
    # Atributos extendidos del layout oficial
    genero = Column(String, nullable=True)
    tipo_tela = Column(String, nullable=True)
    corte = Column(String, nullable=True)
    proveedor = Column(String, nullable=True)
    talla = Column(String, nullable=True)
    costo_indirecto = Column(Float, default=0.0)
    margen = Column(Float, default=0.0)
    codigo_barras = Column(String, nullable=True)
    columna = Column(String, nullable=True)
    caja = Column(String, nullable=True)
    
    # IA y auditoría
    historia_ia = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.datetime('now', 'localtime'))
    
    # Relación uno a muchos para múltiples imágenes de la galería
    imagenes = relationship("ProductoImagenDB", back_populates="producto", cascade="all, delete-orphan")

class ProductoImagenDB(Base):
    __tablename__ = "producto_imagenes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, ForeignKey("productos.codigo"), index=True)
    imagen_url = Column(String, nullable=False)
    
    producto = relationship("ProductoDB", back_populates="imagenes")