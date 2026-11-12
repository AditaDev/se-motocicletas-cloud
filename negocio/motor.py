"""Capa de negocio: infiere por hechos consultados; no codifica las 25 fallas en IF/ELIF."""
from collections import defaultdict


class Motor:
    def __init__(self, repo):
        self.repo=repo

    def iniciar(self, categoria):
        if categoria not in self.repo.categorias():
            raise ValueError('Categoría no encontrada en la base de conocimiento.')
        hs=self.repo.hipotesis(categoria)
        if not hs: raise ValueError('La categoría no tiene hipótesis.')
        return {'categoria':categoria,'ruta':categoria,'puntos':{h['codigo']:1 for h in hs},
                'hechos':list(self.comunes(hs)),'terminada':False,'inconclusa':False}

    def comunes(self, hipotesis):
        grupos=[{x['id_hecho'] for x in self.repo.hechos_de(h['id_hipotesis'])} for h in hipotesis]
        return set.intersection(*grupos) if grupos else set()

    def opciones(self, estado):
        if estado['terminada'] or estado['inconclusa']:return []
        candidatos=self.repo.hipotesis(estado['categoria'], estado['ruta'])
        profundidad=len(estado['ruta'].split('>'))
        grupos=defaultdict(list)
        for h in candidatos:
            trozos=h['ruta'].split('>')
            if len(trozos)>profundidad:
                grupos[trozos[profundidad]].append(h)
        antes=self.comunes(candidatos)
        salida=[]
        for codigo, hs in sorted(grupos.items()):
            nuevos=self.comunes(hs)-antes
            if not nuevos: raise ValueError('Inconsistencia de hechos para '+codigo)
            todos=self.repo.hechos_de(hs[0]['id_hipotesis'])
            textos=[f['descripcion'] for f in todos if f['id_hecho'] in nuevos]
            salida.append({'codigo':codigo,'texto':' '.join(textos), 'hechos':sorted(nuevos)})
        return salida

    def responder(self, estado, codigo):
        if estado['terminada'] or estado['inconclusa']:
            raise ValueError('La consulta ya terminó.')
        validas={o['codigo']:o for o in self.opciones(estado)}
        if codigo not in validas: raise ValueError('Opción fuera del recorrido actual.')
        nueva=estado['ruta']+'>'+codigo
        descendientes=self.repo.hipotesis(estado['categoria'],nueva)
        if not descendientes:raise ValueError('La opción carece de hipótesis descendientes.')
        estado['ruta']=nueva
        estado['hechos']=sorted(set(estado['hechos'])|set(validas[codigo]['hechos']))
        for h in descendientes: estado['puntos'][h['codigo']]+=1
        estado['terminada']=any(h['ruta']==nueva for h in descendientes)
        return estado

    def resultado(self, estado):
        if not (estado['terminada'] or estado['inconclusa']):
            raise ValueError('Aún faltan respuestas.')
        if estado['inconclusa']:
            return {'no_concluyente':True, 'mensaje':'No se identifica una falla con las respuestas disponibles.'}
        hs=self.repo.hipotesis(estado['categoria'])
        ganador=next((h for h in hs if h['ruta']==estado['ruta']),None)
        if not ganador:raise ValueError('No existe hoja final para el camino.')
        total=sum(estado['puntos'].values())
        opciones=[]
        for h in hs:
            gr=self.repo.hechos_de(h['id_hipotesis'])
            ids={r['id_hecho'] for r in gr}
            puntos=estado['puntos'][h['codigo']]
            opciones.append({'codigo':h['codigo'], 'nombre':h['nombre'], 'puntos':puntos,
                             'peso':round(puntos/total*100,2) if total else 0,
                             'regla_completa':ids.issubset(set(estado['hechos']))})
        opciones.sort(key=lambda o:(-o['puntos'],o['codigo']))
        codigo=ganador['codigo']
        if opciones[0]['codigo']!=codigo:
            raise ValueError('La puntuación y la hoja obtenida no coinciden.')
        numero=19+int(codigo[1:])
        es_riesgosa=(estado['categoria'] in ('C','F') or codigo in ('S12','S15','S14'))
        return {'no_concluyente':False, 'principal':{'codigo':codigo,'nombre':ganador['nombre'],
                'descripcion':ganador['descripcion'],'recomendacion':ganador['recomendacion'],
                'regla':f'R{numero:02d}'},'candidatas':opciones,
                'granulos':self.repo.granulos(codigo),'ruta':estado['ruta'],
                'advertencia':('Si los síntomas comprometen la seguridad, no conduzcas la motocicleta y busca revisión profesional.' if es_riesgosa else ''),
                'aclaracion':'Los pesos son porcentajes relativos de puntos, NO probabilidades reales de falla.'}
