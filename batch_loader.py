import pandas as pd
import requests
import time
import ast

# --- CONFIGURACIÓN DEL BÓLIDO DE CARGA MASIVA EN LA NUBE ---
API_URL = "https://kinetik-on-line.onrender.com/crear-producto/"
ARCHIVO_CSV = "inventario_filtrado_hecho_en_mexico_20261111.csv"  # Tu archivo real con el layout completo y galería
API_TOKEN = "ulises_pro_2026"  # La llave del Ferrari 🏎️

def cargar_datos_masivos():
    try:
        print(f"--- Leyendo archivo de inventario exportado: {ARCHIVO_CSV} ---")
        
        # Leemos el CSV asegurándonos de tratar todo como String
        df = pd.read_csv(ARCHIVO_CSV, dtype=str)
        
        headers = {"x-token": API_TOKEN} 
        total_filas = len(df)
        
        print(f"📦 Total de registros detectados para carga masiva a Supabase: {total_filas}\n")
        
        for index, row in df.iterrows():
            # 1. Extraer imagen_url principal de forma segura
            imagen_val = str(row['imagen_url']).strip() if 'imagen_url' in row and pd.notna(row['imagen_url']) else None
            if imagen_val and imagen_val.lower() in ["nan", "none", ""]:
                imagen_val = None

            # 2. Parsear la columna 'imagenes' (que viene como string de lista tipo "['url1', 'url2']")
            lista_imagenes = []
            if 'imagenes' in row and pd.notna(row['imagenes']):
                raw_imgs = str(row['imagenes']).strip()
                try:
                    parsed = ast.literal_eval(raw_imgs)
                    if isinstance(parsed, list):
                        lista_imagenes = [str(u).strip() for u in parsed if str(u).strip()]
                except Exception:
                    if raw_imgs and raw_imgs.lower() not in ["nan", "none", ""]:
                        lista_imagenes = [raw_imgs]

            # Si no hay lista pero hay imagen_url principal, la metemos
            if not lista_imagenes and imagen_val:
                lista_imagenes = [imagen_val]

            # Mapeo completo alineado al ProductoSchema de FastAPI (con todos los campos del layout)
            payload = {
                "codigo": str(row['codigo']).strip(),
                "prenda": str(row['prenda']).strip(),
                "descripcion_original": str(row['descripcion_original']).strip(),
                "precio_costo": float(row['precio_costo']) if pd.notna(row['precio_costo']) else 0.0,
                "precio_venta": float(row['precio_venta']) if pd.notna(row['precio_venta']) else 0.0,
                "color": str(row['color']).strip() if pd.notna(row['color']) else "GENERAL",
                "precio_mayoreo": float(row['precio_mayoreo']) if pd.notna(row['precio_mayoreo']) else 0.0,
                "departamento": str(row['departamento']).strip() if pd.notna(row['departamento']) else "GENERAL",
                "existencia": int(float(row['existencia'])) if pd.notna(row['existencia']) else 0,
                "inventario_minimo": int(float(row['inventario_minimo'])) if pd.notna(row['inventario_minimo']) else 5,
                "inventario_maximo": int(float(row['inventario_maximo'])) if pd.notna(row['inventario_maximo']) else 50,
                
                # Campos extendidos y galería de Supabase Storage
                "imagen_url": imagen_val,
                "imagenes": lista_imagenes,
                "genero": str(row['genero']).strip() if 'genero' in row and pd.notna(row['genero']) else "GENERAL",
                "tipo_tela": str(row['tipo_tela']).strip() if 'tipo_tela' in row and pd.notna(row['tipo_tela']) else "GENERAL",
                "corte": str(row['corte']).strip() if 'corte' in row and pd.notna(row['corte']) else "GENERAL",
                "proveedor": str(row['proveedor']).strip() if 'proveedor' in row and pd.notna(row['proveedor']) else "GENERAL",
                "talla": str(row['talla']).strip() if 'talla' in row and pd.notna(row['talla']) else "UNITALLA",
                "costo_indirecto": float(row['costo_indirecto']) if 'costo_indirecto' in row and pd.notna(row['costo_indirecto']) else 0.0,
                "margen": float(row['margen']) if 'margen' in row and pd.notna(row['margen']) else 0.0,
                "codigo_barras": str(row['codigo_barras']).strip() if 'codigo_barras' in row and pd.notna(row['codigo_barras']) else None,
                "columna": str(row['columna']).strip() if 'columna' in row and pd.notna(row['columna']) else None,
                "caja": str(row['caja']).strip() if 'caja' in row and pd.notna(row['caja']) else None
            }
            
            print(f"🚀 Procesando [{index+1}/{total_filas}]: SKU {payload['codigo']} ({payload['descripcion_original']}) con {len(lista_imagenes)} foto(s)...")
            
            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ ¡Éxito! SKU {payload['codigo']} guardado con su galería en Supabase y storytelling de Groq.")
                elif response.status_code == 400:
                    detalle = response.json().get('detail', 'El producto ya existe.')
                    print(f"⚠️ Saltado: {detalle}")
                elif response.status_code == 403:
                    print("🚫 Error de Seguridad: Token inválido. Deteniendo carga.")
                    break
                else:
                    print(f"❌ Error en SKU {payload['codigo']}: {response.status_code} - {response.text}")
            
            except Exception as e:
                print(f"❌ No se pudo conectar con el servidor: {e}")
            
            time.sleep(1) 

        print("\n--- ¡Carga masiva completada con éxito al 100%! ---")

    except Exception as e:
        print(f"🛑 Error fatal al procesar el archivo: {e}")

if __name__ == "__main__":
    cargar_datos_masivos()