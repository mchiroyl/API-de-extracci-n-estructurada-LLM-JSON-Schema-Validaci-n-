"""
llm_client.py — Cliente para la API de OpenAI.

Se encarga de enviar el prompt al modelo, recibir la respuesta
y parsear el JSON resultante.
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT, build_extraction_prompt

# Cargar variables de entorno
load_dotenv()

# Configurar la API key
API_KEY = os.getenv("OPENAI_API_KEY")

# Usar el modelo de Groq para parseo JSON
MODEL_NAME = "llama-3.3-70b-versatile"



def call_openai(text: str, domain: str) -> dict:
    """
    Envía el texto al modelo de OpenAI y devuelve la respuesta parseada como diccionario.
    Utiliza Structured Outputs (response_format) soportado por GPT-4o-mini.
    """
    user_prompt = build_extraction_prompt(text, domain)

    # Instanciar el cliente usando la base URL de Groq
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = completion.choices[0].message.content
        result_dict = json.loads(content)
        return result_dict

    except Exception as e:
        raise e
