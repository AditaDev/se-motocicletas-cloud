"""Capa de presentación / controlador API REST para desplegar en Render."""
import os
import secrets
import uuid
from functools import wraps
from negocio.usuarios import crear_usuario, obtener_usuario, autenticar
from negocio.consultas import (guardar_consulta, listar_consultas, detalle_consulta,
                               listar_usuarios, estadisticas)
from flask import Blueprint, request, session, jsonify, send_from_directory, current_app
from datos.repositorio import Repositorio
from negocio.motor import Motor

bp = Blueprint('interfaz_y_api', __name__)

NOMBRES={
 'A':'Problemas de arranque', 'B':'Funcionamiento del motor',
 'C':'Sobrecalentamiento', 'D':'Ruidos y vibraciones',
 'E':'Transmisión', 'F':'Frenos, dirección y estabilidad',
 'G':'Sistema eléctrico y electrónico'
}

def require_login(fn):
    @wraps(fn)
    def interno(*args, **kwargs):
        if not usuario_actual():return salida_error('Debes iniciar sesión.',401)
        return fn(*args,**kwargs)
    return interno

def require_admin(fn):
    @wraps(fn)
    def interno(*args, **kwargs):
        u=usuario_actual()
        if not u:return salida_error('Debes iniciar sesión.',401)
        if u['rol']!='ADMINISTRADOR':return salida_error('No tienes permisos de administrador.',403)
        return fn(*args,**kwargs)
    return interno

def usuario_actual():
    return obtener_usuario(session.get('id_usuario'))

@bp.before_app_request
def proteccion_mutaciones():
    if request.method in ('POST','PUT','PATCH','DELETE'):
        if not session.get('csrf_token') or not secrets.compare_digest(
                str(request.headers.get('X-CSRF-Token','')),str(session['csrf_token'])):
            return salida_error('Solicitud no autorizada (CSRF). Recarga la página.',403)

@bp.get('/api/auth/yo')
def yo():
    if 'csrf_token' not in session:session['csrf_token']=secrets.token_urlsafe(32)
    return jsonify({'usuario':usuario_actual(),'csrf_token':session['csrf_token']})

@bp.post('/api/auth/registro')
def registro():
    data=request.get_json(silent=True) or {}
    try:
        u=crear_usuario(data.get('nombre'),data.get('correo'),data.get('clave'))
    except ValueError as exc:return salida_error(str(exc))
    session.clear()
    session['id_usuario']=u['id_usuario']
    session['csrf_token']=secrets.token_urlsafe(32)
    session.permanent=True
    return jsonify({'usuario':u,'csrf_token':session['csrf_token']}),201

@bp.post('/api/auth/ingresar')
def ingresar():
    data=request.get_json(silent=True) or {}
    u,mensaje=autenticar(data.get('correo'),data.get('clave'))
    if not u:return salida_error(mensaje,401)
    session.clear()
    session['id_usuario']=u['id_usuario']
    session['csrf_token']=secrets.token_urlsafe(32)
    session.permanent=True
    return jsonify({'usuario':u,'csrf_token':session['csrf_token']})

@bp.post('/api/auth/salir')
@require_login
def salir():
    session.clear()
    return jsonify({'ok':True})

@bp.get('/api/historial')
@require_login
def historial():
    return jsonify(listar_consultas(usuario_actual()['id_usuario']))

@bp.get('/api/historial/<int:id_consulta>')
@require_login
def historial_detalle(id_consulta):
    d=detalle_consulta(id_consulta,usuario_actual()['id_usuario'])
    return jsonify(d) if d else salida_error('Registro no encontrado.',404)

@bp.get('/api/admin/resumen')
@require_admin
def admin_resumen():
    return jsonify(estadisticas())

@bp.get('/api/admin/usuarios')
@require_admin
def admin_usuarios():
    return jsonify(listar_usuarios())

@bp.get('/api/admin/consultas')
@require_admin
def admin_consultas():
    return jsonify(listar_consultas())

def componentes():
    r=Repositorio()
    return r,Motor(r)

def salida_error(texto,status=400):
    return jsonify({'error':texto}),status

@bp.get('/')
def inicio():
    return send_from_directory(current_app.static_folder,'index.html')

@bp.get('/api/salud')
def salud():
    r,_=componentes()
    return jsonify({'estado':'ok','datos':r.resumen(),'reglas':len(r.reglas()),'servicio':'Sistema experto motocicletas'})

@bp.get('/api/categorias')
def categorias():
    r,_=componentes()
    return jsonify([{'codigo':c,'nombre':NOMBRES[c]} for c in r.categorias()])

@bp.post('/api/iniciar')
@require_login
def iniciar():
    dato=request.get_json(silent=True) or {}
    cat=str(dato.get('categoria','')).upper().strip()
    _,m=componentes()
    try:
        estado=m.iniciar(cat)
        estado['token_consulta']=str(uuid.uuid4())
        estado['pasos_anteriores']=[]
        estado['confirmada']=False
        session['estado']=estado
    except ValueError as e:return salida_error(str(e))
    return jsonify({'ok':True,'categoria':cat})

@bp.get('/api/pregunta')
@require_login
def pregunta():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    _,m=componentes()
    try:ops=m.opciones(estado)
    except ValueError as e:return salida_error(str(e))
    return jsonify({'categoria':estado['categoria'],'ruta':estado['ruta'],
                   'numero_paso':len(estado['ruta'].split('>')),
                   'opciones':[{'codigo':o['codigo'],'texto':o['texto']} for o in ops],
                   'terminada':estado['terminada'],'inconclusa':estado['inconclusa'],
                   'puede_retroceder':True})

@bp.post('/api/responder')
@require_login
def responder():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    dato=request.get_json(silent=True) or {}
    codigo=str(dato.get('opcion','')).strip()
    _,m=componentes()
    try:
        anterior=copia_paso(estado)
        m.responder(estado,codigo)
        estado.setdefault('pasos_anteriores',[]).append(anterior)
        session['estado']=estado
    except ValueError as e:return salida_error(str(e))
    return jsonify({'ok':True,'terminada':estado['terminada']})

@bp.post('/api/no-se')
@require_login
def no_se():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    if estado.get('confirmada') or estado.get('terminada') or estado.get('inconclusa'):
        return salida_error('La consulta ya terminó.',409)
    estado.setdefault('pasos_anteriores',[]).append(copia_paso(estado))
    estado['inconclusa']=True
    session['estado']=estado
    return jsonify({'ok':True})

@bp.get('/api/resultado')
@require_login
def resultado():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    _,m=componentes()
    try:
        r=m.resultado(estado)
        r['puede_retroceder']=not estado.get('confirmada', False)
        r['confirmada']=estado.get('confirmada', False)
        if estado.get('seleccion_usuario'):
            r['seleccion_usuario']=estado['seleccion_usuario']
        return jsonify(r)
    except ValueError as e:return salida_error(str(e))

@bp.get('/api/conocimiento/resumen')
def resumen():
    r,_=componentes()
    return jsonify({'tablas':r.resumen(),'reglas':79,
                    'tipos':{t:len(r.reglas(t)) for t in ('clasificacion','navegacion','diagnostico','recomendacion','control','seguridad')}})

@bp.get('/api/conocimiento/hipotesis/<codigo>')
def granulos(codigo):
    r,_=componentes();codigo=codigo.upper()
    filas=r.granulos(codigo)
    if not filas:return salida_error('Hipótesis no encontrada.',404)
    regla=next((x for x in r.reglas('diagnostico') if x['codigo']==f'R{19+int(codigo[1:]):02d}'),None)
    return jsonify({'hipotesis':codigo,'regla':regla,'hechos':filas})

@bp.get('/api/conocimiento/reglas')
def reglas():
    r,_=componentes();tipo=request.args.get('tipo')
    return jsonify(r.reglas(tipo))

@bp.post('/api/reiniciar')
@require_login
def reiniciar():
    session.pop('estado',None)
    return jsonify({'ok':True})




def copia_paso(estado):
    """Memoria de trabajo reversible: evita sumar dos veces puntos al corregir respuestas."""
    return {
        'ruta': estado['ruta'],
        'puntos': dict(estado['puntos']),
        'hechos': list(estado['hechos']),
        'terminada': estado['terminada'],
        'inconclusa': estado['inconclusa'],
    }


@bp.post('/api/retroceder')
@require_login
def retroceder():
    estado = session.get('estado')
    if not estado:
        return salida_error('No hay consulta activa.',404)
    if estado.get('confirmada'):
        return salida_error('Esta consulta ya fue registrada. Inicia una nueva para cambiar respuestas.',409)
    anteriores = estado.get('pasos_anteriores',[])
    if not anteriores:
        session.pop('estado',None)
        return jsonify({'ok':True,'inicio':True})
    anterior = anteriores.pop()
    estado.update(anterior)
    session['estado']=estado
    return jsonify({'ok':True,'inicio':False,'ruta':estado['ruta']})


@bp.post('/api/confirmar')
@require_login
def confirmar_resultado():
    """Almacena la elección del usuario SIN modificar la inferencia calculada."""
    estado = session.get('estado')
    if not estado:
        return salida_error('No hay consulta activa.',404)
    if estado.get('confirmada'):
        return salida_error('La selección ya fue registrada.',409)
    _, motor = componentes()
    try:
        r = motor.resultado(estado)
    except ValueError as exc:
        return salida_error(str(exc))
    payload = request.get_json(silent=True) or {}
    codigo = str(payload.get('codigo','')).strip().upper()
    if r['no_concluyente']:
        return salida_error('No hay hipótesis disponibles para seleccionar. Regresa a una pregunta o inicia otro diagnóstico.',409)
    opciones = {c['codigo']:c for c in r['candidatas']}
    if codigo not in opciones:
        return salida_error('Selecciona una de las hipótesis mostradas.')
    elegida = opciones[codigo]
    seleccion = {
        'codigo':codigo, 'nombre':elegida['nombre'],
        'tipo':'REPORTADA_POR_USUARIO',
        'nota':'Elección orientativa del usuario; no equivale a una comprobación técnica.'
    }
    r['seleccion_usuario'] = seleccion
    # El id_hipotesis persistido indica la opción reportada por el usuario;
    # resultado_json conserva la principal y la puntuación original del motor.
    guardar_consulta(usuario_actual()['id_usuario'],estado,r)
    estado['confirmada']=True
    estado['seleccion_usuario']=seleccion
    session['estado']=estado
    return jsonify({'ok':True,'seleccion_usuario':seleccion,
                    'mensaje':'Tu selección fue guardada en Mi historial.'})
