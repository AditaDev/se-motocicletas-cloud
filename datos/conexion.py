"""Una conexión PostgreSQL para las tres capas del sistema experto."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

load_dotenv(Path(__file__).resolve().parent.parent / '.env')
_engine = None


def engine():
    global _engine
    if _engine is None:
        raw = os.getenv('DATABASE_URL', '').strip()
        if not raw:
            raise RuntimeError('Falta DATABASE_URL: copia la cadena Session Pooler de Supabase en Render.')
        try:
            # Supabase proporciona una URL PostgreSQL; psycopg es el controlador usado por Flask.
            url = make_url(raw).set(drivername='postgresql+psycopg')
        except Exception as exc:
            raise RuntimeError('DATABASE_URL no tiene un formato PostgreSQL válido.') from exc
        if not url.host or not url.database or not url.username:
            raise RuntimeError('DATABASE_URL debe contener host, base de datos y usuario.')
        _engine = create_engine(
            url, pool_pre_ping=True, pool_recycle=180,
            pool_size=3, max_overflow=2, pool_timeout=20,
            connect_args={'sslmode': 'require', 'connect_timeout': 15},
        )
    return _engine
