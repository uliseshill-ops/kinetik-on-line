from fastapi import FastAPI, Depends, HTTPException, Header, Body, UploadFile, File
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from pydantic import BaseModel
from typing import Optional, List, Union
from ai_helper import generar_storytelling_mexicano
import os
from supabase import create_client, Client

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hecho en México API - E-commerce Engine",
    description="Backend optimizado para inventarios KINETIK con IA e integración de Supabase Storage",
    version="3.2.1"
)

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "ulises_pro_2026")

# Configuración de Supabase Storage en la Nube
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-service-role-o-anon-key")
SUPABASE_BUCKET = "galeria-prendas"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductoSchema(BaseModel):
    codigo: str
    prenda: str
    descripcion_original: str
    precio_costo: float
    precio_venta: float
    color: str
    existencia: int
    imagen_url: Optional[str] = None  
    imagenes: Optional[Union[str, List[str]]] = []
    precio_mayoreo: Optional[float] = 0.0
    departamento: Optional[str] = "GENERAL"
    inventario_minimo: Optional[int] = 0
    inventario_maximo: Optional[int] = 0
    genero: Optional[str] = None
    tipo_tela: Optional[str] = None
    corte: Optional[str] = None
    proveedor: Optional[str] = None
    talla: Optional[str] = None
    costo_indirecto: Optional[float] = 0.0
    margen: Optional[float] = 0.0
    codigo_barras: Optional[str] = None
    columna: Optional[str] = None
    caja: Optional[str] = None

@app.post("/subir-imagen-supabase/")
async def subir_imagen_supabase(
    codigo: str, 
    file: UploadFile = File(...), 
    x_token: str = Header(None)
):
    if x_token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Acceso denegado: Token inválido, compa.")
    
    try:
        contents = await file.read()
        file_path = f"{codigo}_{file.filename}"
        
        # Subida directa al Bucket público de Supabase Storage
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            file_path, 
            contents, 
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        
        # Obtenemos la URL pública permanente
        public_url_res = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        
        return {
            "mensaje": "¡Imagen almacenada con éxito en Supabase Storage!", 
            "imagen_url": public_url_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen al Storage: {str(e)}")

@app.post("/crear-producto/")
def crear_producto(
    producto: ProductoSchema, 
    db: Session = Depends(get_db), 
    x_token: str = Header(None)
):
    if x_token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Acceso denegado: Token inválido, compa.")

    producto_existente = db.query(models.ProductoDB).filter(models.ProductoDB.codigo == producto.codigo).first()
    if producto_existente:
        raise HTTPException(status_code=400, detail=f"El código '{producto.codigo}' ya existe en el inventario.")

    contexto = f"Color: {producto.color}. Tela: {producto.tipo_tela or ''}. Proveedor: {producto.proveedor or ''}"
    
    try:
        historia = generar_storytelling_mexicano(producto.descripcion_original, contexto, producto.departamento or "MEXICO")
        if not historia:
            historia = "[ESPAÑOL]\nPrenda de excelente calidad Hecho en México.\n\n[ENGLISH]\nPremium product proudly Made in Mexico."
    except Exception as ai_err:
        print(f"⚠️ Aviso en backend: La IA no respondió ({ai_err}). Usando historia de respaldo.")
        historia = "[ESPAÑOL]\nPrenda deportiva de alta calidad Hecho en México, diseñada para impulsar tu estilo.\n\n[ENGLISH]\nHigh-end sportswear proudly Made in Mexico."

    datos_producto = producto.dict(exclude={'imagenes'})
    nuevo_producto = models.ProductoDB(
        **datos_producto,
        historia_ia=historia
    )
    
    db.add(nuevo_producto)
    
    urls_a_guardar = []
    if isinstance(producto.imagenes, str):
        try:
            import ast
            parsed = ast.literal_eval(producto.imagenes)
            if isinstance(parsed, list):
                urls_a_guardar = parsed
            else:
                urls_a_guardar = [producto.imagenes]
        except Exception:
            urls_a_guardar = [producto.imagenes] if producto.imagenes else []
    elif isinstance(producto.imagenes, list):
        urls_a_guardar = producto.imagenes

    if producto.imagen_url and producto.imagen_url not in urls_a_guardar:
        urls_a_guardar.insert(0, producto.imagen_url)
        
    for url_img in urls_a_guardar:
        if str(url_img).strip() and str(url_img).strip().lower() not in ["nan", "none"]:
            nueva_img = models.ProductoImagenDB(codigo=producto.codigo, imagen_url=str(url_img).strip())
            db.add(nueva_img)
    
    db.commit()
    db.refresh(nuevo_producto)
    
    return {
        "mensaje": "¡Producto con galería en Supabase guardado exitosamente!", 
        "codigo": nuevo_producto.codigo, 
        "historia": historia,
        "imagenes": urls_a_guardar
    }

@app.put("/actualizar-fotos/{codigo}")
def actualizar_fotos(
    codigo: str, 
    imagenes: List[str] = Body(..., embed=True), 
    modo: str = Body("agregar", embed=True),
    db: Session = Depends(get_db), 
    x_token: str = Header(None)
):
    if x_token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Acceso denegado: Token inválido, compa.")
    
    producto = db.query(models.ProductoDB).filter(models.ProductoDB.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail=f"El producto con código '{codigo}' no existe.")
    
    try:
        # Consultamos explícitamente las imágenes asociadas en la tabla relacional
        imagenes_existentes_db = db.query(models.ProductoImagenDB).filter(
            models.ProductoImagenDB.codigo == codigo
        ).all()
        
        if modo == "reemplazar":
            db.query(models.ProductoImagenDB).filter(models.ProductoImagenDB.codigo == codigo).delete()
            urls_finales = []
        else:
            urls_finales = [img.imagen_url for img in imagenes_existentes_db] if imagenes_existentes_db else []
        
        for url_img in imagenes:
            if url_img not in urls_finales:
                urls_finales.append(url_img)
                nueva_img = models.ProductoImagenDB(codigo=codigo, imagen_url=url_img)
                db.add(nueva_img)
        
        if urls_finales:
            producto.imagen_url = urls_finales[0]
        else:
            producto.imagen_url = None
            
        db.commit()
        return {
            "mensaje": f"¡Galería actualizada en Supabase en modo '{modo}' para el SKU {codigo}!", 
            "imagenes": urls_finales
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al actualizar galería: {str(e)}")

@app.get("/productos/")
def obtener_productos(db: Session = Depends(get_db)):
    try:
        productos = db.query(models.ProductoDB).all()
        resultado = []
        for p in productos:
            p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
            imagenes_asociadas = db.query(models.ProductoImagenDB).filter(
                models.ProductoImagenDB.codigo == p.codigo
            ).all()
            
            p_dict['imagenes'] = [img.imagen_url for img in imagenes_asociadas] if imagenes_asociadas else []
            
            if not p_dict['imagenes'] and p_dict.get('imagen_url'):
                p_dict['imagenes'] = [p_dict['imagen_url']]
            
            if not p_dict.get('imagen_url') and p_dict['imagenes']:
                p_dict['imagen_url'] = p_dict['imagenes'][0]
                
            resultado.append(p_dict)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")