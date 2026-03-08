"""
main.py — Aplicación FastAPI con el endpoint POST /extract.

Punto de entrada del microservicio. Usa response_model para
validar y documentar la respuesta automáticamente.
"""

from fastapi import FastAPI, HTTPException
from models import ExtractionRequest, ExtractionResponse
from llm_client import call_openai

app = FastAPI(
    title="API de Extracción de Texto Estructurada",
    description=(
        "Microservicio que recibe texto y un dominio, y devuelve una respuesta "
        "JSON estructurada con resumen, entidades, acciones, nivel de confianza "
        "y preguntas de aclaración cuando la información es insuficiente."
    ),
    version="1.0.0",
)


@app.post(
    "/extract",
    response_model=ExtractionResponse,
    summary="Extraer información estructurada del texto",
    description=(
        "Recibe un texto y su dominio, lo analiza con un LLM (OpenAI) "
        "y devuelve un JSON validado con resumen, entidades, acciones, confianza "
        "y preguntas de aclaración si el texto es ambiguo."
    ),
)
async def extract(request: ExtractionRequest):
    """
    Endpoint principal: recibe texto + dominio y devuelve la extracción estructurada.

    - Si el texto es claro: needs_clarification=false, clarifying_questions=[]
    - Si el texto es ambiguo: needs_clarification=true, clarifying_questions con ≥2 preguntas
    """
    try:
        # Llamar al LLM para obtener la respuesta
        llm_result = call_openai(request.text, request.domain)

        # Validar la respuesta con el modelo Pydantic
        # response_model de FastAPI se encarga de la validación final,
        # pero hacemos la validación aquí también para capturar errores del LLM
        response = ExtractionResponse(**llm_result)

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Error al procesar la respuesta del LLM: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/", summary="Health check")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "status": "ok",
        "message": "API de Extracción de Texto Estructurada está activa",
        "docs": "/docs",
    }
