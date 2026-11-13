"""Conexión única a una base MySQL compatible para todas las capas."""
import os
import ssl
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv(Path(__file__).resolve().parent.parent / '.env')
_engine = None


def engine():
    global _engine
    if _engine is None:
        host = os.getenv('MYSQL_HOST', '').strip()
        user = os.getenv('MYSQL_USER', '').strip()
        database = os.getenv('MYSQL_DATABASE', 'motos_experto_nm').strip()
        password = os.getenv('MYSQL_PASSWORD')
        if not host or not user or password is None or not database:
            raise RuntimeError('Falta configurar MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD o MYSQL_DATABASE.')
        port = int(os.getenv('MYSQL_PORT', '3306'))
        ssl_flag = os.getenv('MYSQL_SSL', '1' if os.getenv('RENDER') else '0').lower() in ('1', 'true', 'yes', 'on')
        opts = {'connect_timeout': 15}
        if ssl_flag:
            ca = os.getenv('MYSQL_SSL_CA', '').strip() or None
            if ca and not Path(ca).is_file():
                raise RuntimeError('No se encontró el certificado indicado en MYSQL_SSL_CA.')
            # Se verifican la CA y el nombre del servidor; no se desactiva la verificación TLS.
            opts['ssl'] = ssl.create_default_context(cafile=ca)
        elif os.getenv('RENDER'):
            raise RuntimeError('La conexión externa de Render a MySQL debe usar TLS (MYSQL_SSL=1).')
        url = URL.create('mysql+pymysql', username=user, password=password, host=host, port=port, database=database,
                         query={'charset': 'utf8mb4'})
        _engine = create_engine(url, pool_pre_ping=True, pool_recycle=240, connect_args=opts)
    return _engine
