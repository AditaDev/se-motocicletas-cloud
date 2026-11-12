"""Capa de datos: consultas granulares parametrizadas a MySQL (una sola BD)."""
import json
from pathlib import Path
from sqlalchemy import text
from .conexion import engine

BASE = Path(__file__).resolve().parent / 'recursos'
RULES = json.loads((BASE / 'reglas_79.json').read_text(encoding='utf-8'))

class Repositorio:
    def __init__(self):
        self.consultas = 0

    def consultar(self, sql, parametros=None):
        self.consultas += 1
        with engine().connect() as con:
            return [dict(r) for r in con.execute(text(sql), parametros or {}).mappings()]

    def categorias(self):
        return [r['categoria'] for r in self.consultar(
            'SELECT DISTINCT categoria FROM hipotesis ORDER BY categoria')]

    def hipotesis(self, categoria, prefijo=None):
        if prefijo:
            return self.consultar('SELECT * FROM hipotesis WHERE categoria=:cat AND (ruta=:ruta OR ruta LIKE :patron) ORDER BY codigo',
                                  {'cat': categoria, 'ruta': prefijo, 'patron': prefijo + '>%'} )
        return self.consultar('SELECT * FROM hipotesis WHERE categoria=:cat ORDER BY codigo', {'cat':categoria})

    def hechos_de(self, id_hipotesis):
        return self.consultar('''SELECT f.id_hecho, f.codigo, f.descripcion, i.orden FROM intermedia i
             JOIN hechos f ON f.id_hecho=i.id_hecho
             WHERE i.id_hipotesis=:id ORDER BY i.orden''', {'id':id_hipotesis})

    def granulos(self, codigo):
        return self.consultar('''SELECT h.codigo AS hipotesis, h.nombre AS falla,
             i.orden, f.codigo AS codigo_hecho, f.descripcion AS condicion
             FROM hipotesis h JOIN intermedia i ON h.id_hipotesis=i.id_hipotesis
             JOIN hechos f ON f.id_hecho=i.id_hecho
             WHERE h.codigo=:codigo ORDER BY i.orden''', {'codigo':codigo})

    def resumen(self):
        return {tabla:self.consultar(f'SELECT COUNT(*) AS total FROM {tabla}')[0]['total']
                for tabla in ('hipotesis', 'hechos', 'intermedia')}

    def reglas(self, tipo=None):
        return [r for r in RULES if r['tipo']==tipo] if tipo else RULES
