# Sistema experto para diagnóstico preliminar de motocicletas

Aplicación Flask en **tres capas**: `presentacion/`, `negocio/` y `datos/`. Usa **una sola base de datos MySQL o TiDB compatible con MySQL** con las tablas `hipotesis`, `hechos`, `intermedia`, `usuario` y `consulta`.

## Estructura

- `app.py`: punto de entrada de Flask y Gunicorn.
- `presentacion/rutas.py`: endpoints REST, sesiones y conexión con la interfaz.
- `presentacion/static/`: HTML, CSS y JavaScript.
- `negocio/motor.py`: inferencia a partir de hechos y rutas de conocimiento.
- `negocio/usuarios.py`: registro, autenticación y validaciones.
- `negocio/consultas.py`: operaciones del historial y consultas.
- `negocio/crear_admin.py`: comando para crear administrador.
- `datos/conexion.py`: conexión única SQLAlchemy / PyMySQL con TLS.
- `datos/esquema.py`: cinco tablas y claves foráneas.
- `datos/repositorio.py`: lectura granular de hipótesis y hechos.
- `datos/transaccional.py`: persistencia de cuentas y resultados.
- `datos/preparacion.py`: creación inicial de tablas y carga del conocimiento.
- `datos/recursos/`: semilla de 25 hipótesis, 37 hechos y 63 relaciones, y catálogo de 79 reglas.
- `datos/migracion.sql`: **solo si** ya tienes una base con tablas transaccionales del modelo antiguo; realizar copia de seguridad antes.

## Despliegue en Render

1. Crea una instancia de MySQL remoto o TiDB Starter con conexión pública y TLS, y una base (`motos_experto_nm`). En TiDB Cloud usa el puerto y nombre de usuario exactos del panel de conexión.
2. Configura las variables en **Render > Environment**: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_SSL=1` y `SECRET_KEY` (una clave aleatoria larga). Opcional: `MYSQL_SSL_CA` con una ruta a la CA suministrada por tu proveedor, si la necesita.
3. En Render configura **Build Command**: `pip install -r requirements.txt`.
4. Configura **Start Command**: `python -m datos.preparacion && gunicorn app:app`.
5. Publica desde GitHub, entra a la URL, registra un usuario e inicia el diagnóstico. La aplicación creará las cinco tablas y cargará los datos **si estaban vacías**.
6. Para crear un administrador, ejecuta `python -m negocio.crear_admin` desde un entorno que tenga las mismas variables MySQL; el script solicita nombre, correo y contraseña. No hay administrador por defecto.

Si la base existente tiene un esquema antiguo, el arranque indicará columnas faltantes. Aplica `datos/migracion.sql` **una sola vez** después de hacer una copia de seguridad; no lo ejecutes sobre una instalación nueva.

## Ejecución local

Instala Python y ejecuta en la raíz del proyecto:

```sh
python -m pip install -r requirements.txt
```

Copia `.env.example` como `.env` e introduce los parámetros de la base remota. No subas `.env` a GitHub. Después:

```sh
python -m datos.preparacion
python app.py
```

Abre `http://127.0.0.1:5000`. Para comprobar el funcionamiento como usuario, regístrate, responde una consulta y abre **Mi historial**.

**Seguridad:** las contraseñas se almacenan como hashes; el login valida las credenciales y limita intentos fallidos; el historial está restringido a su dueño y las rutas administrativas exigen rol `ADMINISTRADOR`. Los resultados son orientaciones preliminares, no sustituyen una revisión mecánica.
