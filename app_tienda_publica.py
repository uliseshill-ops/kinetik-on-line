import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote
import ast
import os

# --- CONFIGURACIÓN DE SEGURIDAD Y ACCESO ---
CONTRASEÑA_ACCESO = "HechoEnMexico2026"  # Clave de acceso privado
NUMERO_VENTAS_WHATSAPP = "5215659113579"  # Tu WhatsApp comercial de ventas

# URL oficial de la Ferrari en la nube (Render)
URL_FASTAPI_PRODUCTOS = "https://kinetik-on-line.onrender.com/productos/"
URL_BASE_RENDER = "https://kinetik-on-line.onrender.com"
PLACEHOLDER_OFICIAL = "https://via.placeholder.com/400x300/2E7D32/FFFFFF.png?text=KINETIK+Hecho+en+M%C3%A9xico"

st.set_page_config(page_title="Hecho en México - KINETIK Tienda Oficial", page_icon="🇲🇽", layout="wide")

# Estilos CSS comerciales de alta gama + Normalización de tamaño de fotos + Estado Agotado
st.markdown("""
    <style>
    .card-precio {
        font-size: 26px;
        font-weight: bold;
        color: #2E7D32;
    }
    .card-precio-agotado {
        font-size: 24px;
        font-weight: bold;
        color: #757575;
        text-decoration: line-through;
    }
    .badge-sku {
        background-color: #E0E0E0;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
        color: #333333;
    }
    
    /* --- VISTA COMPLETA SIN RECORTES (OBJECT-FIT: CONTAIN) --- */
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        max-height: 750px !important; 
        object-fit: contain !important; /* <--- Esto evita que la foto se recorte en fullscreen */
        border-radius: 8px;
        background-color: #f9f9f9; 
    }

    /* --- ESTILOS PARA PRENDAS AGOTADAS (STOCK = 0) --- */
    .contenedor-imagen-tienda {
        position: relative;
        display: inline-block;
        width: 100%;
    }
    .prenda-agotada {
        filter: grayscale(100%) opacity(55%);
        width: 100%;
        height: auto;
        max-height: 750px;
        object-fit: contain;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .badge-agotado {
        position: absolute;
        top: 12px;
        left: 12px;
        background-color: #D32F2F;
        color: white;
        padding: 6px 12px;
        font-weight: bold;
        border-radius: 6px;
        font-size: 13px;
        z-index: 10;
        box-shadow: 0 2px 5px rgba(0,0,0,0.25);
    }
    </style>
""", unsafe_allow_html=True)

# --- MÓDULO DE AUTENTICACIÓN / CANDADO DE SEGURIDAD ---
def verificar_contraseña():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col_pad1, col_form, col_pad2 = st.columns([1, 2, 1])
        with col_form:
            st.markdown("### 🔒 Acceso Restringido — Hecho en México - KINETIK")
            st.info("Esta es una versión de prueba privada. Por favor ingresa la clave de acceso.")
            pwd_input = st.text_input("Contraseña de Acceso:", type="password", key="pwd_acceso")
            btn_ingresar = st.button("🔑 Entrar a la Tienda", use_container_width=True)
            
            if btn_ingresar:
                if pwd_input == CONTRASEÑA_ACCESO:
                    st.session_state["autenticado"] = True
                    st.success("¡Acceso concedido, compa!")
                    st.rerun()
                else:
                    st.error("🚫 Contraseña incorrecta. Pídesela al admin Ulises.")
        return False
    return True

# Validar clave antes de ejecutar cualquier consulta o cargar la interfaz
if not verificar_contraseña():
    st.stop()

# --- INTERFAZ COMERCIAL DE LA TIENDA PÚBLICA ---
st.title("KINETIK Hecho en México - Colección Oficial")
st.markdown("#### *Ropa y moda textil de alta resistencia. ¡Calidad 100% Mexicana!*")
st.divider()

def construir_url_imagen(ruta_raw: str) -> str:
    """Convierte una ruta local o limpia en una URL remota válida en Render."""
    if not ruta_raw or str(ruta_raw).strip().lower() in ["nan", "none", ""]:
        return PLACEHOLDER_OFICIAL
    
    clean_path = str(ruta_raw).strip().replace("\\", "/")
    if clean_path.startswith("http"):
        return clean_path
    
    return f"{URL_BASE_RENDER}/{clean_path.lstrip('/')}"

def renderizar_imagen_catalogo(url_img: str, agotado: bool):
    """Renderiza la imagen normal o en escala de grises con sello si el inventario es 0."""
    if agotado:
        st.markdown(f"""
            <div class="contenedor-imagen-tienda">
                <div class="badge-agotado">🔴 AGOTADO</div>
                <img src="{url_img}" class="prenda-agotada" onerror="this.src='{PLACEHOLDER_OFICIAL}';">
            </div>
        """, unsafe_allow_html=True)
    else:
        try:
            st.image(url_img, use_container_width=True)
        except Exception:
            st.image(PLACEHOLDER_OFICIAL, use_container_width=True)

try:
    res = requests.get(URL_FASTAPI_PRODUCTOS)
    if res.status_code == 200:
        productos = res.json()
        
        if productos:
            df = pd.DataFrame(productos)
            
            # --- FILTROS RÁPIDOS EN TIENDA ---
            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                deptos = ["TODOS"] + sorted(list(df['departamento'].dropna().unique())) if 'departamento' in df.columns else ["TODOS"]
                sel_depto = st.selectbox("🏷️ Departamento", deptos)
            with col_f2:
                buscar = st.text_input("🔍 Buscar prenda, color o código", placeholder="Ej: LEGGIN, TRIX, NEGRO...")

            # Aplicar Filtros comerciales
            df_filtrado = df.copy()
            if sel_depto != "TODOS":
                df_filtrado = df_filtrado[df_filtrado['departamento'] == sel_depto]
            if buscar:
                df_filtrado = df_filtrado[
                    df_filtrado['descripcion_original'].astype(str).str.contains(buscar, case=False, na=False) |
                    df_filtrado['codigo'].astype(str).str.contains(buscar, case=False, na=False)
                ]

            st.caption(f"Mostrando {len(df_filtrado)} prendas en catálogo")
            st.divider()

            # --- ESCAPARATE DE PRODUCTOS EN CUADRÍCULA (3 COLUMNAS) ---
            cols = st.columns(3)
            
            for idx, row in df_filtrado.reset_index(drop=True).iterrows():
                codigo_sku = str(row.get('codigo', 'SKU'))
                prenda_nombre = str(row.get('prenda', 'PRENDA')).upper()
                desc_orig = str(row.get('descripcion_original', 'Prenda Hecho en México'))
                precio_v = float(row.get('precio_venta', 0.0))
                color_p = str(row.get('color', 'N/A'))
                historia = str(row.get('historia_ia', 'Calidad textil garantizada.'))
                
                # Validación de existencia en inventario
                existencia_actual = int(row.get('existencia', 0)) if pd.notnull(row.get('existencia')) else 0
                esta_agotado = existencia_actual <= 0
                
                # Obtenemos los likes directamente de la base de datos (con fallback al esquema)
                num_likes = int(row.get('total_likes', 0)) if pd.notnull(row.get('total_likes')) else 0
                
                # Extracción robusta de imágenes (Manejo de string lista de Python desde CSV)
                raw_imgs = row.get('imagenes', [])
                lista_imagenes = []
                
                if isinstance(raw_imgs, str):
                    try:
                        parsed = ast.literal_eval(raw_imgs)
                        if isinstance(parsed, list):
                            lista_imagenes = parsed
                        else:
                            lista_imagenes = [raw_imgs]
                    except Exception:
                        lista_imagenes = [raw_imgs] if raw_imgs else []
                elif isinstance(raw_imgs, list):
                    lista_imagenes = raw_imgs
                
                if not lista_imagenes and row.get('imagen_url'):
                    lista_imagenes = [row.get('imagen_url')]

                # Filtrar valores nulos reales
                lista_imagenes_limpia = [
                    img for img in lista_imagenes 
                    if str(img).strip() and str(img).strip().lower() not in ["nan", "none"]
                ]

                with cols[idx % 3]:
                    with st.container(border=True):
                        # --- GALERÍA FOTOGRÁFICA (BLINDADA, ESTANDARIZADA Y CON ESTADO AGOTADO) ---
                        if lista_imagenes_limpia:
                            if len(lista_imagenes_limpia) > 1:
                                nombres_pestanas = [f"Foto {i+1}" for i in range(len(lista_imagenes_limpia))]
                                tabs_fotos = st.tabs(nombres_pestanas)
                                for t_idx, tab_obj in enumerate(tabs_fotos):
                                    with tab_obj:
                                        img_url = construir_url_imagen(lista_imagenes_limpia[t_idx])
                                        renderizar_imagen_catalogo(img_url, esta_agotado)
                            else:
                                img_url = construir_url_imagen(lista_imagenes_limpia[0])
                                renderizar_imagen_catalogo(img_url, esta_agotado)
                        else:
                            renderizar_imagen_catalogo(PLACEHOLDER_OFICIAL, esta_agotado)
                        
                        if esta_agotado:
                            st.subheader(f"👕 {prenda_nombre} (AGOTADO)")
                            st.markdown(f"**{desc_orig}**")
                            st.markdown(f"Color: **{color_p}** | SKU: <span class='badge-sku'>{codigo_sku}</span>", unsafe_allow_html=True)
                            st.markdown(f"<p class='card-precio-agotado'>${precio_v:,.2f} MXN</p>", unsafe_allow_html=True)
                        else:
                            st.subheader(f"👕 {prenda_nombre}")
                            st.markdown(f"**{desc_orig}**")
                            st.markdown(f"Color: **{color_p}** | SKU: <span class='badge-sku'>{codigo_sku}</span>", unsafe_allow_html=True)
                            st.markdown(f"<p class='card-precio'>${precio_v:,.2f} MXN</p>", unsafe_allow_html=True)
                        
                        with st.expander("📖 Storytelling de la Prenda"):
                            st.write(historia)
                        
                        # --- BOTÓN DE LIKE CONECTADO AL BACKEND (ACTIVO INCLUSO SI ESTÁ AGOTADO PARA MEDIR DEMANDA) ---
                        btn_like = st.button(f"❤️ Me Gusta ({num_likes})", key=f"like_{codigo_sku}_{idx}")
                        
                        if btn_like:
                            try:
                                url_like = f"{URL_BASE_RENDER}/productos/{codigo_sku}/like"
                                response_like = requests.post(url_like)
                                
                                if response_like.status_code == 200:
                                    st.success("🔥 ¡Like registrado en la base de datos, compa!")
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ No se pudo registrar el like: {response_like.text}")
                            except Exception as err_like:
                                st.error(f"Error de conexión al dar like: {err_like}")

                        # Si hay existencia y likes acumulados, mostramos botón de WhatsApp
                        if esta_agotado:
                            st.warning("⚠️ Prenda temporalmente agotada. Dale ❤️ Me Gusta para avisarnos que la quieres de vuelta.")
                        elif num_likes > 0:
                            st.success("🔥 ¡Prenda con alta demanda en la tienda!")
                            mensaje_wa = f"¡Hola! Me gustó mucho la prenda SKU: {codigo_sku} ({desc_orig}) con precio de ${precio_v:.2f} MXN. Quisiera ponerme en contacto con ventas para realizar mi compra."
                            url_wa = f"https://wa.me/{NUMERO_VENTAS_WHATSAPP}?text={quote(mensaje_wa)}"
                            
                            st.markdown(f"📞 **Atención a Ventas:** `{NUMERO_VENTAS_WHATSAPP}`")
                            st.link_button("📲 Contactar por WhatsApp de Ventas", url_wa, use_container_width=True)
                            
        else:
            st.info("Aún no hay prendas registradas en el catálogo público.")
    else:
        st.error(f"Error al conectar con el servidor backend: Status {res.status_code}")
except Exception as e:
    st.error(f"No se pudo cargar la tienda online: {e}")