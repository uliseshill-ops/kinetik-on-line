import streamlit as st
import requests
import json
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from voice_to_text import transcribir_audio_bytes

# --- CONFIGURACIÓN Y SEGURIDAD ---
API_TOKEN = "ulises_pro_2026"
HEADERS = {"x-token": API_TOKEN}
URL_FASTAPI_CREAR = "http://127.0.0.1:8000/crear-producto/"
URL_FASTAPI_LISTAR = "http://127.0.0.1:8000/productos/"

DIR_IMAGENES = os.path.join("static", "imagenes")
os.makedirs(DIR_IMAGENES, exist_ok=True)

# Catálogos oficiales
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

st.set_page_config(page_title="Hecho en México - Admin 2026", page_icon="🇲🇽", layout="wide")
st.title("KINETIK Hecho en México - Panel de Control (Galería Múltiple)")

tab1, tab2, tab3, tab4 = st.tabs([
    "🥇️ KINETIK - Quienes somos", 
    "📝 Formulario Manual", 
    "📊 Inventario e Impresión",
    "🖼️ Galería y Fotos por SKU"
])

with tab1:
    st.subheader(" Creamos ropa deportiva para personas que buscan comodidad en su día a día, con telas, costuras y diseños de calidad. Diseñada para sentirte cómodo y seguro realizando cualquier actividad; para sentirte libre de impulsar tus movimientos, generando una mejor versión de ti mismo. ")
    

with tab2:
    st.subheader("📝 Captura Directa de Inventario con Galería Múltiple")
    
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
        st.markdown("#### 📦 Detalle del Producto, Precios y Galería de Fotos")
        c1, c2 = st.columns(2)
        with c1:
            desc = st.text_input("Descripción Original", placeholder="Ej: LEGGIN FIT LICRA NEGRO TALLA S")
            p_costo = st.number_input("Precio Costo ($MXN)", min_value=0.0, step=5.0)
            p_venta = st.number_input("Precio Venta Público ($MXN)", min_value=0.0, step=5.0)
            p_may = st.number_input("Precio Mayoreo ($MXN)", min_value=0.0, step=5.0)
        with c2:
            dep = st.text_input("Departamento / Sección", value=sel_genero, placeholder="Ej: HOMBRE / DEPORTES")
            exi = st.number_input("Existencia en Tienda", min_value=1, step=1, value=1)
            inv_min = st.number_input("Inventario Mínimo", min_value=0, value=5)
            inv_max = st.number_input("Inventario Máximo", min_value=0, value=50)
            
            # --- CARGA MÚLTIPLE DE IMÁGENES ---
            fotos_subidas = st.file_uploader("📷 Subir Galería de Fotos (Múltiples JPG / PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        col_sku_disp, col_bar_disp, col_img_disp = st.columns([1, 1, 1])
        with col_sku_disp:
            st.text_input("🔑 SKU Autogenerado", value=codigo_calculado, disabled=True)
        with col_bar_disp:
            st.text_input("🏷️ Código EAN-13", value=codigo_barras_calculado, disabled=True)
        with col_img_disp:
            img_preview = generar_imagen_barcode_memoria(codigo_barras_calculado, float(p_venta), sel_prenda)
            st.image(img_preview, caption=f"Vista previa (${p_venta:.2f} MXN)", width=200)

        boton_manual = st.form_submit_button("🚀 Guardar Producto y Generar Historia")
        
        if boton_manual:
            if desc:
                rutas_imagenes_relativas = []
                if fotos_subidas:
                    for i, foto in enumerate(fotos_subidas):
                        ext = foto.name.split(".")[-1]
                        nombre_archivo = f"{codigo_calculado}_{i+1}.{ext}"
                        ruta_fisica = os.path.join(DIR_IMAGENES, nombre_archivo)
                        
                        with open(ruta_fisica, "wb") as f:
                            f.write(foto.getbuffer())
                        
                        rutas_imagenes_relativas.append(os.path.join("static", "imagenes", nombre_archivo).replace("\\", "/"))

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
                    "imagen_url": rutas_imagenes_relativas[0] if rutas_imagenes_relativas else None,
                    "imagenes": rutas_imagenes_relativas
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
                        st.session_state["rutas_imgs_recientes"] = rutas_imagenes_relativas
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
        
        st.success(f"✅ ¡Producto [{sku_c}] guardado exitosamente con su galería!")
        if st.session_state.get("rutas_imgs_recientes"):
            st.info(f"📷 Imágenes almacenadas: `{len(st.session_state['rutas_imgs_recientes'])} archivos`")
        
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
                
                # --- BUSCADOR INTELIGENTE POR CÓDIGO O DESCRIPCIÓN ---
                st.markdown("### 🔍 Buscador Inteligente de Prendas")
                c_busq1, c_busq2 = st.columns([2, 1])
                with c_busq1:
                    query_busqueda = st.text_input("Ingresa el código SKU exacto o fragmento a buscar:", placeholder="Ej. 3641741 o SUDADERA")
                with c_busq2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_limpiar = st.button("🔄 Ver Todo el Inventario")

                df_filtrado = df.copy()
                if query_busqueda:
                    df_filtrado = df_filtrado[
                        df_filtrado['codigo'].astype(str).str.contains(query_busqueda, case=False, na=False) |
                        df_filtrado['descripcion_original'].astype(str).str.contains(query_busqueda, case=False, na=False) |
                        df_filtrado['prenda'].astype(str).str.contains(query_busqueda, case=False, na=False)
                    ]
                    st.info(f"Se encontraron **{len(df_filtrado)}** coincidencias para: *{query_busqueda}*")

                st.dataframe(df_filtrado, use_container_width=True)
                
                col_dl, col_print = st.columns([1, 1])
                with col_dl:
                    csv_data = df_filtrado.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Descargar Inventario Filtrado en CSV",
                        data=csv_data,
                        file_name="inventario_filtrado_hecho_en_mexico.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.divider()
                
                st.markdown("### 🏷️ Generar e Imprimir Etiqueta de Código de Barras por SKU")
                lista_skus = df['codigo'].tolist()
                sku_elegido = st.selectbox("Selecciona o busca el SKU del producto:", lista_skus)
                
                if sku_elegido:
                    prod_row = df[df['codigo'] == sku_elegido].iloc[0]
                    p_venta_val = float(prod_row.get('precio_venta', 0.0))
                    prenda_val = str(prod_row.get('prenda', ''))
                    desc_val = str(prod_row.get('descripcion_original', ''))
                    
                    bc_val = calcular_codigo_barras_pos(sku_elegido)
                    
                    col_b_img, col_b_info = st.columns([1, 2])
                    with col_b_img:
                        img_etiqueta = generar_imagen_barcode_memoria(bc_val, p_venta_val, prenda_val)
                        st.image(img_etiqueta, caption=f"SKU: {sku_elegido}", use_container_width=True)
                        st.download_button(
                            label=f"🖨️ Descargar Etiqueta ({sku_elegido})",
                            data=img_etiqueta,
                            file_name=f"etiqueta_{sku_elegido}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    with col_b_info:
                        st.markdown(f"**Prenda:** {prenda_val}")
                        st.markdown(f"**Descripción:** {desc_val}")
                        st.markdown(f"**Precio Público:** ${p_venta_val:,.2f} MXN")
                        st.markdown(f"**Código EAN-13 Calculado:** `{bc_val}`")
                        st.success("💡 ¡Listo para escanear en caja o mandar a imprimir para etiquetar tus prendas en tienda!")
            else:
                st.info("Aún no hay productos registrados.")
    except Exception as e:
        st.error(f"Error al conectar con el API: {e}")

# --- PESTAÑA 4: GESTIÓN Y ACTUALIZACIÓN DE FOTOS POR SKU ---
with tab4:
    st.subheader("🖼️ Galería Visual y Edición Fotográfica por SKU")
    st.markdown("Utiliza este módulo para consultar las imágenes actuales de cualquier prenda o añadir/reemplazar fotos.")
    
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
                        st.markdown(f"##### 📷 Galería fotográfica activa ({len(fotos_actuales)} fotos):")
                        cols_f = st.columns(min(len(fotos_actuales), 5))
                        for idx, f_url in enumerate(fotos_actuales):
                            with cols_f[idx % 5]:
                                st.image(f_url, caption=f"Foto {idx+1}", use_container_width=True)
                    else:
                        st.info("ℹ️ Este producto no cuenta con fotos registradas en su galería actualmente.")
                    
                    st.divider()
                    st.markdown("##### 📤 Cargar Nuevas Imágenes")
                    
                    # --- OPCIÓN DE AGREGAR VS REEMPLAZAR ---
                    modo_actualizacion = st.radio(
                        "Acción a realizar con las fotos:",
                        options=["Agregar a la galería existente", "Reemplazar toda la galería"],
                        index=0,
                        help=" 'Agregar' anexa las nuevas fotos sin borrar las existentes. 'Reemplazar' borra las anteriores."
                    )
                    
                    nuevas_fotos_subidas = st.file_uploader(
                        "Selecciona las imágenes para este SKU:", 
                        type=["jpg", "jpeg", "png"], 
                        accept_multiple_files=True,
                        key=f"uploader_{sku_a_editar}"
                    )
                    
                    if st.button("🚀 Procesar Galería Fotográfica", use_container_width=True):
                        if nuevas_fotos_subidas:
                            rutas_nuevas = []
                            offset_inicial = len(fotos_actuales) if "Agregar" in modo_actualizacion else 0
                            
                            for i, foto in enumerate(nuevas_fotos_subidas):
                                ext = foto.name.split(".")[-1]
                                nombre_archivo = f"{sku_a_editar}_{offset_inicial + i + 1}.{ext}"
                                ruta_fisica = os.path.join(DIR_IMAGENES, nombre_archivo)
                                
                                with open(ruta_fisica, "wb") as f:
                                    f.write(foto.getbuffer())
                                
                                rutas_nuevas.append(os.path.join("static", "imagenes", nombre_archivo).replace("\\", "/"))
                            
                            modo_api = "reemplazar" if "Reemplazar" in modo_actualizacion else "agregar"
                            payload_update = {
                                "imagenes": rutas_nuevas,
                                "modo": modo_api
                            }
                            
                            url_up = f"http://127.0.0.1:8000/actualizar-fotos/{sku_a_editar}"
                            r_up = requests.put(url_up, json=payload_update, headers=HEADERS)
                            
                            if r_up.status_code == 200:
                                st.balloons()
                                res_json = r_up.json()
                                st.success(f"🎉 ¡Galería del SKU [{sku_a_editar}] actualizada exitosamente!")
                                st.info(f"💡 Total de fotos en la galería activa: `{len(res_json.get('imagenes', []))}` fotos.")
                            else:
                                st.error(f"Error {r_up.status_code}: {r_up.text}")
                        else:
                            st.warning("⚠️ Por favor sube al menos una imagen antes de procesar.")
                else:
                    st.warning(f"⚠️ No se encontró ninguna prenda registrada con el SKU '{sku_a_editar}'.")
        except Exception as e:
            st.error(f"Error al conectar con la API de productos: {e}")