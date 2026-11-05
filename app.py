"""Capa de presentación / controlador API REST para desplegar en Render."""
import os
import secrets
from flask import Flask, request, session, jsonify, send_from_directory
from repositorio import Repositorio
from motor import Motor

app=Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY', 'cambia-esta-clave-solo-para-desarrollo')
app.config['SESSION_COOKIE_HTTPONLY']=True
app.config['SESSION_COOKIE_SAMESITE']='Lax'
app.config['MAX_CONTENT_LENGTH']=16*1024

NOMBRES={
 'A':'Problemas de arranque', 'B':'Funcionamiento del motor',
 'C':'Sobrecalentamiento', 'D':'Ruidos y vibraciones',
 'E':'Transmisión', 'F':'Frenos, dirección y estabilidad',
 'G':'Sistema eléctrico y electrónico'
}

def componentes():
    r=Repositorio()
    return r,Motor(r)

def salida_error(texto,status=400):
    return jsonify({'error':texto}),status

@app.get('/')
def inicio():
    return send_from_directory('static','index.html')

@app.get('/api/salud')
def salud():
    r,_=componentes()
    return jsonify({'estado':'ok','datos':r.resumen(),'reglas':len(r.reglas()),'servicio':'Sistema experto motocicletas'})

@app.get('/api/categorias')
def categorias():
    r,_=componentes()
    return jsonify([{'codigo':c,'nombre':NOMBRES[c]} for c in r.categorias()])

@app.post('/api/iniciar')
def iniciar():
    dato=request.get_json(silent=True) or {}
    cat=str(dato.get('categoria','')).upper().strip()
    _,m=componentes()
    try:session['estado']=m.iniciar(cat)
    except ValueError as e:return salida_error(str(e))
    return jsonify({'ok':True,'categoria':cat})

@app.get('/api/pregunta')
def pregunta():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    _,m=componentes()
    try:ops=m.opciones(estado)
    except ValueError as e:return salida_error(str(e))
    return jsonify({'categoria':estado['categoria'],'ruta':estado['ruta'],
                   'numero_paso':len(estado['ruta'].split('>')),
                   'opciones':[{'codigo':o['codigo'],'texto':o['texto']} for o in ops],
                   'terminada':estado['terminada'],'inconclusa':estado['inconclusa']})

@app.post('/api/responder')
def responder():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    dato=request.get_json(silent=True) or {}
    codigo=str(dato.get('opcion','')).strip()
    _,m=componentes()
    try:
        m.responder(estado,codigo)
        session['estado']=estado
    except ValueError as e:return salida_error(str(e))
    return jsonify({'ok':True,'terminada':estado['terminada']})

@app.post('/api/no-se')
def no_se():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    estado['inconclusa']=True
    session['estado']=estado
    return jsonify({'ok':True})

@app.get('/api/resultado')
def resultado():
    estado=session.get('estado')
    if not estado:return salida_error('No hay consulta activa.',404)
    _,m=componentes()
    try:return jsonify(m.resultado(estado))
    except ValueError as e:return salida_error(str(e))

@app.get('/api/conocimiento/resumen')
def resumen():
    r,_=componentes()
    return jsonify({'tablas':r.resumen(),'reglas':79,
                    'tipos':{t:len(r.reglas(t)) for t in ('clasificacion','navegacion','diagnostico','recomendacion','control','seguridad')}})

@app.get('/api/conocimiento/hipotesis/<codigo>')
def granulos(codigo):
    r,_=componentes();codigo=codigo.upper()
    filas=r.granulos(codigo)
    if not filas:return salida_error('Hipótesis no encontrada.',404)
    regla=next((x for x in r.reglas('diagnostico') if x['codigo']==f'R{19+int(codigo[1:]):02d}'),None)
    return jsonify({'hipotesis':codigo,'regla':regla,'hechos':filas})

@app.get('/api/conocimiento/reglas')
def reglas():
    r,_=componentes();tipo=request.args.get('tipo')
    return jsonify(r.reglas(tipo))

@app.post('/api/reiniciar')
def reiniciar():
    session.pop('estado',None)
    return jsonify({'ok':True})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')),debug=False)
