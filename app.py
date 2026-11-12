"""Punto de entrada Flask: arquitectura de tres capas."""
import os
from flask import Flask
from presentacion.rutas import bp


def crear_aplicacion():
    aplicacion = Flask(__name__, static_folder='presentacion/static', static_url_path='/static')
    if os.environ.get('RENDER') and not os.environ.get('SECRET_KEY'):
        raise RuntimeError('Define SECRET_KEY en las variables de entorno de Render.')
    aplicacion.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'solo-desarrollo-local-cambia-esta-clave')
    aplicacion.config['SESSION_COOKIE_HTTPONLY'] = True
    aplicacion.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    aplicacion.config['SESSION_COOKIE_SECURE'] = bool(os.environ.get('RENDER'))
    aplicacion.config['PERMANENT_SESSION_LIFETIME'] = 60*60*12
    aplicacion.config['MAX_CONTENT_LENGTH'] = 16*1024
    aplicacion.register_blueprint(bp)
    return aplicacion


app = crear_aplicacion()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False)
