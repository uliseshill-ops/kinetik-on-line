import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Forzamos la carga del .env buscando la ruta exacta de la raíz del proyecto
ruta_raiz = Path(__file__).resolve().parent
ruta_env = ruta_raiz / ".env"
load_dotenv(dotenv_path=ruta_env)

def generar_storytelling_mexicano(nombre_producto, descripcion_corta, estado_origen):
    # Validamos que la llave exista antes de inicializar el cliente
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("🛑 ALerta: La variable GROQ_API_KEY no fue encontrada en el entorno.")
        return "[ESPAÑOL]\nPrenda exclusiva Hecho en México. (Error: API Key no detectada)\n\n[ENGLISH]\nExclusive product Made in Mexico."

    # Inicializamos el cliente oficial con la llave asegurada
    client = Groq(api_key=api_key)
    
    prompt = f"""
    Eres un experto en marketing internacional de ropa deportiva y cultura mexicana. 
    Producto: {nombre_producto}
    Origen: {estado_origen}
    Descripción: {descripcion_corta}

    Genera dos historias cautivadoras para el producto.
    
    ESTRUCTURA REQUERIDA:
    [ESPAÑOL]
    Crea una descripción emocional y profesional de 2 párrafos que resalte 
    la calidad de lo 'Hecho en México' y la tradición de {estado_origen}.
    
    [ENGLISH]
    (Translate the same story into professional, high-end marketing English)
    
    REGLAS:
    - No uses más de 3 párrafos en total.
    - Mantén el tono fitness y premium.
    """
    
    try:
        # Usamos el modelo validado qwen/qwen3.8-27b
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un redactor experto en marketing de moda y cultura mexicana de lujo."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800,
        )
        
        respuesta_texto = completion.choices[0].message.content
        if respuesta_texto and respuesta_texto.strip():
            return respuesta_texto.strip()
        else:
            return "[ESPAÑOL]\nPrenda de alta calidad Hecho en México.\n\n[ENGLISH]\nPremium product Made in Mexico."
            
    except Exception as e:
        print(f"🛑 Error conectando con Groq en ai_helper: {e}")
        return f"[ESPAÑOL]\nPrenda exclusiva Hecho en México.\n\n[ENGLISH]\nExclusive product Made in Mexico. (Error API Groq: {e})"

# --- PRUEBA UNITARIA DIRECTA ---
#if __name__ == "__main__":
 #   print("🧪 Probando ai_helper directamente...")
  #  resultado_prueba = generar_storytelling_mexicano("sudadera oversize algodón", "descripción corta fitness", "México")
   # print("\n📝 Resultado obtenido:\n", resultado_prueba)