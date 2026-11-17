#!/usr/bin/env python3
"""Genera la pizarra A1, el cuaderno Carta y la vista Markdown desde contenido.json.

Uso, desde la carpeta del tema:
    python3 editables/generar.py .
    python3 editables/generar.py . --privado RUTA/datos_privados.json --salida RUTA/CARPETA

El diseño vive aquí; las explicaciones, cifras y fuentes viven en contenido.json,
fuentes.json y mapa.json. La edición pública no toca datos privados. La edición
privada sustituye las variables con un archivo que no se publica y no modifica
ni el manifiesto ni la vista Markdown.
"""
import argparse
import datetime
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ZONAS = {
    "Z1": "Empieza aquí · La ruta del asunto",
    "Z2": "Puerta de entrada",
    "Z3": "Caducidad",
    "Z4": "Audiencia",
    "Z5": "Las multas",
    "Z6": "Qué pedimos y qué sigue",
    "Z7": "El memorándum",
    "Z8": "Puntos débiles",
}
CAMPOS_CONCEPTO = {"id", "titulo", "apartado", "zona", "pagina", "entradilla", "bloques", "anotar", "sintesis"}
MARCA = re.compile(r"\[([^\]\n]+)\]")
VARIABLE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


class Alto(Exception):
    pass


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def comprobar(c, fuentes, mapa):
    ids_f = {f["id"] for f in fuentes}
    ids_c = [x["id"] for x in c["conceptos"]]
    if len(set(ids_c)) != len(ids_c):
        raise Alto("Conceptos repetidos")
    for x in c["conceptos"]:
        extra = set(x) - CAMPOS_CONCEPTO
        falta = CAMPOS_CONCEPTO - set(x)
        if extra or falta:
            raise Alto(f"{x['id']}: campos no consumidos {sorted(extra)} o faltantes {sorted(falta)}")
        if x["zona"] not in ZONAS:
            raise Alto(f"{x['id']}: zona inexistente {x['zona']}")
        if x["apartado"] != f"{x['id']} · {x['titulo']}":
            raise Alto(f"{x['id']}: apartado distinto del título")
    texto = json.dumps(c, ensure_ascii=False)
    for marca in MARCA.findall(texto):
        for f in re.findall(r"\bF\d+\b", marca):
            if f not in ids_f:
                raise Alto(f"Fuente inexistente {f} en [{marca}]")
    for t in set(VARIABLE.findall(texto)):
        if t not in c["variables"]:
            raise Alto(f"Variable sin valor público: {t}")
    if mapa["tema_id"] != c["id"] or mapa["version"] != c["version"]:
        raise Alto("mapa.json no corresponde al contenido")
    porid = {x["id"]: x for x in c["conceptos"]}
    for m in mapa["conceptos"]:
        x = porid.get(m["id"])
        if not x or x["titulo"] != m["titulo"] or x["apartado"] != m["apartado"]:
            raise Alto(f"mapa.json desactualizado en {m['id']}")
    if {m["id"] for m in mapa["conceptos"]} != set(porid):
        raise Alto("mapa.json no tiene los mismos conceptos")
    for r in mapa["remisiones"]:
        x = porid[r["concepto_id"]]
        if r["paginas_cuaderno"] != [x["pagina"]] or not r["zona_pizarra"].startswith(x["zona"] + " "):
            raise Alto(f"Remisión desactualizada en {x['id']}")
    for r in mapa["relaciones"]:
        if r["desde"] not in porid or r["hacia"] not in porid:
            raise Alto("Relación con concepto inexistente")
    for d in c["defensas"] + c["debiles"]:
        if d["concepto"] not in porid:
            raise Alto("Defensa o punto débil sin concepto")


def sustituir(texto, variables):
    return VARIABLE.sub(lambda m: variables[m.group(1)], texto)


def fuentes_de(concepto):
    vistos = []
    for t in [concepto["entradilla"]] + [b["texto"] for b in concepto["bloques"]]:
        for marca in MARCA.findall(t):
            for f in re.findall(r"\bF\d+\b", marca):
                if f not in vistos:
                    vistos.append(f)
    return sorted(vistos, key=lambda f: int(f[1:]))


def e(t):
    return html.escape(t, quote=False)


def con_refs(t):
    """Escapa y deja las marcas de fuente en estilo de referencia."""
    partes, pos = [], 0
    for m in MARCA.finditer(t):
        partes.append(e(t[pos:m.start()]))
        if re.search(r"\bF\d+\b", m.group(1)):
            partes.append(f'<span class="ref">[{e(m.group(1))}]</span>')
        else:
            partes.append(e(m.group(0)))
        pos = m.end()
    partes.append(e(t[pos:]))
    return "".join(partes)


# ---------------------------------------------------------------- Markdown

def vista_md(c, fuentes, mapa):
    L = [f"# {c['titulo']}", "", f"Tema: {c['id']} · Versión: {c['version']} · Revisión: {c['fecha_revision']}", "",
         c["subtitulo"], "", "## Pregunta y alcance", "", f"**{c['pregunta']}**", "", c["alcance"], "", c["privacidad"], "",
         "## Ruta del asunto", ""]
    L += ["| Fecha | Actuación |", "| --- | --- |"] + [f"| {a} | {b} |" for a, b in c["cronologia"]] + [""]
    L += ["## Desarrollo", ""]
    for x in c["conceptos"]:
        L += [f"### {x['apartado']}", "", f"Zona de la pizarra: {x['zona']} · {ZONAS[x['zona']]}. Página del cuaderno: {x['pagina']}.", "",
              x["entradilla"], ""]
        for b in x["bloques"]:
            L += [f"**{b['subtitulo']}.** {b['texto']}", ""]
        if x["sintesis"]:
            L += ["Síntesis en la pizarra:", ""] + [f"- {s}" for s in x["sintesis"]] + [""]
        L += [f"Para anotar: {x['anotar']}", ""]
    L += ["## Defensas de la Secretaría y respuesta", "", "| Alega | Dónde | Respuesta | Punto | Concepto |", "| --- | --- | --- | --- | --- |"]
    L += [f"| {d['alega']} | {d['donde']} | {d['respuesta']} | {d['punto']} | {d['concepto']} |" for d in c["defensas"]] + [""]
    L += ["## Puntos débiles", "", "| Punto | Por qué es débil | Cómo lo contestamos | Concepto |", "| --- | --- | --- | --- |"]
    L += [f"| {d['punto']} | {d['por_que']} | {d['respuesta']} | {d['concepto']} |" for d in c["debiles"]] + [""]
    L += ["## Lo que el memorándum deja fuera", ""] + [f"- **{d['tema']}.** {d['motivo']}" for d in c["excluidos"]] + [""]
    L += ["## Para repasar", ""] + [f"{i}. {p}" for i, (p, _) in enumerate(c["repaso"], 1)] + ["", "### Respuestas", ""]
    L += [f"{i}. {r}" for i, (_, r) in enumerate(c["repaso"], 1)] + [""]
    L += ["## Correcciones frente a la guía de estudio", ""] + [f"- {d['antes']} Ahora: {d['ahora']} {d['concepto']}." for d in c["correcciones"]] + [""]
    L += ["## Anexo: textos legales", ""]
    for g in c["anexo"]:
        L += [f"### {g['grupo']}", ""]
        for a in g["articulos"]:
            L += [f"**{a['titulo']}.** " + a["texto"].replace("\n", "  \n"), ""]
            if a.get("nota"):
                L += [f"*{a['nota']}*", ""]
    L += ["## Fuentes", ""]
    for f in fuentes:
        L += [f"- **{f['id']}.** {f['titulo']}. {f['autor_institucion']}. {f['fecha_edicion']}. {f['url_o_identificador']}. Consulta: {f['consulta']}. Límites: {f['limites']}"]
    L += ["", "## Relaciones de la pizarra", ""]
    L += [f"- {r['desde']} → {r['hacia']}: {r['relacion']}." for r in mapa["relaciones"]] + [""]
    L += ["## Puntos pendientes", ""] + [f"- {p['descripcion']}" for p in c["pendientes"]] + [""]
    return "\n".join(L)


# ---------------------------------------------------------------- Cuaderno Carta

CSS_CUADERNO = """
@page { size: 215.9mm 279.4mm; margin: 16mm 16mm 18mm 18mm;
  @bottom-left { content: "%(pie)s"; font: 8.5pt Inter; color: #5b6b7f; }
  @bottom-right { content: counter(page); font: 600 9pt Inter; color: #1f4e79; } }
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; color: #1d2733; }
body { font: 11.3pt/1.27 Caladea, serif; width: 181.9mm; }
.hoja { height: 245.4mm; position: relative; break-after: page; overflow: hidden; padding-right: 38mm; }
.hoja::after, .flujo::after { content: ""; position: absolute; top: 14mm; bottom: 0; right: 33mm; border-left: 0.4pt solid #c9d6e3; }
.margen { position: absolute; top: 15mm; right: 0; width: 30mm; font: 7.5pt/1.3 Inter; color: #8a99aa; }
.cinta { font: 600 8.5pt Inter; color: #1f4e79; letter-spacing: .04em; text-transform: uppercase; border-bottom: 1.2pt solid #1f4e79; padding-bottom: 1.5mm; margin-bottom: 5mm; width: calc(100% + 38mm); }
h1 { font: 700 22pt/1.15 Inter; color: #123a5e; margin: 0 0 3mm; }
h2 { font: 700 17pt/1.2 Inter; color: #123a5e; margin: 0 0 3mm; }
h3 { font: 700 11.5pt/1.3 Inter; color: #1f4e79; margin: 3.2mm 0 1mm; }
p { margin: 0 0 2.2mm; }
.entradilla { font-size: 12pt; line-height: 1.3; margin-bottom: 3mm; }
.ref { font: 8.3pt Inter; color: #4a6b8a; white-space: normal; }
.anotar { position: absolute; left: 0; right: 38mm; bottom: 0; border-top: 0.6pt solid #1f4e79; padding-top: 2mm; font: italic 10.5pt Caladea, serif; color: #33475b; }
.anotar .lineas { height: 26mm; background: repeating-linear-gradient(#fff 0 7.6mm, #c9d6e3 7.6mm 7.9mm); margin-top: 1.5mm; }
.contenido { max-height: 229mm; }
.hoja[data-concepto] .contenido { max-height: 200mm; }
.portada { padding-right: 0; }
.portada::after { display: none; }
.portada .cinta { width: 100%; }
table { border-collapse: collapse; width: 100%; font: 9.4pt/1.28 Inter; }
th { text-align: left; color: #fff; background: #1f4e79; padding: 1.4mm 2mm; font-weight: 600; }
td { border-bottom: 0.5pt solid #c9d6e3; padding: 1.4mm 2mm; vertical-align: top; }
td.f { white-space: nowrap; font-weight: 600; color: #123a5e; }
.portada h1 { font-size: 26pt; margin-top: 3mm; margin-bottom: 2mm; }
.portada p, .portada li { font-size: 10.5pt; line-height: 1.25; }
.portada h3 { margin: 2.2mm 0 0.8mm; }
.portada .ficha td { padding: 0.7mm 2mm; font-size: 9pt; }
.portada .sub { font: 12pt/1.35 Inter; color: #3b5068; margin-bottom: 5mm; }
.pregunta { border-left: 2.5mm solid #1f4e79; background: #eef3f8; padding: 3.5mm 5mm; font: 600 13.5pt/1.35 Inter; color: #123a5e; margin-bottom: 4mm; }
.ficha td:first-child { width: 48mm; color: #3b5068; }
.edicion { display: inline-block; font: 600 9pt Inter; color: #fff; background: #1f4e79; padding: 1mm 3mm; border-radius: 1mm; }
ul { margin: 0 0 3mm 5mm; padding: 0; } li { margin-bottom: 1.4mm; }
.flujo { position: relative; padding-right: 38mm; }
.flujo h2 { break-after: avoid; margin-top: 4mm; }
.art { break-inside: avoid-page; margin-bottom: 2.6mm; font-size: 9.8pt; line-height: 1.3; }
.art b { font-family: Inter; font-size: 9.4pt; color: #123a5e; }
.art .nota { font-style: italic; color: #4a5a6b; }
.fuente { font: 9pt/1.35 Inter; margin-bottom: 2.4mm; break-inside: avoid; overflow-wrap: anywhere; }
.repaso li { margin-bottom: 4.5mm; font-size: 11.5pt; }
.repaso.resp li { margin-bottom: 2.2mm; font-size: 10.8pt; }
.dos { columns: 2; column-gap: 7mm; }
"""


def hoja(contenido, cinta, margen="", clase=""):
    return (f'<section class="hoja {clase}"><div class="cinta">{e(cinta)}</div>'
            f'<div class="margen">{margen}</div><div class="fit contenido">{contenido}</div></section>')


def cuaderno_html(c, fuentes, v):
    S = lambda t: sustituir(t, v)
    pie = S(f"{c['id']} · v{c['version']} · {c['fecha_revision']} · {{{{EDICION}}}}").replace('"', "'")
    H = []
    # 1. Portada
    ficha = "".join(f"<tr><td>{e(a)}</td><td>{e(S(b))}</td></tr>" for a, b in c["ficha"])
    uso = "".join(f"<li>{e(u)}</li>" for u in c["como_usar"])
    H.append(f'''<section class="hoja portada"><div class="cinta">Cuaderno de estudio · Carta</div>
      <div class="fit contenido"><span class="edicion">{e(S("{{EDICION}}"))}</span>
      <h1>{e(c["titulo"])}</h1><div class="sub">{e(c["subtitulo"])}</div>
      <div class="pregunta">{e(c["pregunta"])}</div>
      <h3>Alcance</h3><p>{e(c["alcance"])}</p>
      <h3>Cómo usar este cuaderno</h3><ul>{uso}</ul>
      <h3>Ficha del caso</h3><table class="ficha">{ficha}</table>
      <p style="margin-top:3mm;font:9pt Inter;color:#4a5a6b">{e(c["privacidad"])}</p></div></section>''')
    # 2. Cronología
    filas = "".join(f'<tr><td class="f">{e(a)}</td><td>{e(b)}</td></tr>' for a, b in c["cronologia"])
    H.append(hoja(f'<h2>La ruta del asunto en fechas</h2><table><tr><th>Fecha</th><th>Actuación</th></tr>{filas}</table>',
                  "Cronología", "Marca aquí los plazos que tengas que contar."))
    # 3. Conceptos
    for x in c["conceptos"]:
        cuerpo = [f'<h1>{e(x["apartado"])}</h1><p class="entradilla">{con_refs(x["entradilla"])}</p>']
        for b in x["bloques"]:
            cuerpo.append(f'<h3>{e(b["subtitulo"])}</h3><p>{con_refs(b["texto"])}</p>')
        margen = f'Pizarra: {x["zona"]}<br>{e(ZONAS[x["zona"]])}'
        H.append(f'''<section class="hoja" data-concepto="{x["id"]}"><div class="cinta">{e(c["titulo"])}</div>
          <div class="margen">{margen}</div><div class="fit contenido">{"".join(cuerpo)}</div>
          <div class="anotar">{e(x["anotar"])}<div class="lineas"></div></div></section>''')
    # Defensas
    filas = "".join(f'<tr><td>{e(d["alega"])}<br><span class="ref">{e(d["donde"])}</span></td><td>{e(d["respuesta"])}</td>'
                    f'<td class="f">{e(d["punto"])}<br>{d["concepto"]}</td></tr>' for d in c["defensas"])
    H.append(hoja(f'<h2>Defensas de la Secretaría y cómo se contestan</h2><table><tr><th style="width:38%">Lo que alega</th>'
                  f'<th>Respuesta</th><th>En el memo</th></tr>{filas}</table>', "Defensas", "Las páginas son de su contestación."))
    filas = "".join(f'<tr><td class="f">{e(d["punto"])}<br>{d["concepto"]}</td><td>{e(d["por_que"])}</td><td>{e(d["respuesta"])}</td></tr>'
                    for d in c["debiles"])
    H.append(hoja(f'<h2>Puntos débiles</h2><p>Para saberlos, no para decirlos.</p><table><tr><th>Punto</th><th>Por qué es débil</th>'
                  f'<th>Cómo lo contestamos</th></tr>{filas}</table>', "Riesgos"))
    fuera = "".join(f'<h3>{e(d["tema"])}</h3><p>{e(d["motivo"])}</p>' for d in c["excluidos"])
    fuerza = "".join(f"<li>{e(t)}</li>" for t in c["orden_fuerza"])
    H.append(hoja(f'<h2>Lo que el memorándum deja fuera</h2>{fuera}<h2 style="margin-top:6mm">Dos órdenes distintos</h2>'
                  f'<p>Por fuerza para ganar:</p><ol>{fuerza}</ol><p>En el memorándum: competencia, audiencia, caducidad y multas. C13 explica por qué.</p>',
                  "Decisiones del memorándum"))
    preg = "".join(f"<li>{e(p)}</li>" for p, _ in c["repaso"])
    H.append(hoja(f'<h2>Para repasar</h2><p>Contesta sin mirar; las respuestas están en la página siguiente.</p><ol class="repaso">{preg}</ol>', "Repaso"))
    resp = "".join(f"<li>{e(r)}</li>" for _, r in c["repaso"])
    H.append(hoja(f'<h2>Respuestas</h2><ol class="repaso resp">{resp}</ol>', "Repaso"))
    corr = "".join(f'<tr><td>{e(d["antes"])}</td><td>{e(d["ahora"])}</td><td class="f">{d["concepto"]}</td></tr>' for d in c["correcciones"])
    H.append(hoja(f'<h2>Correcciones frente a la guía de estudio</h2><p>La guía se escribió antes de la versión final del memorándum. Esto cambió.</p>'
                  f'<table><tr><th>La guía decía</th><th>Ahora</th><th></th></tr>{corr}</table>', "Correcciones"))
    # Anexo y fuentes, en flujo
    A = ['<section class="flujo"><div class="cinta">Anexo · textos legales</div><h1>Textos legales citados</h1>'
         '<p style="font:9pt Inter;color:#4a5a6b">Copiados de las fuentes F01 a F08; «[…]» marca lo omitido por no aplicar al caso.</p>']
    for g in c["anexo"]:
        A.append(f'<h2>{e(g["grupo"])}</h2>')
        for a in g["articulos"]:
            nota = f'<br><span class="nota">{e(a["nota"])}</span>' if a.get("nota") else ""
            A.append(f'<div class="art"><b>{e(a["titulo"])}.</b> {e(a["texto"]).replace(chr(10), "<br>")}{nota}</div>')
    A.append('<h2 style="break-before:page">Fuentes</h2>')
    for f in fuentes:
        A.append(f'<div class="fuente"><b>{f["id"]}</b> · {e(f["titulo"])}. {e(f["autor_institucion"])}. {e(f["fecha_edicion"])}. '
                 f'{e(f["url_o_identificador"])}. Consulta: {e(f["consulta"])}. Leído: {e(f["alcance_leido"])} Límites: {e(f["limites"])}</div>')
    A.append('<h2>Puntos pendientes</h2><ul>' + "".join(f'<li>{e(p["descripcion"])}</li>' for p in c["pendientes"]) + "</ul></section>")
    H.append("".join(A))
    css = CSS_CUADERNO.replace("%(pie)s", pie)
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(H)}</body></html>'


# ---------------------------------------------------------------- Pizarra A1

CSS_PIZARRA = """
@page { size: 841mm 594mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; }
body { width: 841mm; height: 594mm; position: relative; font-family: Inter; color: #1d2733; overflow: hidden; }
.z { position: absolute; border: 0.9mm solid #1f4e79; border-radius: 3mm; background: #fff; padding: 5mm 6mm 4mm; overflow: hidden; display: flex; flex-direction: column; }
.z.suave { border-color: #8fb0cf; }
.zt { font: 700 30pt/1.1 Inter; color: #123a5e; margin-bottom: 3.5mm; display: flex; align-items: baseline; gap: 4mm; }
.zt .n { font: 700 17pt Inter; color: #fff; background: #1f4e79; border-radius: 2mm; padding: 1mm 3mm; }
.card { border-top: 0.6mm solid #c9d6e3; padding-top: 2.5mm; margin-top: 2.5mm; }
.card:first-of-type { border-top: 0; margin-top: 0; padding-top: 0; }
.ct { font: 700 21pt/1.15 Inter; color: #1f4e79; margin-bottom: 1.5mm; }
.ct .id { color: #fff; background: #1f4e79; font-size: 14pt; padding: 0.6mm 2mm; border-radius: 1.4mm; margin-right: 2mm; vertical-align: 2pt; }
ul { margin: 0; padding: 0; list-style: none; }
li { font: 18pt/1.24 Inter; padding-left: 5mm; position: relative; margin-bottom: 1mm; }
li::before { content: ""; position: absolute; left: 0; top: 3.1mm; width: 2.2mm; height: 2.2mm; background: #1f4e79; border-radius: 50%; }
.refs { font: 14pt/1.25 Inter; color: #4a6b8a; margin-top: 1.2mm; }
.notas { margin-top: auto; border-top: 0.5mm dashed #9fb6cc; padding-top: 1.5mm; font: 14pt Inter; color: #8a99aa; min-height: 18mm; }
header { position: absolute; left: 18mm; top: 14mm; width: 805mm; height: 44mm; }
h1 { font: 800 60pt/1 Inter; color: #123a5e; margin: 0; letter-spacing: -0.5pt; }
.preg { font: 500 24pt/1.25 Inter; color: #1d2733; margin-top: 4mm; width: 560mm; }
.meta { position: absolute; right: 0; top: 0; width: 225mm; font: 14pt/1.35 Inter; color: #3b5068; border-left: 0.6mm solid #1f4e79; padding-left: 4mm; }
.meta b { color: #123a5e; }
.ruta { display: flex; gap: 0; flex: 1; }
.etapa { flex: 1; position: relative; padding: 0 9mm 0 0; }
.etapa + .etapa { padding-left: 7mm; border-left: 0.6mm solid #c9d6e3; }
.et { font: 700 22pt Inter; color: #1f4e79; margin-bottom: 1.5mm; }
.inicio { position: absolute; right: 6mm; top: 5mm; font: 600 15pt Inter; color: #123a5e; background: #eef3f8; padding: 1.5mm 4mm; border-radius: 2mm; max-width: 300mm; }
svg.flechas { position: absolute; left: 0; top: 0; width: 841mm; height: 594mm; pointer-events: none; overflow: visible; }
.et-flecha { position: absolute; font: 600 13pt/1.18 Inter; color: #123a5e; background: #fff; text-align: center; }
.lista2 li { font-size: 17.5pt; }
.pie { position: absolute; left: 18mm; bottom: 6mm; font: 13pt Inter; color: #5b6b7f; width: 805mm; }
"""

# Geometría en mm: x, y, ancho, alto.
ANCHO, HUECO = 181.75, 26
COL = [18 + i * (ANCHO + HUECO) for i in range(4)]
GEOM = {
    "Z1": (18, 58, 805, 90),
    "Z2": (COL[0], 162, ANCHO, 238), "Z3": (COL[1], 162, ANCHO, 238),
    "Z4": (COL[2], 162, ANCHO, 238), "Z5": (COL[3], 162, ANCHO, 238),
    "Z7": (COL[0], 414, ANCHO, 162), "Z6": (COL[1], 414, 2 * ANCHO + HUECO, 162), "Z8": (COL[3], 414, ANCHO, 162),
}


def tarjeta(x):
    items = "".join(f"<li>{e(s)}</li>" for s in x["sintesis"])
    refs = " · ".join(fuentes_de(x))
    return (f'<div class="card"><div class="ct"><span class="id">{x["id"]}</span>{e(x["titulo"])}</div>'
            f'<ul>{items}</ul><div class="refs">{refs} → cuaderno p. {x["pagina"]}</div></div>')


def pizarra_html(c, mapa, v):
    S = lambda t: sustituir(t, v)
    por_zona = {}
    for x in c["conceptos"]:
        por_zona.setdefault(x["zona"], []).append(x)
    B = []
    B.append(f'''<header><h1>{e(c["titulo"])}</h1><div class="preg">{e(c["pregunta"])}</div>
      <div class="meta"><b>{e(S("{{EDICION}}"))}</b><br>{e(c["id"])} · versión {c["version"]} · {c["fecha_revision"]}<br>
      Flecha: relación comprobada en mapa.json<br>F01 a F10: fuentes · p.: página del cuaderno</div></header>''')
    def zona(z, interior, clase=""):
        x, y, w, h = GEOM[z]
        return (f'<div class="z fit {clase}" id="{z}" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm">'
                f'<div class="zt"><span class="n">{z}</span>{e(ZONAS[z])}</div>{interior}</div>')
    c01 = por_zona["Z1"][0]
    etapas = "".join(f'<div class="etapa"><div class="et">{i}. {e(s["etapa"])}</div><ul>'
                     + "".join(f"<li>{e(l)}</li>" for l in s["lineas"]) + "</ul></div>"
                     for i, s in enumerate(c["ruta_lienzo"], 1))
    B.append(zona("Z1", f'<div class="inicio">{e(c["inicio"])}</div><div class="ruta">{etapas}</div>'
                        f'<div class="refs">{" · ".join(fuentes_de(c01))} → cuaderno pp. 2 y {c01["pagina"]}</div>'))
    for z in ("Z2", "Z3", "Z4", "Z5"):
        B.append(zona(z, "".join(tarjeta(x) for x in por_zona[z]) + '<div class="notas">Notas</div>'))
    c12 = por_zona["Z6"][0]
    fuerza = "".join(f"<li>{e(t)}</li>" for t in c["orden_fuerza"])
    B.append(zona("Z6", f'<div style="display:flex;gap:8mm;flex:1"><div style="flex:1;display:flex;flex-direction:column">{tarjeta(c12)}<div class="notas">Notas</div></div>'
                        f'<div style="flex:1"><div class="ct">Orden por fuerza para ganar</div><ul class="lista2">{fuerza}</ul>'
                        f'<div class="refs">El memorándum va en otro orden: ver C13</div></div></div>'))
    c13 = por_zona["Z7"][0]
    defs = "".join(f'<li>{e(d["corta"])} → {e(d["punto"].lower())}</li>' for d in c["defensas"] if d["punto"].startswith("Punto"))
    B.append(zona("Z7", tarjeta(c13) + f'<div class="card"><div class="ct">Defensas y dónde se contestan</div><ul class="lista2">{defs}</ul>'
                        f'<div class="refs">Detalle: cuaderno p. {c13["pagina"] + 1}</div></div>'))
    deb = "".join(f'<li><b>{e(d["punto"])}.</b> {e(d["corta"])}</li>' for d in c["debiles"])
    B.append(zona("Z8", f'<div class="refs" style="margin:-2mm 0 2.5mm">Para saberlos, no para decirlos</div><ul class="lista2">{deb}</ul><div class="refs">Detalle: cuaderno p. {c13["pagina"] + 2}</div>', "suave"))
    B.append(f'<div class="pie">{e(c["privacidad"])} Fuentes completas, textos legales y pendientes: cuaderno, páginas finales.</div>')
    flechas = [r for r in mapa["relaciones"] if r.get("lienzo")]
    zonas_rel = [[next(x["zona"] for x in c["conceptos"] if x["id"] == r["desde"]),
                  next(x["zona"] for x in c["conceptos"] if x["id"] == r["hacia"]), r["etiqueta"]] for r in flechas]
    js = "const REL = " + json.dumps(zonas_rel, ensure_ascii=False) + ";" + JS_FLECHAS
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS_PIZARRA}</style></head><body>{"".join(B)}'
            f'<svg class="flechas" viewBox="0 0 841 594"><defs><marker id="p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="#1f4e79"/></marker></defs></svg><script>{js}</script></body></html>')


JS_FLECHAS = r"""
const MM = 96 / 25.4;
const svg = document.querySelector('svg.flechas');
function caja(id) { const r = document.getElementById(id).getBoundingClientRect();
  return {x: r.left / MM, y: r.top / MM, w: r.width / MM, h: r.height / MM}; }
function linea(x1, y1, x2, y2) {
  const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  Object.entries({x1, y1, x2, y2, stroke: '#1f4e79', 'stroke-width': 1.1, 'marker-end': 'url(#p)'}).forEach(([k, v]) => l.setAttribute(k, v));
  svg.appendChild(l); }
function rotulo(texto, x, y, w, alinear) {
  const d = document.createElement('div'); d.className = 'et-flecha'; d.textContent = texto;
  d.style.left = x + 'mm'; d.style.top = y + 'mm'; d.style.width = w + 'mm'; d.style.textAlign = alinear || 'center';
  document.body.appendChild(d); return d; }
window.FLECHAS = [];
REL.forEach(([a, b, t], i) => {
  const A = caja(a), Bx = caja(b);
  if (A.y + A.h <= Bx.y + 0.1) {            // vertical, hacia abajo
    const x0 = Math.max(A.x, Bx.x), x1 = Math.min(A.x + A.w, Bx.x + Bx.w);
    const x = a === 'Z1' ? Bx.x + 40 : (x0 + x1) / 2;
    linea(x, A.y + A.h + 0.5, x, Bx.y - 0.8);
    const r = rotulo(t, x + 3, A.y + A.h + 2.2, 120, 'left'); r.style.background = 'transparent';
    window.FLECHAS.push([a, b, 'v']);
  } else {                                   // horizontal, en el hueco entre zonas
    const izq = A.x < Bx.x;
    const xa = izq ? A.x + A.w : A.x, xb = izq ? Bx.x : Bx.x + Bx.w;
    const y = A.y + 26;
    linea(xa + 0.6, y, xb - (izq ? 0.9 : -0.9), y);
    const g = Math.abs(xb - xa);
    rotulo(t, Math.min(xa, xb) + 0.5, y + 2.5, g - 1);
    window.FLECHAS.push([a, b, 'h']);
  }
});
"""


CHEQUEO_JS = r"""() => {
  const malos = [];
  document.querySelectorAll('.fit').forEach(el => {
    if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)
      malos.push((el.id || el.closest('[data-concepto]')?.dataset.concepto || el.closest('section')?.querySelector('h1,h2')?.textContent || el.className) + ' ' + el.scrollHeight + '/' + el.clientHeight);
  });
  const rot = [...document.querySelectorAll('.et-flecha')].map(d => d.getBoundingClientRect());
  const zonas = [...document.querySelectorAll('.z')].map(d => d.getBoundingClientRect());
  rot.forEach((r, i) => zonas.forEach((z, j) => {
    const solapa = r.left < z.right - 1 && r.right > z.left + 1 && r.top < z.bottom - 1 && r.bottom > z.top + 1;
    if (solapa) malos.push('rótulo ' + i + ' tapa una zona');
  }));
  return malos;
}"""


INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PESOS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}


def inter_truetype(carpeta, texto):
    """Convierte a TrueType el subconjunto de Inter que usa la página.

    Chromium incrusta las OpenType CFF como Type 3; con TrueType el PDF queda con
    fuentes normales, más fiables al imprimir y al importar en Goodnotes.
    """
    from fontTools import subset
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, newTable
    caras = []
    for peso, nombre in PESOS.items():
        f = TTFont(INTER.format(nombre))
        op = subset.Options()
        op.layout_features = ["kern", "liga", "calt", "case"]
        op.notdef_outline = True
        sub = subset.Subsetter(op)
        sub.populate(text=texto)
        sub.subset(f)
        orden, gs = f.getGlyphOrder(), f.getGlyphSet()
        f["loca"] = newTable("loca")
        glyf = f["glyf"] = newTable("glyf")
        glyf.glyphOrder, glyf.glyphs = orden, {}
        for n in orden:
            pen = TTGlyphPen(gs)
            gs[n].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
            glyf[n] = pen.glyph()
        del f["CFF "]
        maxp = f["maxp"] = newTable("maxp")
        maxp.tableVersion = 0x00010000
        for k in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                  "maxStackElements", "maxSizeOfInstructions", "maxComponentElements", "maxPoints", "maxContours",
                  "maxCompositePoints", "maxCompositeContours", "maxComponentDepth"):
            setattr(maxp, k, 1 if k == "maxZones" else 0)
        post = f["post"]
        post.formatType, post.extraNames, post.mapping, post.glyphOrder = 2.0, [], {}, orden
        f.sfntVersion = "\x00\x01\x00\x00"
        destino = Path(carpeta) / f"inter-{peso}.ttf"
        f.save(destino)
        caras.append(f"@font-face {{ font-family: Inter; font-weight: {peso}; src: url({destino.name}); }}")
    return "\n".join(caras)


def render(html_txt, pdf, ancho, alto, tmp):
    from playwright.sync_api import sync_playwright
    caras = inter_truetype(Path(tmp).parent, html_txt + "0123456789")
    html_txt = html_txt.replace("<style>", "<style>" + caras, 1)
    Path(tmp).write_text(html_txt, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.emulate_media(media="print")
        pg.goto(Path(tmp).resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        malos = pg.evaluate(CHEQUEO_JS)
        if malos:
            b.close()
            raise Alto("Texto que desborda o rótulo encimado: " + "; ".join(malos))
        pg.pdf(path=str(pdf), width=ancho, height=alto, print_background=True, prefer_css_page_size=True)
        b.close()


def paginas_de_conceptos(pdf, conceptos):
    from pypdf import PdfReader
    textos = [pg.extract_text() or "" for pg in PdfReader(str(pdf)).pages]
    for x in conceptos:
        donde = [i + 1 for i, t in enumerate(textos) if x["apartado"] in t.replace("\n", " ")]
        if not donde or donde[0] != x["pagina"]:
            raise Alto(f"{x['id']} está en la página {donde}, no en la {x['pagina']}")
    return len(textos)


def registrar(tema, c):
    m_ruta = tema / "manifest.json"
    m = leer(m_ruta)
    entradas = ["contenido.json", "fuentes.json", "mapa.json", "cobertura.json", "editables/README.md", "editables/generar.py"]
    salidas = ["salidas/pizarra.pdf", "salidas/cuaderno.pdf", "contenido.md"]
    gen = {"entradas": [{"ruta": r, "sha256": sha(tema / r)} for r in entradas],
           "salidas": [{"ruta": r, "sha256": sha(tema / r)} for r in salidas],
           "entorno": entorno()}
    previa = m.get("auditoria", {}).get("generacion_verificada")
    m["generacion"] = gen
    if previa != gen:
        m["auditoria"]["generacion_verificada"] = None
        for k in ("contenido", "visual", "correspondencia"):
            m["auditoria"][k] = {"estado": "pendiente", "evidencia": None}
        m["estado"] = "borrador"
    fijos = {r["ruta"]: r["funcion"] for r in m.get("archivos", [])}
    for r in entradas + salidas:
        fijos.setdefault(r, "salida" if r in salidas else "fuente_editable")
    m["archivos"] = [{"ruta": r, "funcion": f, "sha256": sha(tema / r)} for r, f in sorted(fijos.items())]
    m["version"], m["id"], m["fecha_revision"] = c["version"], c["id"], c["fecha_revision"]
    m_ruta.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entorno():
    import platform
    from importlib.metadata import version
    return {"python": platform.python_version(), "playwright": version("playwright"), "pypdf": version("pypdf"),
            "tipografia": "Inter 4 OpenType del sistema, convertida a TrueType con fontTools; Caladea TrueType del sistema", "fonttools": version("fonttools")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tema")
    ap.add_argument("--privado", help="JSON con los valores reales de las variables; no se publica")
    ap.add_argument("--salida", help="Carpeta de salida para la edición privada")
    a = ap.parse_args()
    tema = Path(a.tema).resolve()
    c, fuentes, mapa = leer(tema / "contenido.json"), leer(tema / "fuentes.json"), leer(tema / "mapa.json")
    try:
        comprobar(c, fuentes, mapa)
        v = dict(c["variables"])
        if a.privado:
            if not a.salida:
                raise Alto("La edición privada necesita --salida fuera del repositorio")
            salida = Path(a.salida).resolve()
            if tema in salida.parents or salida == tema:
                raise Alto("La edición privada no puede escribirse dentro del tema")
            priv = leer(a.privado)
            desconocidas = set(priv) - set(v)
            if desconocidas:
                raise Alto(f"Variables privadas no usadas: {sorted(desconocidas)}")
            v.update(priv)
        else:
            salida = tema / "salidas"
        salida.mkdir(parents=True, exist_ok=True)
        tmp = salida / ".html"
        tmp.mkdir(exist_ok=True)
        render(pizarra_html(c, mapa, v), salida / "pizarra.pdf", "841mm", "594mm", tmp / "pizarra.html")
        render(cuaderno_html(c, fuentes, v), salida / "cuaderno.pdf", "215.9mm", "279.4mm", tmp / "cuaderno.html")
        n = paginas_de_conceptos(salida / "cuaderno.pdf", c["conceptos"])
        for f in tmp.iterdir():
            f.unlink()
        tmp.rmdir()
        if not a.privado:
            (tema / "contenido.md").write_text(vista_md(c, fuentes, mapa), encoding="utf-8")
            registrar(tema, c)
        print(f"Listo: pizarra A1 y cuaderno de {n} páginas en {salida}. Auditorías pendientes hasta revisar.")
    except Alto as exc:
        print("Generación detenida: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
