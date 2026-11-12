"""Crea las 5 tablas MySQL y carga las 25 hipótesis/37 hechos/63 vínculos, sin borrar datos."""
import json
from pathlib import Path
from sqlalchemy import inspect, select, func
from .conexion import engine
from .esquema import metadata, hipotesis, hechos, intermedia, usuario, consulta

BASE=Path(__file__).resolve().parent / 'recursos'
TABLES={'hipotesis':hipotesis,'hechos':hechos,'intermedia':intermedia,
        'usuario':usuario,'consulta':consulta}


def preparar():
    e=engine()
    with e.begin() as con:
        metadata.create_all(con)
        insp=inspect(con)
        for nombre,t in TABLES.items():
            reales={c['name'] for c in insp.get_columns(nombre)}
            faltantes=set(t.c.keys())-reales
            if faltantes:
                raise RuntimeError(f'La tabla {nombre} es del modelo anterior; faltan {sorted(faltantes)}. '
                       'Aplica primero datos/migracion.sql y reinicia.')
        seed=json.loads((BASE/'semilla_conocimiento.json').read_text(encoding='utf-8'))
        counts={name:con.scalar(select(func.count()).select_from(TABLES[name]))
                for name in ('hipotesis','hechos','intermedia')}
        if all(v==0 for v in counts.values()):
            for name in ('hipotesis','hechos','intermedia'):
                con.execute(TABLES[name].insert(),seed[name])
            print('Conocimiento cargado en MySQL: 25 hipótesis, 37 hechos y 63 relaciones.')
        elif counts == {'hipotesis':25,'hechos':37,'intermedia':63}:
            # Los IDs y las rutas son claves para la navegación de las 25 hojas.
            local_h={(r['id_hipotesis'],r['codigo'],r['ruta']) for r in seed['hipotesis']}
            db_h={(r.id_hipotesis,r.codigo,r.ruta) for r in con.execute(select(
                hipotesis.c.id_hipotesis,hipotesis.c.codigo,hipotesis.c.ruta))}
            local_f={(r['id_hecho'],r['codigo']) for r in seed['hechos']}
            db_f={(r.id_hecho,r.codigo) for r in con.execute(select(
                hechos.c.id_hecho,hechos.c.codigo))}
            local_i={(r['id_hipotesis'],r['id_hecho'],r['orden']) for r in seed['intermedia']}
            db_i={(r.id_hipotesis,r.id_hecho,r.orden) for r in con.execute(select(
                intermedia.c.id_hipotesis,intermedia.c.id_hecho,intermedia.c.orden))}
            if (local_h,local_f,local_i)!=(db_h,db_f,db_i):
                raise RuntimeError('La base existente tiene 25/37/63 registros pero difiere del árbol documentado. '
                                   'Revisa los datos sin borrarlos.')
            print('Base de conocimiento verificada: 25 / 37 / 63. Sin sobrescribir datos.')
        else:
            raise RuntimeError(f'Conocimiento incompleto: {counts}. No se modificó el contenido existente.')
        print('Tablas listas: hipotesis, hechos, intermedia, usuario, consulta.')

if __name__=='__main__':
    preparar()
