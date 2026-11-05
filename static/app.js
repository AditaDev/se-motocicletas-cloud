'use strict';
const $ = (id) => document.getElementById(id);
const areas = ['inicio', 'preguntas', 'resultados'];
function mostrar(id) { areas.forEach(n => $(n).classList.toggle('oculto', n !== id)); window.scrollTo({top:0,behavior:'smooth'}); }
function error(e) { $('error').textContent = e.message || String(e); $('error').classList.remove('oculto'); }
function limpiarError() { $('error').classList.add('oculto'); }
async function api(ruta, metodo='GET', datos=null) {
  limpiarError();
  const resp = await fetch(ruta, {method:metodo,headers:{'Content-Type':'application/json'},credentials:'same-origin',
    ...(datos!==null ? {body:JSON.stringify(datos)} : {})});
  const json = await resp.json();
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
inicio();
