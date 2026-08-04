import os
import json
from pydantic import BaseModel

class ReviewAnalysisResult(BaseModel):
    sentiment: str
    urgency: str
    reasoning: str

async def analyze_review_text(text: str) -> ReviewAnalysisResult:
    # Verificación de la API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is required for Gemini analysis.")

    # Importación correcta del SDK de Google GenAI
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("El paquete 'google-genai' no está instalado. Ejecuta 'pip install google-genai'.") from exc

    # Inicialización del cliente oficial
    client = genai.Client(api_key=api_key)

    prompt = (
        "Analiza el siguiente texto de reseña y determina el sentimiento (POSITIVO, NEUTRO, NEGATIVO) "
        "y la urgencia de atención (BAJA, MEDIA, ALTA).\n"
        "Devuelve únicamente un objeto JSON plano con las claves: 'sentiment', 'urgency' y 'reasoning'.\n\n"
        f"Texto de la reseña: \"{text}\""
    )

    try:
        # Llamada asíncrona nativa oficial del SDK de Gemini
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
        )
        
        # Limpieza de marcado markdown en caso de que el modelo responda con ```json ... ```
        raw_text = response.text.strip().strip("```json").strip("```").strip()
        data = json.loads(raw_text)

        return ReviewAnalysisResult(
            sentiment=data.get("sentiment", "NEUTRO"),
            urgency=data.get("urgency", "MEDIA"),
            reasoning=data.get("reasoning", "Análisis completado sin justificación detallada.")
        )
    except Exception as exc:
        raise RuntimeError(f"Error procesando la respuesta con Gemini: {str(exc)}") from exc