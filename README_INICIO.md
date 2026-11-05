# Sistema experto de motocicletas en la nube

Proyecto académico listo para subir a **Render Web Service**. Usa Flask (Python) como API REST y HTML/CSS/JavaScript como interfaz. La base de conocimiento se almacena en `data/conocimiento.sqlite3` con la **misma estructura normalizada y los mismos datos** de `hipotesis` (25 registros), `hechos` (37) e `intermedia` (63 relaciones) que la base MySQL de clase. El archivo `data/reglas_79.json` conserva el catálogo de 79 reglas IF–AND–THEN.

## Qué se reutilizó y qué cambió

- Se conservan las 7 categorías, 25 posibles fallas y puntuación por ramas, sin cruces entre categorías.
- Para esta práctica cloud se copió la información de las 3 tablas de MySQL a **SQLite de solo lectura**, que se distribuye con el proyecto. No se conecta a tu MySQL local: no hace falta mantener tu computador encendido.
- `reglas_79.json` contiene la descripción de las 79 reglas para consulta y exposición. La inferencia ejecuta las 25 reglas diagnósticas consultando la asociación entre hipótesis y hechos; las restantes reglas de clasificación, navegación, recomendación, control y seguridad están reflejadas en el flujo del servicio y el catálogo documental. **No se afirma que las 79 se interpreten de forma dinámica desde JSON.**
- No se graban cuentas ni historiales de diagnóstico en esta práctica. Cada sesión usa una cookie firmada de Flask. La base cloud es de solo lectura.
- Los porcentajes presentados son **pesos relativos derivados de puntos**, no probabilidades estadísticas de un fallo mecánico.

## Actividad 1: crear cuenta en la plataforma cloud

La guía de clase permite otra plataforma distinta de Azure. **Recomendación:** usar Render porque permite publicar Flask en un Web Service gratuito (con limitaciones).

1. Abre https://render.com/ y pulsa **Get Started** o **Sign Up**.
2. Crea tu cuenta y verifica los datos que te solicite.
3. Vincula tu cuenta de GitHub cuando Render lo pida. No compartas contraseñas ni tokens.
4. Guarda una captura del panel donde aparece tu cuenta y después del servicio publicado.

**Si el docente pide explorar Azure:** visita https://portal.azure.com/ o https://azure.microsoft.com/ ; puedes revisar sus servicios sin tener que crear recursos facturables. Para cuenta de estudiante: https://azure.microsoft.com/free/students/ (verifica los requisitos actuales de la oferta). Azure AI/Foundry reúne IA generativa, agentes, lenguaje, visión y búsqueda. Azure Functions permite publicar lógica propia por HTTP. **No hay que confundir una IA generativa con las reglas deterministas de un sistema experto.**

## Actividad 2: explorar servicios de inteligencia artificial

En https://azure.microsoft.com/en-us/products/category/ai/ observa y explica al menos:

1. **Microsoft Foundry / Foundry Agent Service:** creación y gestión de aplicaciones/agentes de IA.
2. **Azure AI Language:** procesamiento de lenguaje natural.
3. **Azure AI Search:** recuperación de conocimiento mediante búsqueda.
4. **Azure Machine Learning:** desarrollo y despliegue de modelos predictivos.
5. **Azure Functions:** no es IA preentrenada, es una opción serverless para publicar un motor de inferencia por HTTP.

**Elección implementada:** Render Web Service. Render es una plataforma de hosting, **no un servicio especializado de sistemas expertos**. Lo que se publica allí es **nuestro motor de inferencia como servicio REST**. Si tu profesor exige específicamente un producto de IA preconstruido de un proveedor cloud, explícale esta diferencia antes de entregar.

## Actividad 3: publicar el sistema en Render (sin programar más)

### A. Preparar repositorio GitHub

1. Descomprime el ZIP del proyecto.
2. En https://github.com/ inicia sesión y selecciona **New repository**.
3. Nómbralo `se-motocicletas-cloud`. Puede ser público para la práctica, pero NO subas contraseñas ni claves.
4. En el repositorio, selecciona **Add file > Upload files** y sube **el contenido** de la carpeta del proyecto, conservando estas rutas en la raíz:

```
se-motocicletas-cloud/
  app.py
  motor.py
  repositorio.py
  requirements.txt
  render.yaml
  data/conocimiento.sqlite3
  data/reglas_79.json
  static/index.html
  static/app.js
  static/estilos.css
  README_INICIO.md
  GUION_VIDEO.md
```

5. Confirma los archivos mediante **Commit changes**. Comprueba que `app.py` aparece en la raíz y que `data/` y `static/` contienen sus archivos.

### B. Crear el Web Service

1. Entra a https://dashboard.render.com/.
2. Haz clic en **New > Web Service**.
3. Autoriza el acceso a GitHub y selecciona el repositorio `se-motocicletas-cloud`.
4. Configura **Language: Python 3** (o Runtime: Python), **Branch: main**, **Plan/Instance type: Free**.
5. Completa los comandos:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. En **Environment**, agrega una variable de entorno `SECRET_KEY` con una cadena larga aleatoria. Desde Python local puedes generar una con `python -c "import secrets; print(secrets.token_hex(32))"`. No la copies a GitHub.
7. Presiona **Create Web Service** / **Deploy Web Service**. Render instalará las dependencias y publicará la aplicación.
8. En la sección de Logs comprueba mensajes de inicio correctos. El servicio tendrá una dirección como `https://<nombre-asignado>.onrender.com/` (Render te mostrará la dirección exacta).

No necesitas subir archivos SQL a phpMyAdmin ni configurar una conexión MySQL remota para esta práctica: la base de conocimiento está contenida en `data/conocimiento.sqlite3`.

> Plan gratuito: Render suspende el servicio después de un periodo sin tráfico. La siguiente visita puede tardar en cargar. Los cambios locales no persisten entre reinicios, por eso la base de conocimiento **se incluye como archivo de lectura en el repositorio**. Los datos se conservan mientras estén en el repositorio. No es una solución productiva.

### C. Verificar la aplicación y el API

En la URL que te dé Render, abre:

- `/` — Interfaz para hacer un diagnóstico.
- `/api/salud` — Debe indicar 25 hipótesis, 37 hechos, 63 asociaciones y 79 reglas.
- `/api/categorias` — Devuelve las siete categorías.
- `/api/conocimiento/resumen` — Resumen de reglas por tipo y tablas.
- `/api/conocimiento/hipotesis/S03` — Gránulos IF/AND de la hipótesis S03, y su regla R22.
- `/api/conocimiento/reglas?tipo=diagnostico` — Catálogo de reglas de diagnóstico.

**Recorrido para mostrar en video:** categoría A (arranque) → opción `A1-N` (motor no gira) → opción `A2-2` (luces normales y un clic). Deberás obtener S03 (motor de arranque/relé) con 3 puntos y 37,50 % de peso relativo; S01 y S02 con 2 puntos cada una; S04 con 1 punto. Es una puntuación por el camino, **no una probabilidad real de diagnóstico**.

### D. Probar antes de publicarlo (opcional)

En la carpeta donde se encuentra `app.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre `http://127.0.0.1:5000`. La práctica publicada en Render **no requiere** que mantengas este servidor local encendido.

## Actividad 4: grabar el video

Consulta `GUION_VIDEO.md` para un guion de unos 4-5 minutos con pantalla, narración, orden de evidencias y advertencias sobre el uso académico. Graba tu propia cuenta y aplicación; no grabes credenciales, contraseñas ni la clave `SECRET_KEY`.

## Solución de errores comunes

- **Build failed / ModuleNotFoundError:** comprueba que `requirements.txt` esté en la raíz y que Build Command sea `pip install -r requirements.txt`.
- **Application failed to respond / no web process:** comprueba `gunicorn app:app` y que `app.py` esté en la raíz.
- **No encuentra `conocimiento.sqlite3`:** comprueba que el repositorio contenga `data/conocimiento.sqlite3`, no solo el archivo SQL original de MySQL.
- **Error de cookies o sesión reiniciada:** confirma que `SECRET_KEY` esté configurada con un valor estable en Render.
- **Demora al abrir:** puede estar reactivándose después de un periodo de inactividad del plan Free.
- **Se eligió una respuesta de otra categoría:** el servidor la rechaza para respetar el árbol definido en el proyecto.

## Referencias técnicas

- https://render.com/docs/deploy-flask
- https://render.com/docs/free
- https://render.com/docs/your-first-deploy
- https://azure.microsoft.com/en-us/products/category/ai/
- https://learn.microsoft.com/en-us/azure/architecture/data-guide/technology-choices/ai-services
