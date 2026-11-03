import pandas as pd
import requests
import time
import ast

# URL oficial de producción en Render
API_URL = "https://kinetik-on-line.onrender.com/crear-producto/"
ARCHIVO_CSV = "inventario_hecho_en_mexico_20261102.csv"
API_TOKEN = "ulises_pro_2026"

def cargar_datos_masivos():
    try:
        print(f"--- 🚀 Leyendo layout 2026 en Render: {ARCHIVO_CSV} ---")
        df = pd.read_csv(ARCHIVO_CSV, dtype={'CODIGO': str, 'C.BARRAS': str, 'codigo': str, 'codigo_barras': str})
        
        df.columns = df.columns.str.strip().str.lower()
        headers = {"x-token": API_TOKEN}
        
        for index, row in df.iterrows():
            lista_imagenes = []
            raw_imagenes = row.get('imagenes', None)
            
            if pd.notna(raw_imagenes):
                str_imgs = str(raw_imagenes).strip()
                if str_imgs.startswith('[') and str_imgs.endswith(']'):
                    try:
                        lista_imagenes = ast.literal_eval(str_imgs)
                    except Exception:
                        lista_imagenes = [str_imgs]
                else:
                    lista_imagenes = [img.strip() for img in str_imgs.split(',') if img.strip()]

            payload = {
                "codigo": str(row.get('codigo', '')).strip(),
                "prenda": str(row.get('prenda', '')).strip(),
                "descripcion_original": str(row.get('descripcion_original', '')).strip(),
                "precio_costo": float(row.get('precio_costo', 0.0)),
                "precio_venta": float(row.get('precio_venta', 0.0)),
                "color": str(row.get('color', '')).strip(),
                "precio_mayoreo": float(row.get('precio_mayoreo', 0.0)),
                "departamento": str(row.get('departamento', 'GENERAL')).strip(),
                "existencia": int(row.get('existencia', 0)),
                "inventario_minimo": int(row.get('inventario_minimo', 5)),
                "inventario_maximo": int(row.get('inventario_maximo', 50)),
                "genero": str(row.get('genero', '')).strip() if pd.notna(row.get('genero')) else None,
                "tipo_tela": str(row.get('tipo_tela', '')).strip() if pd.notna(row.get('tipo_tela')) else None,
                "corte": str(row.get('corte', '')).strip() if pd.notna(row.get('corte')) else None,
                "proveedor": str(row.get('proveedor', '')).strip() if pd.notna(row.get('proveedor')) else None,
                "talla": str(row.get('talla', '')).strip() if pd.notna(row.get('talla')) else None,
                "imagen_url": lista_imagenes[0] if lista_imagenes else None,
                "imagenes": lista_imagenes
            }
            
            codigo_item = payload['codigo']
            print(f"📦 Procesando [{index + 1}/{len(df)}]: SKU '{codigo_item}' en Render...")
            
            res = requests.post(API_URL, json=payload, headers=headers)
            
            if res.status_code == 200:
                print(f"  ✅ Guardado exitoso en producción: {codigo_item}")
            elif res.status_code == 400:
                print(f"  ⚠️ Ignorado: {res.json().get('detail', 'El producto ya existe.')}")
            elif res.status_code == 403:
                print("  🚫 Error 403: Token de seguridad inválido.")
                break
            else:
                print(f"  ❌ Error ({res.status_code}): {res.text}")
                
            time.sleep(1)
            
        print("\n🎉 ¡Proceso de carga masiva hacia la nube completado al 100%!")

    except Exception as e:
        print(f"🛑 Error fatal durante la carga masiva: {e}")

if __name__ == "__main__":
    cargar_datos_masivos()