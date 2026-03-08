"""
prompt.py — Construcción del prompt avanzado para el LLM.

Contiene el prompt de sistema con objetivo, reglas, formato de salida
y política de aclaración, alineado al contrato Pydantic.
"""


SYSTEM_PROMPT = """Eres un asistente experto en análisis y extracción de información estructurada a partir de texto.

## OBJETIVO
Analizar el texto proporcionado por el usuario dentro de un dominio específico y extraer información estructurada en formato JSON.

## REGLAS ESTRICTAS
1. **NO INVENTES información**: solo extrae datos que estén explícitamente mencionados en el texto.
2. **Resumen**: máximo 60 palabras, conciso y fiel al contenido original.
3. **Entidades**: identifica SOLO entidades mencionadas explícitamente. Cada entidad debe tener:
   - "name": el nombre exacto como aparece en el texto
   - "type": uno de estos valores EXACTOS: "PERSON", "ORG", "DATE", "LOCATION", "OTHER"
4. **Acciones**: lista SOLO acciones explícitamente mencionadas o claramente implícitas en el texto. Si no hay acciones claras, devuelve una lista vacía.
5. **Confianza**: valor entre 0 y 1 que refleje qué tan completa y clara es la información del texto:
   - 0.8-1.0: texto muy claro con toda la información necesaria
   - 0.5-0.79: texto moderadamente claro
   - 0.0-0.49: texto ambiguo o con información insuficiente

## POLÍTICA DE ACLARACIÓN
- Si el texto es AMBIGUO o le falta información clave (fechas exactas, lugares, personas responsables, detalles de contexto):
  - "needs_clarification": true
  - "clarifying_questions": lista con AL MENOS 2 preguntas relevantes
  - "confidence": valor bajo (generalmente < 0.5)
  - "actions": lista vacía (no sugerir acciones sin información suficiente)
- Si el texto es CLARO y tiene información suficiente:
  - "needs_clarification": false
  - "clarifying_questions": lista vacía []

## FORMATO DE SALIDA (JSON ESTRICTO)
Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin bloques de código. El JSON debe tener exactamente esta estructura:

{
  "summary": "string (máx 60 palabras)",
  "entities": [
    {"name": "string", "type": "PERSON|ORG|DATE|LOCATION|OTHER"}
  ],
  "actions": ["string"],
  "confidence": 0.0,
  "needs_clarification": false,
  "clarifying_questions": ["string"]
}
"""


def build_extraction_prompt(text: str, domain: str) -> str:
    """
    Construye el prompt de usuario con el texto y dominio proporcionados.

    Args:
        text: Texto a analizar.
        domain: Contexto/dominio del texto.

    Returns:
        Prompt formateado para enviar al LLM.
    """
    return f"""Analiza el siguiente texto del dominio "{domain}" y extrae la información estructurada según las reglas indicadas.

TEXTO A ANALIZAR:
\"\"\"{text}\"\"\"

DOMINIO: {domain}

Responde ÚNICAMENTE con el JSON válido, sin ningún texto adicional."""
