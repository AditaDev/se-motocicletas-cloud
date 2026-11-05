"""Capa de datos: consultas granulares sobre la base de conocimiento normalizada."""
import json
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'data' / 'conocimiento.sqlite3'
RULES = json.loads((BASE / 'data' / 'reglas_79.json').read_text(encoding='utf-8'))

class Repositorio:
    def __init__(self):
        self.consultas = 0

    def consultar(self, sql, parametros=()):
        self.consultas += 1
        # Solo lecturas: el archivo se publica junto al código y sobrevive a reinicios.
        con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
        con.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in con.execute(sql, parametros).fetchall()]
        finally:
            con.close()

    def categorias(self):
        return [r['categoria'] for r in self.consultar(
            'SELECT DISTINCT categoria FROM hipotesis ORDER BY categoria')]

    def hipotesis(self, categoria, prefijo=None):
        if prefijo:
            return self.consultar('SELECT * FROM hipotesis WHERE categoria=? AND (ruta=? OR ruta LIKE ?) ORDER BY codigo',
                                  (categoria, prefijo, prefijo+'>%'))
        return self.consultar('SELECT * FROM hipotesis WHERE categoria=? ORDER BY codigo', (categoria,))

    def hechos_de(self, id_hipotesis):
        return self.consultar('''SELECT f.id_hecho, f.codigo, f.descripcion, i.orden FROM intermedia i
                              JOIN hechos f ON f.id_hecho=i.id_hecho
                              WHERE i.id_hipotesis=? ORDER BY i.orden''',(id_hipotesis,))

    def granulos(self, codigo):
        return self.consultar('''SELECT h.codigo AS hipotesis, h.nombre AS falla,
            i.orden, f.codigo AS codigo_hecho, f.descripcion AS condicion
            FROM hipotesis h JOIN intermedia i ON h.id_hipotesis=i.id_hipotesis
            JOIN hechos f ON f.id_hecho=i.id_hecho
            WHERE h.codigo=? ORDER BY i.orden''', (codigo,))

    def resumen(self):
        return {tabla: self.consultar(f'SELECT COUNT(*) AS total FROM {tabla}')[0]['total']
                for tabla in ('hipotesis', 'hechos', 'intermedia')}

    def reglas(self, tipo=None):
        return [r for r in RULES if r['tipo']==tipo] if tipo else RULES
