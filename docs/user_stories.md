# Historias de Usuario - ReviewMind-API

## Historia de Usuario 1: Análisis y Clasificación Automática de Reseñas por IA

Como Product Manager,
quiero que el backend acepte reseñas mediante un endpoint POST y utilice Gemini para analizar y clasificar automáticamente el contenido,
para que las reseñas queden estructuradas con sentimiento, categoría y etiquetas relevantes en Firestore.

### Criterios de Aceptación

Escenario: Envío de reseña y clasificación automática por IA
  Dado que un cliente envía una solicitud POST a `/api/v1/reviews/` con los campos `userId`, `productId`, `rating` y `text`
  Cuando el backend recibe la solicitud
  Entonces el servicio debe invocar a la API de Gemini para analizar el texto de la reseña
  Y debe recibir de Gemini los resultados de sentimiento, categoría y etiquetas
  Y debe almacenar en Firestore el documento de reseña con los datos originales más el análisis IA
  Y debe responder con un estado `201 Created` y el payload de la reseña enriquecida.

Escenario: Manejo de error en la comunicación con Gemini
  Dado que el backend envía el texto de reseña a Gemini
  Cuando la llamada a la API de Gemini falla o devuelve una respuesta inválida
  Entonces el backend debe responder con un estado `502 Bad Gateway`
  Y debe incluir un mensaje de error claro indicando que el análisis de IA no pudo completarse.

## Historia de Usuario 2: Autenticación e Identidad de Usuarios con Firebase Auth

Como Product Manager,
quiero que los usuarios sean autenticados mediante Firebase Auth antes de crear o consultar reseñas,
para que la API garantice identificación segura y permita asociar reseñas a usuarios reales.

### Criterios de Aceptación

Escenario: Acceso protegido a endpoints de reseñas con token Firebase
  Dado que un usuario intenta acceder a un endpoint de reseñas
  Cuando la solicitud incluye un token de Firebase Auth válido en el encabezado `Authorization`
  Entonces el backend debe verificar el token con Firebase Auth
  Y debe extraer el `userId` autenticado del token
  Y debe permitir la operación solo si la verificación es exitosa.

Escenario: Rechazo de solicitudes sin autenticación válida
  Dado que un usuario intenta acceder a un endpoint de reseñas
  Cuando la solicitud no incluye un token de Firebase Auth válido
  Entonces el backend debe responder con un estado `401 Unauthorized`
  Y debe incluir un mensaje que indique que la autenticación es requerida.
