import os
import requests
import json

# Puedes configurar tu GROQ_API_KEY en las variables de entorno del servidor cloud (Render/HuggingFace)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "tu_api_key_aqui")

def generar_storytelling_mexicano(nombre_producto, descripcion_corta, estado_origen, contexto_extra=""):
    """
    Genera narrativa comercial en la nube usando la API de Groq (Llama 3.3) 
    aprovechando detalles de tela, corte y género.
    """
    prompt = f"""
    Eres un experto en marketing internacional y moda mexicana. 
    Producto: {nombre_producto}
    Origen / Departamento: {estado_origen}
    Descripción: {descripcion_corta}
    Detalles Técnicos: {contexto_extra}

    Genera dos historias cautivadoras para el producto resaltando la calidad textil mexicana.
    
    ESTRUCTURA REQUERIDA:
    [ESPAÑOL]
    Crea una descripción emocional y profesional de 1 párrafo que resalte 
    la calidad de lo 'Hecho en México', la confección y la tradición de {estado_origen}.
    
    [ENGLISH]
    (Translate the same story into professional, high-end marketing English)
    
    REGLAS:
    - No uses más de 3 renglones en total.
    - Mantén el tono de ropa deportiva, cómodo y premium.
    """
    
    # Endpoint compatible con OpenAI / Groq Cloud para inferencia ultrarrápida de Llama 3
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['choices']['message']['content']
        else:
            return f"Hecho en México: {nombre_producto} de alta calidad. (IA Cloud temporalmente offline: {response.status_code})"
    except Exception as e:
        return f"Error conectando con la API de IA en la nube: {e}"