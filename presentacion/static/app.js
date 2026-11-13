'use strict';
const $ = (id) => document.getElementById(id);
const areas = ['autenticacion','inicio', 'preguntas', 'resultados','historial','administracion'];
let csrfToken = '';
let usuarioActual = null;
let modoRegistro = false;
function mostrar(id) { areas.forEach(n => $(n).classList.toggle('oculto', n !== id)); window.scrollTo({top:0,behavior:'smooth'}); }
function error(e) { $('error').textContent = e.message || String(e); $('error').classList.remove('oculto'); }
function limpiarError() { $('error').classList.add('oculto'); }
async function api(ruta, metodo='GET', datos=null) {
  limpiarError();
  const resp = await fetch(ruta, {method:metodo,headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken},credentials:'same-origin',
    ...(datos!==null ? {body:JSON.stringify(datos)} : {})});
  const cuerpo = await resp.text();
  let json;
  try { json = JSON.parse(cuerpo); } catch (_) {
    throw new Error(`El servidor devolvió una respuesta inesperada (HTTP ${resp.status}). Revisa los registros de Render.`);
  }
  if(!resp.ok) throw new Error(json.error || `Error ${resp.status}`);
  return json;
}
function boton(titulo, accion, codigo) {
  const b=document.createElement('button'); b.className='choice';b.type='button';
  const t=document.createElement('span');t.textContent=titulo;b.appendChild(t);
  if(codigo) {const s=document.createElement('small');s.textContent=codigo;b.appendChild(s);}
  b.addEventListener('click',accion);return b;
}
async function inicio() {
  if(!usuarioActual){mostrar('autenticacion');return;}
  try {
    const [categorias,resumen] = await Promise.all([api('/api/categorias'),api('/api/conocimiento/resumen')]);
    const destino=$('categorias');destino.replaceChildren();
    categorias.forEach(cat=>destino.appendChild(boton(cat.nombre,async()=>{
      try {await api('/api/iniciar','POST',{categoria:cat.codigo});await pregunta();}catch(e){error(e);}
    },cat.codigo)));
    const d=resumen.tablas;
    $('contador').textContent=`${d.hipotesis} hipótesis · ${d.hechos} hechos · ${d.intermedia} asociaciones`;
    mostrar('inicio');
  } catch(e) {error(e);}
}
async function pregunta() {
  try{
    const r=await api('/api/pregunta');
    if(r.terminada || r.inconclusa){await resultado();return;}
    $('etapa').textContent=`CATEGORÍA ${r.categoria} · PASO ${r.numero_paso} · RUTA ${r.ruta}`;
    const destino=$('opciones');destino.replaceChildren();
    r.opciones.forEach(o=>destino.appendChild(boton(o.texto,async()=>{
      try {const res=await api('/api/responder','POST',{opcion:o.codigo});if(res.terminada)await resultado();else await pregunta();}catch(e){error(e);}
    },o.codigo)));
    mostrar('preguntas');
  }catch(e){error(e);}
}
function lineaHecho(conector,descripcion) {
  const p=document.createElement('p');const s=document.createElement('span');s.className='keyword';s.textContent=conector;p.appendChild(s);p.appendChild(document.createTextNode(descripcion));return p;
}
async function resultado(){
  try{
    const r=await api('/api/resultado');mostrar('resultados');
    mostrarConfirmacion(r);
    const hallazgo=$('granulos');hallazgo.replaceChildren();
    if(r.no_concluyente) {
      $('resultado_titulo').textContent='Consulta no concluyente';$('resultado_desc').textContent=r.mensaje;
      $('recomendacion').textContent='Solicita una revisión profesional si el síntoma persiste.';
      $('tabla_resultados').replaceChildren();$('alerta').classList.add('oculto');return;
    }
    const h=r.principal;
    $('resultado_titulo').textContent=`${h.codigo} · ${h.nombre}`;
    $('resultado_desc').textContent=h.descripcion;
    $('recomendacion').textContent=h.recomendacion;
    $('alerta').classList.toggle('oculto',!r.advertencia);
    $('alerta').textContent=r.advertencia;
    const tabla=$('tabla_resultados');tabla.replaceChildren();
    r.candidatas.forEach((op,i)=>{
      const div=document.createElement('div');div.className='result-row'+(i===0?' top':'');
      const titulo=document.createElement('div');const nm=document.createElement('div');nm.className='name';nm.textContent=op.codigo+' · '+op.nombre;
      const barra=document.createElement('div');barra.className='bar';const fill=document.createElement('i');fill.style.width=op.peso+'%';barra.appendChild(fill);
      titulo.append(nm,barra);
      const p=document.createElement('div');p.className='score';p.textContent=op.puntos+' pt';
      const por=document.createElement('div');por.className='score';por.textContent=op.peso.toFixed(1)+' %';
      div.append(titulo,p,por);tabla.appendChild(div);
    });
    r.granulos.forEach((g,i)=>hallazgo.appendChild(lineaHecho(i===0?'IF':'AND',g.condicion)));
    hallazgo.appendChild(lineaHecho('THEN',`Seleccionar ${h.codigo} · ${h.nombre} (${h.regla}).`));
    hallazgo.appendChild(lineaHecho('NOTA',r.aclaracion));
  }catch(e){error(e);}
}
async function reiniciar(){try {await api('/api/reiniciar','POST',{});await inicio();}catch(e){error(e);}}
$('no_se').addEventListener('click',async()=>{try{await api('/api/no-se','POST',{});await resultado();}catch(e){error(e);}});
$('reiniciar_pregunta').addEventListener('click',reiniciar);
$('reiniciar_resultado').addEventListener('click',reiniciar);

function vistaAutenticacion(registro=false){
  modoRegistro=registro;
  document.querySelectorAll('.registro-only').forEach(x=>x.classList.toggle('oculto',!registro));
  $('auth_titulo').textContent=registro?'Crear una cuenta':'Iniciar sesión';
  $('auth_enviar').textContent=registro?'Registrarme':'Ingresar';
  $('auth_cambiar').textContent=registro?'Ya tengo cuenta':'Regístrate';
  $('auth_pregunta').textContent=registro?'¿Ya tienes cuenta?':'¿Aún no tienes una cuenta?';
  $('auth_clave').autocomplete=registro?'new-password':'current-password';
  $('auth_nombre').required=registro;
  $('auth_clave').value='';
  mostrar('autenticacion');
}
function cuentaUI(){
  $('usuario_cabecera').textContent=usuarioActual?usuarioActual.nombre+' · '+usuarioActual.rol:'Inicia sesión para continuar';
  $('salir').classList.toggle('oculto',!usuarioActual);
  $('acciones_cuenta').classList.toggle('oculto',!usuarioActual);
  $('ver_admin').classList.toggle('oculto',!usuarioActual || usuarioActual.rol!=='ADMINISTRADOR');
}
$('auth_cambiar').addEventListener('click',()=>vistaAutenticacion(!modoRegistro));
$('auth_form').addEventListener('submit',async(ev)=>{
  ev.preventDefault();
  const datos={correo:$('auth_correo').value,clave:$('auth_clave').value};
  if(modoRegistro)datos.nombre=$('auth_nombre').value;
  try{
    const r=await api(modoRegistro?'/api/auth/registro':'/api/auth/ingresar','POST',datos);
    usuarioActual=r.usuario; csrfToken=r.csrf_token; $('auth_form').reset(); cuentaUI();await inicio();
  }catch(e){error(e);}
});
$('salir').addEventListener('click',async()=>{
  try{await api('/api/auth/salir','POST',{});usuarioActual=null;csrfToken='';
  const r=await api('/api/auth/yo');csrfToken=r.csrf_token;
  cuentaUI();vistaAutenticacion(false);}catch(e){error(e);}
});
$('ver_inicio').addEventListener('click',reiniciar);
$('volver_historial').addEventListener('click',inicio);
$('volver_admin').addEventListener('click',inicio);
$('ver_historial').addEventListener('click',async()=>{
  try{
    const d=await api('/api/historial');
    let cont=$('historial_lista');cont.replaceChildren();
    if(!d.length){cont.textContent='Todavía no has realizado diagnósticos.';}
    for(const c of d){
      let fila=document.createElement('button');fila.type='button';fila.className='history-item';
      fila.textContent=`#${c.id_consulta} · ${c.estado} · ${c.codigo_hipotesis||'Sin conclusión'} · ${new Date(c.fecha).toLocaleString('es-CO')}`;
      fila.addEventListener('click',async()=>{
        try{let detalle=await api('/api/historial/'+c.id_consulta);mostrarDetalleHistorico(detalle);}
        catch(e){error(e);}
      });
      cont.appendChild(fila);
    }
    mostrar('historial');
  }catch(e){error(e);}
});
function mostrarDetalleHistorico(c){
  const r=c.resultado;
  $('resultado_titulo').textContent=r.no_concluyente?'Consulta no concluyente':`${r.principal.codigo} · ${r.principal.nombre}`;
  $('resultado_desc').textContent=r.no_concluyente?r.mensaje:r.principal.descripcion;
  $('recomendacion').textContent=r.no_concluyente?'Consulta con un profesional.':r.principal.recomendacion;
  $('alerta').textContent=r.advertencia||'';$('alerta').classList.toggle('oculto',!r.advertencia);
  const t=$('tabla_resultados');t.replaceChildren();
  (r.candidatas||[]).forEach(op=>{const fila=document.createElement('div');fila.className='result-row';fila.textContent=`${op.codigo} · ${op.nombre} | ${op.puntos} puntos | ${op.peso}%`;t.appendChild(fila);});
  const g=$('granulos');g.replaceChildren();
  (r.granulos||[]).forEach((o,i)=>g.appendChild(lineaHecho(i?'AND':'IF',o.condicion)));
  if(!r.no_concluyente)g.appendChild(lineaHecho('THEN',r.principal.nombre));
  mostrarConfirmacionHistorica(r);
  mostrar('resultados');
}
$('ver_admin').addEventListener('click',async()=>{
  try{
    const [res,users,cons]=await Promise.all([api('/api/admin/resumen'),api('/api/admin/usuarios'),api('/api/admin/consultas')]);
    $('admin_resumen').textContent=`${res.usuarios} usuarios · ${res.consultas} consultas · ${res.finalizadas} finalizadas`;
    $('admin_usuarios').replaceChildren();$('admin_consultas').replaceChildren();
    users.forEach(u=>{let p=document.createElement('p');p.textContent=`${u.nombre} · ${u.correo} · ${u.rol}`;$('admin_usuarios').appendChild(p);});
    cons.forEach(c=>{let p=document.createElement('p');p.textContent=`#${c.id_consulta} · ${c.nombre} · ${c.codigo_hipotesis||'No concluyente'} · ${c.estado}`;$('admin_consultas').appendChild(p);});
    mostrar('administracion');
  }catch(e){error(e);}
});

// Confirmación final: se guarda exclusivamente después de que el usuario elige.
function mostrarConfirmacion(r) {
  const bloque=$('confirmacion_bloque');
  const guardada=$('seleccion_guardada');
  const volver=$('volver_desde_resultado');
  $('opciones_confirmacion').replaceChildren();
  guardada.classList.add('oculto');
  if(r.confirmada){
    bloque.classList.add('oculto');
    volver.classList.add('oculto');
    renderSeleccion(r.seleccion_usuario);
    return;
  }
  // Solo permitir confirmar hipótesis existentes. Si la consulta no es
  // concluyente, se puede retroceder o iniciar otra sin guardar una elección ficticia.
  bloque.classList.toggle('oculto', Boolean(r.no_concluyente));
  volver.classList.toggle('oculto', !r.puede_retroceder);
  if (r.no_concluyente) return;
  const candidatas = r.candidatas;
  candidatas.forEach(op=>{
    const label=document.createElement('label');label.className='opcion-confirmacion';
    const input=document.createElement('input');input.type='radio';input.name='hipotesis_confirmada';input.value=op.codigo;input.required=true;
    const span=document.createElement('span');
    const titulo=document.createElement('strong');titulo.textContent=`${op.codigo} · ${op.nombre} (${op.puntos} puntos; peso ${Number(op.peso).toFixed(1)} %)`;
    const descripcion=document.createElement('small');descripcion.textContent=op.descripcion||'';descripcion.className='descripcion-hyp';
    span.append(titulo,descripcion);
    label.append(input,span);$('opciones_confirmacion').appendChild(label);
  });
}
function renderSeleccion(seleccion){
  if(!seleccion)return;
  const cont=$('seleccion_guardada');
  cont.textContent=`Selección registrada: ${seleccion.codigo ? seleccion.codigo+' · ' : ''}${seleccion.nombre}. La elección no reemplaza la revisión profesional.`;
  cont.classList.remove('oculto');
}
function mostrarConfirmacionHistorica(r){
  $('confirmacion_bloque').classList.add('oculto');
  $('volver_desde_resultado').classList.add('oculto');
  $('seleccion_guardada').classList.add('oculto');
  if(r.seleccion_usuario)renderSeleccion(r.seleccion_usuario);
}
async function volverPregunta(){
  try {
    const res=await api('/api/retroceder','POST',{});
    if(res.inicio)await inicio();else await pregunta();
  }catch(e){error(e);}
}
$('volver_pregunta').addEventListener('click',volverPregunta);
$('volver_desde_resultado').addEventListener('click',volverPregunta);
$('confirmacion_form').addEventListener('submit',async(ev)=>{
  ev.preventDefault();
  const opcion=document.querySelector('input[name="hipotesis_confirmada"]:checked');
  if(!opcion){error(new Error('Selecciona una opción antes de guardar.'));return;}
  const enviar=$('confirmar_seleccion');enviar.disabled=true;
  try {
    const res=await api('/api/confirmar','POST',{codigo:opcion.value});
    $('confirmacion_bloque').classList.add('oculto');
    $('volver_desde_resultado').classList.add('oculto');
    renderSeleccion(res.seleccion_usuario);
  }catch(e){error(e);}finally{enviar.disabled=false;}
});

async function arrancar(){
  try{
    const r=await api('/api/auth/yo');csrfToken=r.csrf_token;
    usuarioActual=r.usuario;cuentaUI();
    if(usuarioActual)await inicio();else vistaAutenticacion();
  }catch(e){error(e);}
}
arrancar();
