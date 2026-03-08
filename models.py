"""
models.py — Modelos Pydantic para el contrato de entrada/salida del endpoint /extract.

Define la estructura exacta del request y response, con validaciones
para asegurar que la respuesta del LLM cumpla con el contrato.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Literal


class ExtractionRequest(BaseModel):
    """Modelo de entrada para el endpoint POST /extract."""
    text: str = Field(
        ...,
        min_length=1,
        description="Texto a analizar"
    )
    domain: str = Field(
        ...,
        min_length=1,
        description="Contexto del texto (ej.: 'universidad', 'soporte', 'ventas')"
    )


class Entity(BaseModel):
    """Entidad extraída del texto."""
    name: str = Field(..., description="Nombre de la entidad")
    type: Literal["PERSON", "ORG", "DATE", "LOCATION", "OTHER"] = Field(
        ...,
        description="Tipo de entidad"
    )


class ExtractionResponse(BaseModel):
    """
    Modelo de respuesta (contrato de salida) del endpoint POST /extract.
    FastAPI usa este modelo como response_model para validar y documentar la respuesta.
    """
    summary: str = Field(
        ...,
        description="Resumen del texto en máximo 60 palabras"
    )
    entities: list[Entity] = Field(
        default_factory=list,
        description="Lista de entidades extraídas del texto"
    )
    actions: list[str] = Field(
        default_factory=list,
        description="Acciones sugeridas explícitas (vacía si no hay)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza entre 0 y 1"
    )
    needs_clarification: bool = Field(
        ...,
        description="True si el texto necesita aclaración"
    )
    clarifying_questions: list[str] = Field(
        default_factory=list,
        description="Preguntas de aclaración (vacía si needs_clarification es false)"
    )

    @model_validator(mode="after")
    def validate_clarification_logic(self):
        """
        Validador personalizado:
        - Si needs_clarification=True, debe haber al menos 2 preguntas.
        - Si needs_clarification=False, la lista de preguntas debe estar vacía.
        """
        if self.needs_clarification and len(self.clarifying_questions) < 2:
            raise ValueError(
                "Cuando needs_clarification es True, se requieren al menos 2 preguntas en clarifying_questions."
            )
        if not self.needs_clarification and len(self.clarifying_questions) > 0:
            # Limpiar preguntas si no se necesita aclaración
            self.clarifying_questions = []
        return self
