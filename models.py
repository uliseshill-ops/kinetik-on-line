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
    
    total_likes = Column(Integer, default=0)
    
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

class ProductoImagenDB(Base):
    __tablename__ = "producto_imagenes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, index=True)
    imagen_url = Column(String)

# <--- ¡ NUEVA TABLA PARA AUDITORÍA Y ANALÍTICA DE PRECIOS ! --->
class HistorialPrecioDB(Base):
    __tablename__ = "historial_precios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, index=True)
    precio_costo_anterior = Column(Float)
    precio_costo_nuevo = Column(Float)
    precio_venta_anterior = Column(Float)
    precio_venta_nuevo = Column(Float)
    fecha_cambio = Column(DateTime, server_default=func.datetime('now', 'localtime'))


### 2. Actualización en `main.py`[cite: 2]
#Incorporamos el esquema de validación `ProductoUpdateSchema` y el endpoint `PUT /productos/{codigo}` que actualiza los datos operativos/financieros y dispara el registro histórico de precios de forma automática.


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
    version="3.4.0"
)

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "ulises_pro_2026")

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
    total_likes: Optional[int] = 0

# <--- ¡ NUEVO ESQUEMA PARA ACTUALIZACIÓN PARCIAL DE PRENDA ! --->
class ProductoUpdateSchema(BaseModel):
    descripcion_original: Optional[str] = None
    precio_costo: Optional[float] = None
    precio_venta: Optional[float] = None
    precio_mayoreo: Optional[float] = None
    existencia: Optional[int] = None
    inventario_minimo: Optional[int] = None
    inventario_maximo: Optional[int] = None
    departamento: Optional[str] = None

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
        
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            file_path, 
            contents, 
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        
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
        historia = "[ESPAÑOL]\nPrenda deportiva de alta calidad Hecho en México.\n\n[ENGLISH]\nHigh-end sportswear proudly Made in Mexico."

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
        "imagenes": urls_a_guardar,
        "total_likes": nuevo_producto.total_likes
    }

# <--- ¡ NUEVO ENDPOINT PUT PARA ACTUALIZAR PRECIOS, INVENTARIO Y DESCRIPCIÓN CON HISTORIAL ! --->
@app.put("/productos/{codigo}")
def actualizar_producto(
    codigo: str,
    producto_update: ProductoUpdateSchema,
    db: Session = Depends(get_db),
    x_token: str = Header(None)
):
    if x_token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Acceso denegado: Token inválido, compa.")
    
    producto = db.query(models.ProductoDB).filter(models.ProductoDB.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail=f"El producto con código '{codigo}' no existe, compa.")
    
    pc_anterior = producto.precio_costo
    pv_anterior = producto.precio_venta
    
    update_data = producto_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(producto, key, value)
        
    # Registrar en historial si hay cambios en costos o precios de venta
    if (producto_update.precio_costo is not None and producto_update.precio_costo != pc_anterior) or \
       (producto_update.precio_venta is not None and producto_update.precio_venta != pv_anterior):
        historial = models.HistorialPrecioDB(
            codigo=codigo,
            precio_costo_anterior=pc_anterior,
            precio_costo_nuevo=producto.precio_costo,
            precio_venta_anterior=pv_anterior,
            precio_venta_nuevo=producto.precio_venta
        )
        db.add(historial)
        
    db.commit()
    db.refresh(producto)
    
    return {
        "mensaje": f"¡Producto con SKU {codigo} actualizado exitosamente!",
        "codigo": producto.codigo,
        "precio_venta": producto.precio_venta,
        "precio_costo": producto.precio_costo,
        "existencia": producto.existencia
    }

@app.post("/productos/{codigo}/like")
def dar_like_producto(codigo: str, db: Session = Depends(get_db)):
    producto = db.query(models.ProductoDB).filter(models.ProductoDB.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail=f"El producto con código '{codigo}' no existe, compa.")
    
    if producto.total_likes is None:
        producto.total_likes = 0
    producto.total_likes += 1
    
    db.commit()
    db.refresh(producto)
    
    return {
        "mensaje": "¡Like registrado con éxito!",
        "codigo": producto.codigo,
        "total_likes": producto.total_likes
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


### 3. Actualización en `app_frontend.py`[cite: 4]
#Añadimos la **Pestaña 5 ("✏️ Editar Precios e Inventario")** aplicando la **Opción 2**: buscas por SKU o descripción, se precargan los campos operativos y financieros que encerraste en tu imagen (costo, venta, mayoreo, existencias, límites e info)[cite: 1], y guardas los cambios de inmediato contra la API protegida por token.


import streamlit as st
import requests
import json
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

API_TOKEN = "ulises_pro_2026"
HEADERS = {"x-token": API_TOKEN}
BASE_URL_RENDER = "https://kinetik-on-line.onrender.com"
URL_FASTAPI_CREAR = f"{BASE_URL_RENDER}/crear-producto/"
URL_FASTAPI_LISTAR = f"{BASE_URL_RENDER}/productos/"
URL_FASTAPI_SUBIR_SUPABASE = f"{BASE_URL_RENDER}/subir-imagen-supabase/"

load_dotenv()
admin_password = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="Hecho en México - Admin 2026", page_icon="🇲🇽", layout="wide")

st.markdown("""
    <style>
    .card-precio {
        font-size: 26px;
        font-weight: bold;
        color: #2E7D32;
    }
    .badge-sku {
        background-color: #E0E0E0;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
        color: #333333;
    }
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        max-height: 550px !important;
        object-fit: contain !important;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c_login1, c_login2, c_login3 = st.columns([1, 2, 1])
    
    with c_login2:
        st.title("🔒 KINETIK Admin Panel")
        st.subheader("Acceso Restringido - Control de Inventarios")
        
        if not admin_password:
            st.error("🚨 Error del Sistema: La variable de entorno 'ADMIN_PASSWORD' está vacía o no configurada en Render.")
            st.stop()
            
        st.info("Ingresa la contraseña maestra para abrir la cabecera de control.")
        
        with st.form("form_login_maestro", clear_on_submit=False):
            password_input = st.text_input("Contraseña de Acceso:", type="password", placeholder="••••••••••••")
            btn_login = st.form_submit_button("🔑 Entrar al Sistema", use_container_width=True)
            
            if btn_login:
                pwd_ingresado = password_input.strip()
                if pwd_ingresado == admin_password:
                    st.session_state["autenticado"] = True
                    st.success("¡Acceso concedido! Entrando a la pista...")
                    st.rerun()
                else:
                    st.error("🚫 Contraseña incorrecta. Revisa tu clave de acceso y vuelve a intentar.")
                    
    st.stop()

MAPEO_GENERO = {'MUJER': '1', 'HOMBRE': '2', 'UNISEX': '3'}
MAPEO_TIPO_TELA = {
    'NAYLON': '1', 'LICRA': '2', 'TRIX': '3', 'PIQUE': '4', 'LASER': '5',
    'ALGODÓN': '6', 'ALGODON': '6', 'COMPOSICIÓN': '7', 'COMPOSICION': '7',
    'AFELPADO': '8', 'PANAL': '9', 'TIGRE': '10', 'FELPA': '11', 'FRESCO': '12'
}
MAPEO_PRENDA = {
    'LEGGIN': '1', 'LEGGIN PUSH SHOP': '2', 'CHAMARRA': '3', 'SUDADERA': '4',
    'PANS': '5', 'PLAYERA': '6', 'SHORT': '7', 'SHORT PUSH UP': '8',
    'PLAYERA TIRANTES': '9', 'GORRA': '10', 'VESTIDO': '11', 'FALDA': '12',
    'TOP TIRANTES': '13', 'TOP AJUSTABLE': '14', 'TOP': '15', 'FALDA SHORT': '16',
    'ROMPE VIENTOS': '17', 'MONO': '18', 'CAMISETA': '19', 'VARIADO': '20',
    'PLAYERA MANGA LARGA': '21', 'SHORT DOBLE CAPA': '22', 'BALON': '23',
    'JOGGER': '24', 'SHORT COLOMBIANO': '25', 'TRAJE DE BAÑO MANGA LARGA': '26',
    'TRAJE DE BAÑO TIRANTE': '27', 'PLAYERA CIERRE': '28', 'TOP Y SHORT': '29'
}
MAPEO_CORTE = {
    'OVER': '1', 'NORMAL': '2', 'FIT': '3', 'CORTO': '4', 'LARGO': '5',
    'CRUZADO': '6', 'TIRANTES': '7', 'ACAMPANADO': '8', 'YOGA': '9',
    'MAYA': '10', 'ESPALDA ABIERTA': '11', 'CIERRE': '12', 'EN V': '13',
    'ESPALDA CRUZADA': '14', 'YOGER': '15', 'VARIADO': '17'
}
MAPEO_PROVEEDOR = {
    'NOVARAS': '1', 'ARAPOS': '2', 'MERCADO LIBRE': '3', 'OTRO': '4',
    'BAMI': '5', 'VARIADO': '6', 'KINETIK': '7'
}
MAPEO_TALLA = {
    'XS': '1', 'S': '2', 'M': '3', 'G': '4', 'XG': '5', 'XXG': '6', 'UNITALLA': '7'
}
MAPEO_COLOR = {
    'NEGRO': '1', 'BLANCO': '2', 'ROJO': '3', 'VERDE': '4', 'GRIS': '5',
    'NARANJA': '6', 'CAMUFLAJE': '7', 'ROSA': '8', 'CAFÉ': '9', 'CAFE': '9',
    'AMARILLO': 'A', 'BEIGE': 'B', 'LILA': 'C', 'AZUL CLARO': 'D',
    'AZUL OSCURO': 'E', 'AZUL CIELO': 'F', 'AZUL REY': 'G', 'MARRON': 'H',
    'PURPURA': 'I', 'PISTACHE': 'J', 'ROSA MEX': 'K', 'VARIOS': 'L',
    'ROSA NEON': 'M', 'VINO': 'N', 'OXFOR': 'O', 'VERDE FLUORESCENTE': 'P', 'ROSA PALIDO': 'Q'
}

def generar_codigo_producto(genero, tipo_tela, prenda, corte, proveedor, talla, color) -> str:
    c_gen = MAPEO_GENERO.get(str(genero).strip().upper(), '0')
    c_tela = MAPEO_TIPO_TELA.get(str(tipo_tela).strip().upper(), '0')
    c_prenda = MAPEO_PRENDA.get(str(prenda).strip().upper(), '0')
    c_corte = MAPEO_CORTE.get(str(corte).strip().upper(), '0')
    c_prov = MAPEO_PROVEEDOR.get(str(proveedor).strip().upper(), '0')
    c_talla = MAPEO_TALLA.get(str(talla).strip().upper(), '0')
    c_color = MAPEO_COLOR.get(str(color).strip().upper(), '0')
    return f"{c_gen}{c_tela}{c_prenda}{c_corte}{c_prov}{c_talla}{c_color}"

def calcular_codigo_barras_pos(codigo_sku: str, prefijo_pais: str = "750") -> str:
    numeros_sku = "".join([char if char.isdigit() else str(ord(char) % 10) for char in str(codigo_sku)])
    cadena_base = f"{prefijo_pais}{numeros_sku}".zfill(12)[-12:]
    suma = sum(int(digit) * (3 if i % 2 == 0 else 1) for i, digit in enumerate(reversed(cadena_base)))
    digito_verificador = (10 - (suma % 10)) % 10
    return f"{cadena_base}{digito_verificador}"

def generar_imagen_barcode_memoria(codigo_barras_str: str, precio_venta: float = 0.0, titulo_prenda: str = "") -> BytesIO:
    EAN13 = barcode.get_barcode_class('ean13')
    base_12 = codigo_barras_str[:12] if len(codigo_barras_str) >= 12 else codigo_barras_str.zfill(12)
    buffer_bc = BytesIO()
    EAN13(base_12, writer=ImageWriter()).write(buffer_bc)
    buffer_bc.seek(0)
    
    img_bc = Image.open(buffer_bc)
    w_bc, h_bc = img_bc.size
    altura_encabezado = 110
    img_final = Image.new('RGB', (w_bc, h_bc + altura_encabezado), color=(255, 255, 255))
    draw = ImageDraw.Draw(img_final)
    
    try:
        font_precio = ImageFont.truetype("arial.ttf", 42)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        font_precio = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    texto_precio = f"${precio_venta:,.2f} MXN" if precio_venta > 0 else "HECHO EN MÉXICO"
    bbox_p = draw.textbbox((0, 0), texto_precio, font=font_precio)
    draw.text(((w_bc - (bbox_p[2] - bbox_p[0])) / 2, 15), texto_precio, fill=(0, 0, 0), font=font_precio)
    
    texto_sub = titulo_prenda[:28].upper() if titulo_prenda else "HECHO EN MÉXICO"
    bbox_s = draw.textbbox((0, 0), texto_sub, font=font_sub)
    draw.text(((w_bc - (bbox_s[2] - bbox_s[0])) / 2, 65), texto_sub, fill=(80, 80, 80), font=font_sub)
    
    img_final.paste(img_bc, (0, altura_encabezado))
    buffer_out = BytesIO()
    img_final.save(buffer_out, format="PNG")
    buffer_out.seek(0)
    return buffer_out

st.title("KINETIK Hecho en México - Panel de Control (Cloud Storage)")

with st.sidebar:
    st.markdown("### 👤 Sesión Activa")
    st.write(f"**Usuario:** Admin Pro")
    st.write(f"**Token Activo:** `...{admin_password[-3:]}`")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

# <--- 5 PESTAÑAS: INCLUYENDO EL NUEVO MÓDULO DE EDICIÓN (OPCIÓN 2) --->
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🥇️ KINETIK - Quienes somos", 
    "📝 Formulario Manual", 
    "📊 Inventario e Impresión",
    "🖼️ Galería y Fotos por SKU",
    "✏️ Editar Precios e Inventario"
])

with tab1:
    st.subheader(" Creamos ropa deportiva para personas que buscan comodidad en su día a día, con telas, costuras y diseños de calidad. Diseñada para sentirte cómodo y seguro realizando cualquier actividad; para sentirte libre de impulsar tus movimientos, generando una mejor versión de ti mismo. ")

with tab2:
    st.subheader("📝 Captura Directa de Inventario con Galería Cloud (Supabase Storage)")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        sel_genero = st.selectbox("Género", list(MAPEO_GENERO.keys()), index=0)
        sel_tipo_tela = st.selectbox("Tipo de Tela", [k for k in MAPEO_TIPO_TELA.keys() if k != 'ALGODON' and k != 'COMPOSICION'], index=0)
    with col_b:
        sel_prenda = st.selectbox("Prenda", list(MAPEO_PRENDA.keys()), index=0)
        sel_corte = st.selectbox("Corte", list(MAPEO_CORTE.keys()), index=0)
    with col_c:
        sel_proveedor = st.selectbox("Proveedor", list(MAPEO_PROVEEDOR.keys()), index=0)
        sel_talla = st.selectbox("Talla", list(MAPEO_TALLA.keys()), index=0)
    with col_d:
        sel_color = st.selectbox("Color", [k for k in MAPEO_COLOR.keys() if k != 'CAFE'], index=0)
        
        codigo_calculado = generar_codigo_producto(
            sel_genero, sel_tipo_tela, sel_prenda, sel_corte, sel_proveedor, sel_talla, sel_color
        )
        codigo_barras_calculado = calcular_codigo_barras_pos(codigo_calculado)

    st.divider()

    with st.form("form_manual_autocodigo"):
        st.markdown("#### 📦 Detalle del Producto, Precios y Galería Cloud")
        c1, c2 = st.columns(2)
        with c1:
            desc = st.text_input("Descripción Original", placeholder="Ej: LEGGIN FIT LICRA NEGRO TALLA S")
            p_costo = st.number_input("Precio Costo ($MXN)", min_value=0.0, step=5.0)
            p_venta = st.number_input("Precio Venta Público ($MXN)", min_value=0.0, step=5.0)
            p_may = st.number_input("Precio Mayoreo ($MXN)", min_value=0.0, step=5.0)
            t_likes = st.number_input("Total de Likes Iniciales", min_value=0, step=1, value=0)
        with c2:
            dep = st.text_input("Departamento / Sección", value=sel_genero, placeholder="Ej: HOMBRE / DEPORTES")
            exi = st.number_input("Existencia en Tienda", min_value=1, step=1, value=1)
            inv_min = st.number_input("Inventario Mínimo", min_value=0, value=5)
            inv_max = st.number_input("Inventario Máximo", min_value=0, value=50)
            
            fotos_subidas = st.file_uploader("📷 Subir Galería de Fotos a Supabase Storage (Múltiples JPG / PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        col_sku_disp, col_bar_disp, col_img_disp = st.columns([1, 1, 1])
        with col_sku_disp:
            st.text_input("🔑 SKU Autogenerado", value=codigo_calculado, disabled=True)
        with col_bar_disp:
            st.text_input("🏷️ Código EAN-13", value=codigo_barras_calculado, disabled=True)
        with col_img_disp:
            img_preview = generar_imagen_barcode_memoria(codigo_barras_calculado, float(p_venta), sel_prenda)
            st.image(img_preview, caption=f"Vista previa (${p_venta:.2f} MXN)", width=200)

        boton_manual = st.form_submit_button("🚀 Guardar Producto y Subir Fotos a la Nube")
        
        if boton_manual:
            if desc:
                rutas_supabase = []
                if fotos_subidas:
                    with st.spinner("Subiendo archivos fotográficos directo al bucket de Supabase Storage..."):
                        for foto in fotos_subidas:
                            files = {"file": (foto.name, foto.getvalue(), foto.type)}
                            try:
                                r_subida = requests.post(
                                    f"{URL_FASTAPI_SUBIR_SUPABASE}?codigo={codigo_calculado}",
                                    files=files,
                                    headers=HEADERS
                                )
                                if r_subida.status_code == 200:
                                    url_publica = r_subida.json().get("imagen_url")
                                    if url_publica:
                                        rutas_supabase.append(url_publica)
                                else:
                                    st.warning(f"⚠️ No se pudo subir {foto.name}: {r_subida.text}")
                            except Exception as err_sub:
                                st.error(f"Error de red al subir imagen: {err_sub}")

                payload = {
                    "codigo": codigo_calculado,
                    "codigo_barras": codigo_barras_calculado,
                    "prenda": sel_prenda.upper(),
                    "descripcion_original": desc,
                    "precio_costo": float(p_costo),
                    "precio_venta": float(p_venta),
                    "color": sel_color.upper(),
                    "precio_mayoreo": float(p_may),
                    "departamento": dep.upper() if dep else sel_genero.upper(),
                    "existencia": int(exi),
                    "inventario_minimo": int(inv_min),
                    "inventario_maximo": int(inv_max),
                    "genero": sel_genero.upper(),
                    "tipo_tela": sel_tipo_tela.upper(),
                    "corte": sel_corte.upper(),
                    "proveedor": sel_proveedor.upper(),
                    "talla": sel_talla.upper(),
                    "total_likes": int(t_likes),
                    "imagen_url": rutas_supabase[0] if rutas_supabase else None,
                    "imagenes": rutas_supabase
                }
                
                try:
                    r = requests.post(URL_FASTAPI_CREAR, json=payload, headers=HEADERS)
                    if r.status_code == 200:
                        resultado = r.json()
                        st.session_state["exito_guardado"] = True
                        st.session_state["sku_reciente"] = codigo_calculado
                        st.session_state["precio_reciente"] = float(p_venta)
                        st.session_state["prenda_reciente"] = sel_prenda
                        st.session_state["barcode_reciente"] = codigo_barras_calculado
                        st.session_state["historia_reciente"] = resultado.get("historia", "")
                        st.session_state["rutas_imgs_recientes"] = rutas_supabase
                        st.session_state["error_guardado"] = None
                    elif r.status_code == 400:
                        st.session_state["exito_guardado"] = False
                        st.session_state["error_guardado"] = r.json().get('detail', 'El producto ya existe.')
                    elif r.status_code == 403:
                        st.session_state["exito_guardado"] = False
                        st.session_state["error_guardado"] = "Acceso denegado: Token de seguridad inválido."
                    else:
                        st.session_state["exito_guardado"] = False
                        st.session_state["error_guardado"] = f"Error {r.status_code}: {r.text}"
                except Exception as e:
                    st.session_state["exito_guardado"] = False
                    st.session_state["error_guardado"] = f"No se pudo conectar con el API: {e}"
            else:
                st.session_state["exito_guardado"] = False
                st.session_state["error_guardado"] = "Por favor proporciona la Descripción Original del producto."

    if st.session_state.get("error_guardado"):
        st.warning(st.session_state["error_guardado"])
        st.session_state["error_guardado"] = None

    if st.session_state.get("exito_guardado"):
        st.balloons()
        sku_c = st.session_state["sku_reciente"]
        precio_c = st.session_state["precio_reciente"]
        prenda_c = st.session_state["prenda_reciente"]
        bc_c = st.session_state["barcode_reciente"]
        
        st.success(f"✅ ¡Producto [{sku_c}] guardado exitosamente con su galería en Supabase Storage!")
        img_final = generar_imagen_barcode_memoria(bc_c, precio_c, prenda_c)
        st.download_button(
            label="🖨️ Imprimir / Descargar Etiqueta Final (con Precio)",
            data=img_final,
            file_name=f"etiqueta_{sku_c}.png",
            mime="image/png"
        )
        st.markdown("### 📖 Storytelling Generado:")
        st.write(st.session_state.get("historia_reciente", ""))

with tab3:
    st.subheader("📊 Inventario, Búsqueda y Galería de Precios")
    try:
        res = requests.get(URL_FASTAPI_LISTAR)
        if res.status_code == 200:
            datos = res.json()
            if datos:
                df = pd.DataFrame(datos)
                
                if 'total_likes' in df.columns:
                    cols = list(df.columns)
                    if 'existencia' in cols:
                        idx_exi = cols.index('existencia')
                        cols.insert(idx_exi, cols.pop(cols.index('total_likes')))
                        df = df[cols]
                
                st.markdown("### 🔍 Buscador Inteligente de Prendas")
                c_busq1, c_busq2 = st.columns([2, 1])
                with c_busq1:
                    query_busqueda = st.text_input("Ingresa el código SKU exacto o fragmento a buscar:", placeholder="Ej. 3641741 o SUDADERA", key="search_tab3")
                with c_busq2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_limpiar = st.button("🔄 Ver Todo el Inventario", key="btn_clear_tab3")

                df_filtrado = df.copy()
                if query_busqueda:
                    df_filtrado = df_filtrado[
                        df_filtrado['codigo'].astype(str).str.contains(query_busqueda, case=False, na=False) |
                        df_filtrado['descripcion_original'].astype(str).str.contains(query_busqueda, case=False, na=False) |
                        df_filtrado['prenda'].astype(str).str.contains(query_busqueda, case=False, na=False)
                    ]
                    st.info(f"Se encontraron **{len(df_filtrado)}** coincidencias para: *{query_busqueda}*")

                st.dataframe(df_filtrado, use_container_width=True)
                
                csv_data = df_filtrado.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Descargar Inventario Filtrado en CSV",
                    data=csv_data,
                    file_name="inventario_filtrado_hecho_en_mexico.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("Aún no hay productos registrados.")
    except Exception as e:
        st.error(f"Error al conectar con el API: {e}")

with tab4:
    st.subheader("🖼️ Galería Visual Cloud y Edición Fotográfica por SKU")
    st.markdown("Utiliza este módulo para consultar las URLs públicas de Supabase Storage asociadas a cualquier prenda o añadir/reemplazar fotos.")
    
    sku_a_editar = st.text_input("Ingresa el código SKU exacto a actualizar:", placeholder="Ej. 3641741", key="input_sku_edit")
    
    if sku_a_editar:
        try:
            res_info = requests.get(URL_FASTAPI_LISTAR)
            if res_info.status_code == 200:
                prods = res_info.json()
                prod_encontrado = next((p for p in prods if str(p["codigo"]).strip() == str(sku_a_editar).strip()), None)
                
                if prod_encontrado:
                    st.success(f"✅ Prenda Encontrada: **{prod_encontrado.get('prenda')}** - {prod_encontrado.get('descripcion_original')}")
                    fotos_actuales = prod_encontrado.get('imagenes', [])
                    if fotos_actuales:
                        st.markdown(f"##### 📷 Galería fotográfica activa en la nube ({len(fotos_actuales)} fotos):")
                        cols_f = st.columns(min(len(fotos_actuales), 5))
                        for idx, f_url in enumerate(fotos_actuales):
                            with cols_f[idx % 5]:
                                st.image(f_url, caption=f"Foto {idx+1}", use_container_width=True)
                    else:
                        st.info("ℹ️ Este producto no cuenta con fotos registradas en su galería actualmente.")
                else:
                    st.warning(f"⚠️ No se encontró ninguna prenda registrada con el SKU '{sku_a_editar}'.")
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# ==============================================================================
# ✏️ PESTAÑA 5: MÓDULO DE EDICIÓN RÁPIDA DE PRECIOS E INVENTARIO (OPCIÓN 2)
# ==============================================================================
with tab5:
    st.subheader("✏️ Actualización Rápida de Precios, Costos y Existencias por SKU")
    st.markdown("Busca el producto por su código SKU[cite: 1] para actualizar sus valores financieros y de stock en tiempo real de forma limpia y segura.")
    
    sku_busqueda_edit = st.text_input("🔍 Ingresa el código SKU o escanea el código de barras:", placeholder="Ej. 3641741", key="sku_busqueda_actualizacion")
    
    if sku_busqueda_edit:
        try:
            resp_prod = requests.get(URL_FASTAPI_LISTAR)
            if resp_prod.status_code == 200:
                lista_prods = resp_prod.json()
                item_encontrado = next((p for p in lista_prods if str(p["codigo"]).strip() == str(sku_busqueda_edit).strip()), None)
                
                if item_encontrado:
                    st.success(f"🎯 Producto localizado: **[{item_encontrado.get('codigo')}] {item_encontrado.get('prenda')}** - {item_encontrado.get('color')}")
                    
                    # Formulario precargado con los datos actuales del producto (basado en el recuadro rojo de tu imagen)[cite: 1]
                    with st.form("form_actualizacion_precios_stock"):
                        st.markdown("#### 📦 Modificar Datos de Inventario y Precios")
                        
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            nuevo_desc = st.text_input("Descripción Original", value=item_encontrado.get('descripcion_original', ''))
                            nuevo_p_costo = st.number_input("Precio Costo ($MXN)", min_value=0.0, step=1.0, value=float(item_encontrado.get('precio_costo', 0.0)))
                            nuevo_p_venta = st.number_input("Precio Venta Público ($MXN)", min_value=0.0, step=1.0, value=float(item_encontrado.get('precio_venta', 0.0)))
                            nuevo_p_mayoreo = st.number_input("Precio Mayoreo ($MXN)", min_value=0.0, step=1.0, value=float(item_encontrado.get('precio_mayoreo', 0.0)))
                        with col_e2:
                            nuevo_dep = st.text_input("Departamento / Sección", value=item_encontrado.get('departamento', 'GENERAL'))
                            nueva_existencia = st.number_input("Existencia en Tienda", min_value=0, step=1, value=int(item_encontrado.get('existencia', 0)))
                            nuevo_inv_min = st.number_input("Inventario Mínimo", min_value=0, step=1, value=int(item_encontrado.get('inventario_minimo', 0)))
                            nuevo_inv_max = st.number_input("Inventario Máximo", min_value=0, step=1, value=int(item_encontrado.get('inventario_maximo', 0)))
                        
                        st.info("ℹ️ Nota: Los identificadores estructurales (SKU y Código EAN-13) están bloqueados para proteger la integridad histórica de tus reportes y análisis de ventas[cite: 1].")
                        
                        btn_guardar_cambios = st.form_submit_button("💾 Guardar Actualización de Precios y Stock", use_container_width=True)
                        
                        if btn_guardar_cambios:
                            payload_actualizacion = {
                                "descripcion_original": nuevo_desc,
                                "precio_costo": float(nuevo_p_costo),
                                "precio_venta": float(nuevo_p_venta),
                                "precio_mayoreo": float(nuevo_p_mayoreo),
                                "existencia": int(nueva_existencia),
                                "inventario_minimo": int(nuevo_inv_min),
                                "inventario_maximo": int(nuevo_inv_max),
                                "departamento": nuevo_dep.upper()
                            }
                            
                            url_put = f"{BASE_URL_RENDER}/productos/{sku_busqueda_edit}"
                            r_put = requests.put(url_put, json=payload_actualizacion, headers=HEADERS)
                            
                            if r_put.status_code == 200:
                                st.balloons()
                                st.success(f"🎉 ¡Precios y stock del SKU [{sku_busqueda_edit}] actualizados correctamente en el sistema!")
                                st.rerun()
                            else:
                                st.error(f"Error {r_put.status_code}: {r_put.text}")
                else:
                    st.warning(f"⚠️ No se encontró ningún producto con el SKU '{sku_busqueda_edit}'. Verifica el código.")
        except Exception as err_act:
            st.error(f"Error al conectar con la API de actualización: {err_act}")