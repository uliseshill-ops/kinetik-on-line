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

# Estilos CSS comerciales de alta gama
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

if "likes" not in st.session_state:
    st.session_state.likes = {}

def construir_url_imagen(ruta_raw: str) -> str:
    """Convierte una ruta local o limpia en una URL remota válida en Render."""
    if not ruta_raw or str(ruta_raw).strip().lower() in ["nan", "none", ""]:
        return PLACEHOLDER_OFICIAL
    
    clean_path = str(ruta_raw).strip().replace("\\", "/")
    if clean_path.startswith("http"):
        return clean_path
    
    return f"{URL_BASE_RENDER}/{clean_path.lstrip('/')}"

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

            st.caption(f"Mostrando {len(df_filtrado)} prendas disponibles en catálogo")
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
                        # --- GALERÍA FOTOGRÁFICA (BLINDADA AL 100%) ---
                        if lista_imagenes_limpia:
                            if len(lista_imagenes_limpia) > 1:
                                nombres_pestanas = [f"Foto {i+1}" for i in range(len(lista_imagenes_limpia))]
                                tabs_fotos = st.tabs(nombres_pestanas)
                                for t_idx, tab_obj in enumerate(tabs_fotos):
                                    with tab_obj:
                                        img_url = construir_url_imagen(lista_imagenes_limpia[t_idx])
                                        try:
                                            st.image(img_url, use_container_width=True)
                                        except Exception:
                                            st.image(PLACEHOLDER_OFICIAL, use_container_width=True)
                            else:
                                img_url = construir_url_imagen(lista_imagenes_limpia[0])
                                try:
                                    st.image(img_url, use_container_width=True)
                                except Exception:
                                    st.image(PLACEHOLDER_OFICIAL, use_container_width=True)
                        else:
                            st.image(PLACEHOLDER_OFICIAL, use_container_width=True)
                        
                        st.subheader(f"👕 {prenda_nombre}")
                        st.markdown(f"**{desc_orig}**")
                        st.markdown(f"Color: **{color_p}** | SKU: <span class='badge-sku'>{codigo_sku}</span>", unsafe_allow_html=True)
                        st.markdown(f"<p class='card-precio'>${precio_v:,.2f} MXN</p>", unsafe_allow_html=True)
                        
                        with st.expander("📖 Storytelling de la Prenda"):
                            st.write(historia)
                        
                        num_likes = st.session_state.likes.get(codigo_sku, 0)
                        btn_like = st.button(f"❤️ Me Gusta ({num_likes})", key=f"like_{codigo_sku}_{idx}")
                        
                        if btn_like:
                            st.session_state.likes[codigo_sku] = num_likes + 1
                            st.rerun()

                        if st.session_state.likes.get(codigo_sku, 0) > 0:
                            st.success("🔥 ¡Excelente elección, compa!")
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


---

### 🚀 ¿Cómo la probamos de volada, carnal?

1. Guarda el código arriba como `app_tienda_publica.py`[cite: 11].
2. Ejecuta en tu terminal:
   ```powershell
   streamlit run app_tienda_publica.py