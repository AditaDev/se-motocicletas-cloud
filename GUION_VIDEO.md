# Guion de video: sistema experto desplegado en la nube

**Duración orientativa:** 4 a 5 minutos. Grabar pantalla y explicar en voz propia, sin exponer cuentas, claves ni tokens.

## 0:00–0:35 | Introducción y objetivo

**Mostrar:** título del proyecto, enlace del servicio publicado.

**Narración:** «Nuestro proyecto es un sistema experto académico para orientar la identificación de posibles fallas en motocicletas. Utiliza un árbol de siete categorías y una base de conocimiento construida con hipótesis, hechos y relaciones entre ambos. El objetivo de esta actividad fue llevar el motor a un servicio cloud y crear una interfaz web para consultarlo.»

## 0:35–1:15 | Cuenta y exploración cloud

**Mostrar:** panel de Render; opcionalmente pestaña de catálogo de IA de Azure.

**Narración:** «La actividad permitía utilizar Azure u otra plataforma. Revisamos servicios como Microsoft Foundry, Azure AI Language, Azure AI Search y Azure Functions. Elegimos Render Web Service porque nuestro motor ya estaba desarrollado en Python y necesitábamos publicarlo sin añadir un modelo generativo. Render aloja la aplicación y la API; el sistema experto es nuestro código de reglas.»

## 1:15–2:05 | Base de conocimiento y despliegue

**Mostrar:** repositorio GitHub con `data/conocimiento.sqlite3`, `data/reglas_79.json`, `app.py`, `motor.py`, `repositorio.py`; panel del Web Service y URL.

**Narración:** «Conservamos la base de conocimiento del proyecto: 25 hipótesis, 37 hechos y 63 asociaciones. Para la demostración trasladamos esos datos desde MySQL a una copia de SQLite de solo lectura, almacenada en el repositorio y publicada con la aplicación. También conservamos el catálogo de las 79 reglas IF–AND–THEN. Render instaló Flask y Gunicorn y publica el motor mediante una API REST.»

## 2:05–3:25 | Demostración de la interfaz

**Mostrar:** abrir enlace de Render, seleccionar arranque, motor no gira, luces normales y clic, ver resultado.

**Narración:** «Ahora iniciamos una consulta en la interfaz. Cada respuesta se envía al servicio HTTP. El motor consulta de forma granular los hechos y las relaciones de la base, sigue únicamente la rama seleccionada y suma un punto a las hipótesis descendientes. En este ejemplo se selecciona S03, motor de arranque o relé, con tres puntos y 37,5 % de peso relativo.»

## 3:25–4:10 | Mostrar que es un servicio cloud

**Mostrar:** abrir en otra pestaña `/api/salud`, `/api/conocimiento/resumen` y `/api/conocimiento/hipotesis/S03`.

**Narración:** «La aplicación no depende de que el servidor se ejecute en mi computador. El endpoint de salud muestra la cantidad de hipótesis, hechos, relaciones y reglas; el endpoint de hipótesis permite consultar las condiciones IF y AND asociadas al diagnóstico. Estas respuestas provienen de la API que está alojada en Render.»

## 4:10–4:45 | Conclusión

**Mostrar:** interfaz de resultados y pantalla con arquitectura o código.

**Narración:** «Logramos publicar nuestro sistema experto como servicio cloud y consumirlo desde una interfaz web. Mantuvimos la estructura de conocimiento y el mecanismo de puntuación que definimos para la materia. Los porcentajes son pesos relativos calculados a partir de puntos y no probabilidades mecánicas validadas. El prototipo entrega orientación inicial y no reemplaza una revisión técnica.»

## Evidencias que debes conservar

- Pantalla de la cuenta cloud creada y servicio desplegado.
- Vista del repositorio con base de conocimiento y reglas.
- Prueba del diagnóstico desde la web.
- Respuesta del endpoint `/api/conocimiento/hipotesis/S03`.
- Enlace final real publicado por Render.

**Importante:** no afirmar que Azure procesa la consulta si la aplicación se publicó en Render; Azure se menciona como plataforma explorada. No afirmar que se utilizó un servicio de IA preentrenada: el motor de reglas se construyó y desplegó como servicio propio.
