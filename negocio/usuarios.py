"""Capa de negocio: validación, autenticación y permisos de los usuarios."""
import re
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datos import transaccional as datos

CORREO_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def usuario_publico(row):
    return {k: row[k] for k in ('id_usuario', 'nombre', 'correo', 'rol')} if row else None


def normalizar_correo(valor):
    return str(valor or '').strip().lower()


def crear_usuario(nombre, correo, clave, rol='USUARIO'):
    nombre = str(nombre or '').strip()
    correo = normalizar_correo(correo)
    if not 2 <= len(nombre) <= 120:
        raise ValueError('El nombre debe tener entre 2 y 120 caracteres.')
    if len(correo) > 254 or not CORREO_RE.fullmatch(correo):
        raise ValueError('El correo electrónico no es válido.')
    if not isinstance(clave, str) or not 10 <= len(clave) <= 128:
        raise ValueError('La contraseña debe tener entre 10 y 128 caracteres.')
    if rol not in ('USUARIO', 'ADMINISTRADOR'):
        raise ValueError('Rol inválido.')
    try:
        return usuario_publico(datos.insertar_usuario(nombre, correo,
            generate_password_hash(clave), rol))
    except IntegrityError:
        raise ValueError('El correo electrónico ya está registrado.') from None


def obtener_usuario(uid):
    return usuario_publico(datos.buscar_id(uid))


def autenticar(correo, clave):
    registro = datos.buscar_correo(normalizar_correo(correo))
    if not registro:
        return None, 'Correo o contraseña incorrectos.'
    ahora = datetime.utcnow()
    if registro['bloqueado_hasta'] and registro['bloqueado_hasta'] > ahora:
        return None, 'Demasiados intentos. Inténtalo nuevamente más tarde.'
    if not isinstance(clave, str) or not check_password_hash(registro['clave_hash'], clave):
        n = (registro['intentos_fallidos'] or 0) + 1
        datos.actualizar_acceso(registro['id_usuario'], n if n < 5 else 0,
            ahora + timedelta(minutes=10) if n >= 5 else None)
        return None, 'Correo o contraseña incorrectos.'
    datos.actualizar_acceso(registro['id_usuario'], 0, None)
    return usuario_publico(registro), None
