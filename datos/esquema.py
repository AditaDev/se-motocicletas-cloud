"""Cinco tablas del modelo relacional documentado, compartidas por las tres capas."""
from sqlalchemy import (MetaData, Table, Column, Integer, String, Text, DateTime,
                        ForeignKey, UniqueConstraint, ForeignKeyConstraint, text)

metadata = MetaData()

hipotesis = Table('hipotesis', metadata,
    Column('id_hipotesis', Integer, primary_key=True, autoincrement=True),
    Column('codigo', String(3), nullable=False, unique=True),
    Column('categoria', String(1), nullable=False),
    Column('nombre', String(200), nullable=False),
    Column('ruta', String(40), nullable=False, unique=True),
    Column('descripcion', Text, nullable=False),
    Column('recomendacion', Text, nullable=False),
)

hechos = Table('hechos', metadata,
    Column('id_hecho', Integer, primary_key=True, autoincrement=True),
    Column('codigo', String(3), nullable=False, unique=True),
    Column('descripcion', String(400), nullable=False),
)

intermedia = Table('intermedia', metadata,
    Column('id_hipotesis', Integer, ForeignKey('hipotesis.id_hipotesis'), primary_key=True),
    Column('id_hecho', Integer, ForeignKey('hechos.id_hecho'), primary_key=True),
    Column('orden', Integer, nullable=False),
    UniqueConstraint('id_hipotesis', 'orden', name='uq_orden_por_hipotesis'),
)

usuario = Table('usuario', metadata,
    Column('id_usuario', Integer, primary_key=True, autoincrement=True),
    Column('nombre', String(120), nullable=False),
    Column('correo', String(254), nullable=False, unique=True),
    Column('clave_hash', String(255), nullable=False),
    Column('rol', String(15), nullable=False, server_default='USUARIO'),
    Column('intentos_fallidos', Integer, nullable=False, server_default='0'),
    Column('bloqueado_hasta', DateTime, nullable=True),
    Column('fecha_registro', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
)

consulta = Table('consulta', metadata,
    Column('id_consulta', Integer, primary_key=True, autoincrement=True),
    Column('id_usuario', Integer, ForeignKey('usuario.id_usuario'), nullable=True),
    Column('id_hipotesis', Integer, ForeignKey('hipotesis.id_hipotesis'), nullable=True),
    Column('token_consulta', String(36), nullable=True, unique=True),
    Column('categoria', String(1), nullable=False),
    Column('ruta_elegida', String(40), nullable=False),
    Column('estado', String(20), nullable=False),
    Column('resultado_json', Text, nullable=True),
    Column('fecha', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
)
