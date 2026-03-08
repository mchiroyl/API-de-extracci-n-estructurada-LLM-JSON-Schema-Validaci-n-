# API de Extracción de Texto Estructurada

Microservicio con **FastAPI** que recibe un texto y su dominio, lo analiza usando **OpenAI** mediante *Structured Outputs*, y devuelve un JSON estructurado y validado con:

- **Resumen** del texto (máx. 60 palabras)
- **Entidades** extraídas (personas, organizaciones, fechas, ubicaciones)
- **Acciones** sugeridas
- **Nivel de confianza** (0 a 1)
- **Preguntas de aclaración** si el texto es ambiguo

## Tecnologías

- Python 3.10+
- FastAPI + Pydantic (contrato de salida estricta y validación en servidor)
- OpenAI API (`openai`, modelo mediante base URL alternativa)
- Uvicorn (servidor ASGI)
- Python-Dotenv (manejo seguro de API keys)

## Estructura del Proyecto

```
api/
├── main.py            # App FastAPI principal con endpoint POST /extract
├── models.py          # Modelos Pydantic (request, response, entities, clarificaciones)
├── prompt.py          # Ingeniería del prompt, reglas estrictas y formato
├── llm_client.py      # Cliente de conexión a OpenAI
├── requirements.txt   # Dependencias de Python
├── .env               # API Key de OpenAI (No subir al repositorio)
├── .gitignore         # Evita subir archivos temporales y secretos
└── README.md          # Esta documentación
```

## Cómo Ejecutar el Proyecto

### 1. Clonar el repositorio y acceder a la carpeta

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd api
```

### 2. Crear entorno virtual e instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
.\venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate

# Instalar los paquetes necesarios
pip install -r requirements.txt
```

### 3. Configurar API Key

Editar el archivo `.env` y reemplazar `TU_API_KEY_AQUI` con tu clave real.

```env
OPENAI_API_KEY=tu_clave_real_de_api
```

### 4. Levantar la API e Iniciar el Servidor

```bash
uvicorn main:app --reload --port 8000
```
> El servidor estará disponible en `http://localhost:8000`. \
> Para probar tu código de forma interactiva e interfaz gráfica, ingresa a: **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI).

---

## Pruebas de Request / Response (Casos)

Puedes probar el endpoint usando la terminal (con `curl`) o herramientas como herramienta de pruebas (Por ejemplo: [Postman](https://www.postman.com/)) enviando un POST a `http://localhost:8000/extract`.

### Caso: Texto Analizable

**Petición JSON (Request):**
```json
{
  "text": "La Universidad organizará una reunión el 10 de abril de 2026 en el auditorio principal. María López coordinará el evento.",
  "domain": "universidad"
}
```

**Respuesta JSON (Response):**
```json
{
  "summary": "Se organizará una reunión el 10 de abril de 2026 en el auditorio principal, coordinada por María López.",
  "entities": [
    {
      "name": "Universidad",
      "type": "ORG"
    },
    {
      "name": "10 de abril de 2026",
      "type": "DATE"
    },
    {
      "name": "auditorio principal",
      "type": "LOCATION"
    },
    {
      "name": "María López",
      "type": "PERSON"
    }
  ],
  "actions": [
    "Asistir a la reunión el 10 de abril de 2026",
    "Contactar a María López para coordinación"
  ],
  "confidence": 0.9,
  "needs_clarification": false,
  "clarifying_questions": []
}
```

### Caso: Texto ambiguo (Requiere aclaración)

**Petición JSON (Request):**
```json
{
  "text": "Hay una reunión la próxima semana para revisar el proyecto. Necesitamos decidir el lugar y quién presentará.",
  "domain": "universidad"
}
```

**Respuesta JSON (Response):**
```json
{
  "summary": "Reunión programada para la próxima semana con el objetivo de revisar el proyecto.",
  "entities": [
    {
      "name": "próxima semana",
      "type": "DATE"
    }
  ],
  "actions": [
    "Decidir el lugar de la reunión.",
    "Decidir quién será el presentador."
  ],
  "confidence": 0.3,
  "needs_clarification": true,
  "clarifying_questions": [
    "¿En qué lugar físico o plataforma virtual se llevará a cabo la reunión?",
    "¿Quién será la persona encargada de presentar?"
  ]
}
```

## Explicación Técnica y Arquitectura

- **Contrato de Salida Estricto (`models.py`)**: Utilizando `Pydantic` se define y restringe la respuesta (ej. la confianza en rango `0.0 a 1.0` y que los tipos de Entidades no se inventen). Se codificó un bloque `@model_validator` para prohibir que un modelo responda `needs_clarification=True` sin una lista de al menos dos (`>= 2`) preguntas.
- **Validación Automática (`main.py`)**: Con `response_model=ExtractionResponse`, la capa del servidor realiza la serialización protegiendo a la aplicación de inyecciones del LLM.
- **Prompt Enforzado (`prompt.py`)**: Centraliza la inteligencia artificial con una política clara de cómo deducir las aclaraciones o resumir todo estructuradamente, según indicaciones del contrato.
