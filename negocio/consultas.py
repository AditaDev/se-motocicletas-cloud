"""Capa de negocio: gestión de consultas e historial del sistema experto."""
from datos import transaccional as repo


def guardar_consulta(uid, estado, resultado):
    return repo.guardar_consulta(uid, estado, resultado)


def listar_consultas(uid=None):
    return repo.listar_consultas(uid)


def detalle_consulta(id_consulta, uid=None):
    return repo.detalle_consulta(id_consulta, uid)


def listar_usuarios():
    return repo.listar_usuarios()


def estadisticas():
    return repo.estadisticas()
