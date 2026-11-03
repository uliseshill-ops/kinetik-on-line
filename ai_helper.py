import os
import requests
import json

def generar_storytelling_mexicano(nombre_producto, descripcion_corta, estado_origen):
    prompt = f"""
    Eres un experto en marketing internacional y cultura mexicana. 
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
    - No uses más de 4 párrafos en total.
    - Mantén el tono artesanal y premium.
    """
    
    # Obtenemos la llave de Groq de las variables de entorno de la nube (Render)
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Respaldo por si la variable de entorno no está configurada temporalmente
    if not groq_api_key:
        return "[ESPAÑOL]\nPrenda deportiva de excelente calidad Hecho en México, diseñada para impulsar tus movimientos con máximo confort.\n\n[ENGLISH]\nHigh-end sportswear proudly Made in Mexico, designed to empower your daily movement with ultimate comfort."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": "Eres un redactor experto en marketing de moda y cultura mexicana de lujo."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"[ESPAÑOL]\nPrenda de alta calidad Hecho en México.\n\n[ENGLISH]\nPremium product Made in Mexico. (Error API Groq: {response.status_code})"
    except Exception as e:
        return f"[ESPAÑOL]\nPrenda exclusiva Hecho en México.\n\n[ENGLISH]\nExclusive product Made in Mexico. (Excepción de red: {e})"