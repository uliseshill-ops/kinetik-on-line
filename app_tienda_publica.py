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
PLACEHOLDER_OFICIAL = "https://via.placeholder.com/400x300/1A1D24/CCFF00.png?text=KINETIK+Hecho+en+M%C3%A9xico"

st.set_page_config(page_title="Hecho en México - KINETIK Tienda Oficial", page_icon="⚡", layout="wide")

# --- ESTILOS CSS: KINETIK DARK MODE + VERDE VOLT NEÓN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Montserrat:ital,wght@0,700;0,800;1,800&display=swap');

    /* Fondo principal Dark Mode Deportivo */
    .stApp {
        background-color: #0F1115;
        color: #F4F6F8;
        font-family: 'Inter', sans-serif;
    }

    /* Tipografía de títulos con fuerza deportiva */
    h1, h2, h3, .kinetik-title {
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 0.5px;
    }

    /* --- CORRECCIÓN DE ETIQUETAS DE INPUTS (SELECTBOX Y TEXT_INPUT) --- */
    /* Las ponemos en verde volt discreto, sin negritas, para perfecta visibilidad */
    [data-testid="stWidgetLabel"] p, label, .stTextInput label, .stSelectbox label {
        color: #B8FF33 !important;
        font-weight: 400 !important;
        font-size: 0.95rem !important;
    }

    /* Banner Hero Superior */
    .kinetik-hero {
        background: linear-gradient(135deg, #161920 0%, #0F1115 100%);
        border-left: 6px solid #CCFF00;
        border-top: 1px solid #2A2E39;
        border-right: 1px solid #2A2E39;
        border-bottom: 1px solid #2A2E39;
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .kinetik-hero h1 {
        color: #FFFFFF;
        font-weight: 800;
        font-style: italic;
        margin: 0;
        font-size: 2.2rem;
    }
    .kinetik-hero span {
        color: #CCFF00;
    }
    .kinetik-hero p {
        color: #A0AAB2;
        margin: 8px 0 0 0;
        font-size: 1.05rem;
    }

    /* Tarjetas de Producto (Containers con borde) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1A1D24 !important;
        border: 1px solid #2A2E39 !important;
        border-radius: 12px !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #CCFF00 !important;
        box-shadow: 0 6px 20px rgba(204, 255, 0, 0.12) !important;
        transform: translateY(-2px);
    }

    /* Precios y Badges */
    .card-precio {
        font-family: 'Montserrat', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #CCFF00;
        margin: 6px 0 12px 0;
        text-shadow: 0 0 12px rgba(204, 255, 0, 0.25);
    }
    .card-precio-agotado {
        font-family: 'Montserrat', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: #6C757D;
        text-decoration: line-through;
        margin: 6px 0 12px 0;
    }
    .badge-sku {
        background-color: #262A34;
        border: 1px solid #3A3F4B;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        color: #CCFF00;
        letter-spacing: 0.5px;
    }

    /* --- VISTA COMPLETA SIN RECORTES (OBJECT-FIT: CONTAIN) --- */
    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        max-height: 750px !important; 
        object-fit: contain !important;
        border-radius: 8px;
        background-color: #12141A; 
    }

    /* --- ESTILOS PARA PRENDAS AGOTADAS (STOCK = 0) --- */
    .contenedor-imagen-tienda {
        position: relative;
        display: inline-block;
        width: 100%;
    }
    .prenda-agotada {
        filter: grayscale(100%) opacity(45%);
        width: 100%;
        height: auto;
        max-height: 750px;
        object-fit: contain;
        border-radius: 8px;
        background-color: #12141A;
    }
    .badge-agotado {
        position: absolute;
        top: 12px;
        left: 12px;
        background-color: #FF2A55;
        color: white;
        padding: 6px 12px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        border-radius: 6px;
        font-size: 12px;
        letter-spacing: 0.8px;
        z-index: 10;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }

    /* Botones estándar de Streamlit (Likes / Entrar) */
    .stButton > button {
        background-color: #252932 !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3F4B !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        border-color: #CCFF00 !important;
        color: #CCFF00 !important;
        background-color: #1E222A !important;
    }

    /* Botón de Compra Directa WhatsApp (Verde Volt de Alto Contraste) */
    [data-testid="stLinkButton"] > a {
        background-color: #CCFF00 !important;
        color: #0F1115 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 14px rgba(204, 255, 0, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stLinkButton"] > a:hover {
        background-color: #D9FF33 !important;
        transform: scale(1.01);
        box-shadow: 0 6px 20px rgba(204, 255, 0, 0.5) !important;
    }

    /* Pestañas de fotos (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #A0AAB2;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #CCFF00 !important;
        border-bottom-color: #CCFF00 !important;
    }

    /* Inputs y Selectbox en modo oscuro */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1A1D24 !important;
        color: #FFFFFF !important;
        border-color: #2A2E39 !important;
    }
    .stTextInput input::placeholder {
        color: #6C757D !important;
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
            st.markdown("""
                <div class="kinetik-hero">
                    <h1>⚡ KINETIK <span>ACCESS</span></h1>
                    <p>Catálogo Privado — Ropa Deportiva Hecho en México</p>
                </div>
            """, unsafe_allow_html=True)
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

# --- INTERFAZ COMERCIAL DE LA TIENDA PÚBLICA (HERO BANNER) ---
st.markdown("""
    <div class="kinetik-hero">
        <h1>⚡ KINETIK <span>IMPULSA CADA MOVIMIENTO</span></h1>
        <p>Colección Oficial — Ropa deportiva de alto rendimiento. ¡Ingeniería textil 100% Mexicana! 🇲🇽</p>
    </div>
""", unsafe_allow_html=True)

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
                <div class="badge-agotado">AGOTADO</div>
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

            st.caption(f"⚡ Mostrando {len(df_filtrado)} prendas en catálogo")
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
                
                # Obtenemos los likes directamente de la base de datos
                num_likes = int(row.get('total_likes', 0)) if pd.notnull(row.get('total_likes')) else 0
                
                # Extracción robusta de imágenes
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

                lista_imagenes_limpia = [
                    img for img in lista_imagenes 
                    if str(img).strip() and str(img).strip().lower() not in ["nan", "none"]
                ]

                with cols[idx % 3]:
                    with st.container(border=True):
                        # --- GALERÍA FOTOGRÁFICA ---
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
                            st.subheader(f"{prenda_nombre} (AGOTADO)")
                            st.markdown(f"<span style='color:#A0AAB2;'>{desc_orig}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#A0AAB2;'>Color: **{color_p}** | SKU:</span> <span class='badge-sku'>{codigo_sku}</span>", unsafe_allow_html=True)
                            st.markdown(f"<p class='card-precio-agotado'>${precio_v:,.2f} MXN</p>", unsafe_allow_html=True)
                        else:
                            st.subheader(f"{prenda_nombre}")
                            st.markdown(f"<span style='color:#D0D7DE;'>{desc_orig}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#A0AAB2;'>Color: **{color_p}** | SKU:</span> <span class='badge-sku'>{codigo_sku}</span>", unsafe_allow_html=True)
                            st.markdown(f"<p class='card-precio'>${precio_v:,.2f} MXN</p>", unsafe_allow_html=True)
                        
                        with st.expander("📖 Detalles y Tecnología Textil"):
                            st.write(historia)
                        
                        # --- BOTÓN DE LIKE CONECTADO AL BACKEND ---
                        btn_like = st.button(f"❤️ Me Gusta ({num_likes})", key=f"like_{codigo_sku}_{idx}", use_container_width=True)
                        
                        if btn_like:
                            try:
                                url_like = f"{URL_BASE_RENDER}/productos/{codigo_sku}/like"
                                response_like = requests.post(url_like)
                                
                                if response_like.status_code == 200:
                                    st.toast("🔥 ¡Like registrado en KINETIK!")
                                    st.rerun()
                                else:
                                    st.error(f"⚠️ No se pudo registrar el like: {response_like.text}")
                            except Exception as err_like:
                                st.error(f"Error de conexión al dar like: {err_like}")

                        # --- ACCIÓN DE COMPRA / ESTADO DE STOCK ---
                        if esta_agotado:
                            st.warning("⚠️ Temporalmente agotado. Dale ❤️ Me Gusta para priorizar su reabastecimiento.")
                        else:
                            if num_likes > 0:
                                st.caption(f"🔥 ¡Alta demanda! {num_likes} personas ya la tienen en la mira.")
                            
                            mensaje_wa = f"¡Hola KINETIK! Me interesa la prenda SKU: {codigo_sku} ({desc_orig}) en color {color_p} con precio de ${precio_v:.2f} MXN. ¿Me apoyas con mi pedido?"
                            url_wa = f"https://wa.me/{NUMERO_VENTAS_WHATSAPP}?text={quote(mensaje_wa)}"
                            st.link_button("⚡ Pedir por WhatsApp", url_wa, use_container_width=True)
                            
        else:
            st.info("Aún no hay prendas registradas en el catálogo público.")
    else:
        st.error(f"Error al conectar con el servidor backend: Status {res.status_code}")
except Exception as e:
    st.error(f"No se pudo cargar la tienda online: {e}")