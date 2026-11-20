import os
import sys
import time
import requests

# Toma la URL desde los Secrets de GitHub o usa tu URL oficial por defecto
RENDER_URL = os.getenv("RENDER_API_URL", "https://kinetik-on-line.onrender.com/productos/")
TIMEOUT_SEGUNDOS = 45  # Margen amplio por si Render viene despertando de un cold start

def ejecutar_ping():
    print(f"🚀 Iniciando pulso keep-alive hacia: {RENDER_URL}")
    inicio = time.perf_counter()
    
    try:
        respuesta = requests.get(RENDER_URL, timeout=TIMEOUT_SEGUNDOS)
        latencia_ms = (time.perf_counter() - inicio) * 1000
        
        if respuesta.status_code == 200:
            data = respuesta.json()
            total_items = len(data) if isinstance(data, list) else "OK"
            print(f"✅ Render ACTIVO (HTTP 200) | Latencia: {latencia_ms:.0f} ms | Productos en catálogo: {total_items}")
        else:
            print(f"⚠️ Render respondió con HTTP {respuesta.status_code} ({latencia_ms:.0f} ms): {respuesta.text[:150]}")
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        print(f"⏳ Timeout tras {TIMEOUT_SEGUNDOS}s: Render estaba dormido o tardó en responder.")
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"❌ Error de conexión al contactar Render: {err}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_ping()