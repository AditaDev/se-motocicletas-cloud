"""Crea un administrador con credenciales proporcionadas por variables de entorno."""
import getpass
import os
from .usuarios import crear_usuario

if __name__=='__main__':
    nombre=os.environ.get('ADMIN_NOMBRE') or input('Nombre: ').strip()
    correo=os.environ.get('ADMIN_CORREO') or input('Correo: ').strip()
    clave=os.environ.get('ADMIN_CLAVE') or getpass.getpass('Contraseña (mínimo 10 caracteres): ')
    try:
        admin=crear_usuario(nombre,correo,clave,'ADMINISTRADOR')
        print('Administrador creado:',admin['correo'])
    except ValueError as e:
        print('No se creó:',e)
        raise SystemExit(1)
