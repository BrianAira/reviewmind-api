# Instrucciones del Proyecto: ReviewMind-API

- Adoptar estrictamente la estrategia de ramificación GitHub Flow (main es sagrada, se trabaja en ramas feature/*).
- Estructurar el backend de forma modular adoptando principios de Arquitectura Limpia.
- Frameworks obligatorios: FastAPI para la API, Firebase Admin SDK para la persistencia NoSQL y Google GenAI SDK (Gemini) para la capa de IA.
- Regla de oro de rendimiento: Todo el código de entrada/salida (I/O), base de datos y enrutamiento debe ser estrictamente asíncrono utilizando 'async' y 'await'.