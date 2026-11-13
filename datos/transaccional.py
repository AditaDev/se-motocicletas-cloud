"""Capa de datos: persistencia de cuentas e historial en la única base compatible con MySQL."""
import json
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.dialects.mysql import insert as mysql_insert
from .conexion import engine
from .esquema import usuario, consulta, hipotesis


def buscar_correo(correo):
    with engine().connect() as con:
        return con.execute(select(usuario).where(usuario.c.correo == correo)).mappings().first()


def buscar_id(uid):
    if not isinstance(uid, int):
        return None
    with engine().connect() as con:
        return con.execute(select(usuario).where(usuario.c.id_usuario == uid)).mappings().first()


def insertar_usuario(nombre, correo, clave_hash, rol):
    with engine().begin() as con:
        r = con.execute(usuario.insert().values(nombre=nombre, correo=correo,
            clave_hash=clave_hash, rol=rol, intentos_fallidos=0, fecha_registro=datetime.utcnow()))
        return con.execute(select(usuario).where(
            usuario.c.id_usuario == r.inserted_primary_key[0])).mappings().first()


def actualizar_acceso(uid, intentos, bloqueado_hasta):
    with engine().begin() as con:
        con.execute(usuario.update().where(usuario.c.id_usuario == uid).values(
            intentos_fallidos=intentos, bloqueado_hasta=bloqueado_hasta))


def guardar_consulta(uid, estado, resultado):
    seleccion = resultado.get('seleccion_usuario')
    codigo = seleccion.get('codigo') if seleccion else (
        None if resultado['no_concluyente'] else resultado['principal']['codigo'])
    with engine().begin() as con:
        id_hip = None
        if codigo:
            id_hip = con.scalar(select(hipotesis.c.id_hipotesis).where(hipotesis.c.codigo == codigo))
            if id_hip is None:
                raise ValueError('La hipótesis ya no existe en la base de conocimiento.')
        valores = {
            'id_usuario': uid, 'id_hipotesis': id_hip,
            'token_consulta': estado['token_consulta'], 'categoria': estado['categoria'],
            'ruta_elegida': estado['ruta'],
            'estado': ('NO_CONCLUYENTE' if resultado['no_concluyente'] else 'FINALIZADA'),
            'resultado_json': json.dumps(resultado, ensure_ascii=False),
            'fecha': datetime.utcnow(),
        }
        # UNIQUE token_consulta evita duplicar diagnósticos al recargar los resultados.
        stmt = mysql_insert(consulta).values(**valores)
        con.execute(stmt.on_duplicate_key_update(id_consulta=consulta.c.id_consulta))


def serializar(d):
    return {k: (v.isoformat(timespec='seconds')+'Z' if isinstance(v, datetime) else v)
            for k,v in d.items()}


def listar_consultas(uid=None, limite=100):
    q = select(consulta.c.id_consulta, consulta.c.id_usuario,
        hipotesis.c.codigo.label('codigo_hipotesis'), consulta.c.categoria,
        consulta.c.ruta_elegida, consulta.c.estado, consulta.c.fecha,
        usuario.c.nombre, usuario.c.correo).select_from(
        consulta.join(usuario, usuario.c.id_usuario == consulta.c.id_usuario)
            .outerjoin(hipotesis, hipotesis.c.id_hipotesis == consulta.c.id_hipotesis))
    if uid is not None:
        q = q.where(consulta.c.id_usuario == uid)
    q = q.order_by(consulta.c.id_consulta.desc()).limit(limite)
    with engine().connect() as con:
        return [serializar(dict(r)) for r in con.execute(q).mappings().all()]


def detalle_consulta(id_consulta, uid=None):
    q = select(consulta).where(consulta.c.id_consulta == id_consulta)
    if uid is not None:
        q = q.where(consulta.c.id_usuario == uid)
    with engine().connect() as con:
        r = con.execute(q).mappings().first()
        if not r:
            return None
        d = serializar(dict(r))
        d['resultado'] = (json.loads(d.pop('resultado_json')) if d.get('resultado_json') else
            {'no_concluyente': True,
             'mensaje': 'Registro anterior sin detalle histórico de puntuación.'})
        return d


def listar_usuarios():
    q = select(usuario.c.id_usuario, usuario.c.nombre, usuario.c.correo, usuario.c.rol,
        usuario.c.fecha_registro).order_by(usuario.c.id_usuario.desc()).limit(250)
    with engine().connect() as con:
        return [serializar(dict(r)) for r in con.execute(q).mappings().all()]


def estadisticas():
    with engine().connect() as con:
        return {'usuarios': con.scalar(select(func.count()).select_from(usuario)),
                'consultas': con.scalar(select(func.count()).select_from(consulta)),
                'finalizadas': con.scalar(select(func.count()).select_from(consulta).where(
                    consulta.c.estado == 'FINALIZADA'))}
