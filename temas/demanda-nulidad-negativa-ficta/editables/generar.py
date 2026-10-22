#!/usr/bin/env python3
"""Dos composiciones abiertas desde un único contenido revisado.

No investiga ni aprueba su propia salida. Todo cambio de conceptos o reglas
requiere revisar la correspondencia de la síntesis antes de regenerar.
"""
import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape, A1, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

BLUE = colors.HexColor('#174B70')
INK = colors.HexColor('#23323D')
MUTED = colors.HexColor('#516470')
PALE = colors.HexColor('#EFF5F8')
LINE = colors.HexColor('#B8C9D3')
MM = 72 / 25.4


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    return digest_bytes(path.read_bytes())


def review_digest(data):
    scope = {k: data[k] for k in ('conceptos', 'reglas_criticas')}
    return digest_bytes(json.dumps(scope, ensure_ascii=False, sort_keys=True,
                                   separators=(',', ':')).encode('utf-8'))


def check_keys(obj, required, optional=(), label='objeto'):
    missing = set(required) - set(obj)
    extra = set(obj) - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f'{label}: campos faltantes {sorted(missing)}; no consumidos {sorted(extra)}')


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: se requiere texto no vacío')


def validate(data, sources, mapa, coverage):
    check_keys(data, ('id', 'titulo', 'version', 'fecha_revision', 'pregunta', 'alcance',
                      'conceptos', 'paginas', 'pizarra', 'reglas_criticas', 'revision_sintesis'))
    for key in ('id', 'titulo', 'version', 'fecha_revision', 'pregunta', 'alcance'):
        nonempty(data[key], key)
    concepts = {}
    source_ids = {f['id'] for f in sources}
    if len(source_ids) != len(sources):
        raise ValueError('Fuentes con identificadores repetidos')
    for item in data['conceptos']:
        check_keys(item, ('id', 'titulo', 'apartado', 'pagina', 'entradilla', 'bloques',
                          'sintesis', 'notas_prompt'), label='concepto')
        if item['id'] in concepts:
            raise ValueError('Concepto repetido: ' + item['id'])
        for key in ('id', 'titulo', 'apartado', 'entradilla', 'notas_prompt'):
            nonempty(item[key], item['id'] + '.' + key)
        for block in item['bloques']:
            check_keys(block, ('subtitulo', 'texto', 'fuentes'), label='bloque')
            nonempty(block['subtitulo'], 'subtitulo')
            nonempty(block['texto'], 'texto')
            if not set(block['fuentes']).issubset(source_ids):
                raise ValueError('Fuente inexistente en ' + item['id'])
        check_keys(item['sintesis'], ('titulo', 'texto', 'fuentes'), label='sintesis')
        for key in ('titulo', 'texto'):
            nonempty(item['sintesis'][key], 'sintesis.' + key)
        if not set(item['sintesis']['fuentes']).issubset(source_ids):
            raise ValueError('Fuente inexistente en síntesis')
        concepts[item['id']] = item
    page_concepts = []
    listed_sources = []
    for index, page in enumerate(data['paginas'], 1):
        check_keys(page, ('numero', 'titulo', 'conceptos', 'tipo', 'notas_prompt'),
                   ('fuentes',), label='pagina')
        if page['numero'] != index or page['tipo'] not in ('conceptos', 'fuentes'):
            raise ValueError('Páginas deben ser consecutivas y con tipo válido')
        nonempty(page['titulo'], 'titulo página')
        nonempty(page['notas_prompt'], 'notas_prompt página')
        if page['tipo'] == 'conceptos':
            if not page['conceptos']:
                raise ValueError('Página de conceptos vacía')
            for cid in page['conceptos']:
                if cid not in concepts or concepts[cid]['pagina'] != index:
                    raise ValueError('Destino de concepto incoherente: ' + cid)
            page_concepts += page['conceptos']
        else:
            if page['conceptos']:
                raise ValueError('Página de fuentes no puede ocultar conceptos')
            listed_sources += page.get('fuentes', [])
    if sorted(page_concepts) != sorted(concepts):
        raise ValueError('Cada concepto debe consumirse una vez en el cuaderno')
    if sorted(listed_sources) != sorted(source_ids):
        raise ValueError('Distribuir cada fuente una vez en páginas tipo fuentes')
    check_keys(data['pizarra'], ('subtitulo', 'zonas'), label='pizarra')
    if len(data['pizarra']['zonas']) != 6:
        raise ValueError('Esta composición requiere seis zonas; cambiar diseño si cambia la arquitectura')
    zoned = []
    for zone in data['pizarra']['zonas']:
        check_keys(zone, ('id', 'titulo', 'conceptos'), label='zona')
        nonempty(zone['titulo'], 'zona.titulo')
        zoned += zone['conceptos']
    if sorted(zoned) != sorted(concepts):
        raise ValueError('Cada síntesis debe consumirse una vez en el lienzo')
    rule_ids = []
    for rule in data['reglas_criticas']:
        check_keys(rule, ('id', 'valor', 'unidad', 'aplica_a'), label='regla')
        nonempty(rule['id'], 'regla.id')
        nonempty(rule['unidad'], 'regla.unidad')
        nonempty(rule['aplica_a'], 'regla.aplica_a')
        rule_ids.append(rule['id'])
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError('Reglas repetidas')
    text_blob = json.dumps(data, ensure_ascii=False)
    for token in re.findall(r'\{\{([^{}]+)\}\}', text_blob):
        if token not in rule_ids:
            raise ValueError('Token de regla inexistente: ' + token)
    if mapa['tema_id'] != data['id'] or mapa['version'] != data['version']:
        raise ValueError('Identidad/versión del mapa no corresponde')
    if {c['id'] for c in mapa['conceptos']} != set(concepts):
        raise ValueError('Mapa y canónico tienen conceptos distintos')
    for relation in mapa['relaciones']:
        if relation['desde'] not in concepts or relation['hacia'] not in concepts:
            raise ValueError('Conexión con concepto inexistente')
        if not set(relation['fuentes']).issubset(source_ids):
            raise ValueError('Conexión con fuente inexistente')
    for row in coverage:
        if not set(row['conceptos']).issubset(concepts):
            raise ValueError('Cobertura con destino inexistente')
    check_keys(data['revision_sintesis'], ('sha256', 'nota'), label='revision_sintesis')
    nonempty(data['revision_sintesis']['nota'], 'revision_sintesis.nota')
    if data['revision_sintesis']['sha256'] != review_digest(data):
        raise ValueError('Cambió una explicación, síntesis o premisa compartida. Revisar sus condiciones, '
                         'excepciones y correspondencia entre formatos; después registrar la huella '
                         'revisada. Se detuvo la generación para no conservar una síntesis incompatible.')
    return concepts


def resolved(text, data):
    for rule in data['reglas_criticas']:
        text = text.replace('{{' + rule['id'] + '}}', str(rule['valor']) + ' ' + rule['unidad'])
    return text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-').replace('\u00a0', ' ')


def markup(text, data):
    return escape(resolved(text, data)).replace('\n', '<br/>')


def para(text, x, top, width, size=11.5, leading=None, color=INK, bold=False, data=None,
         canvas_obj=None, bottom=0, html=False):
    text = text if html else markup(text, data)
    style = ParagraphStyle('p', fontName='Helvetica-Bold' if bold else 'Helvetica',
                           fontSize=size, leading=leading or size * 1.26,
                           textColor=color, alignment=TA_LEFT, spaceBefore=0, spaceAfter=0,
                           splitLongWords=True, allowWidows=0, allowOrphans=0)
    p = Paragraph(text, style)
    w, h = p.wrap(width, 10000)
    if top - h < bottom:
        raise ValueError(f'Texto desborda la zona ({top-h:.1f} < {bottom:.1f}): {text[:100]}')
    if canvas_obj:
        p.drawOn(canvas_obj, x, top - h)
    return top - h


def line(c, x1, y1, x2, y2, width=0.6, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def arrow(c, points, label, data, label_box):
    c.setStrokeColor(BLUE)
    c.setFillColor(BLUE)
    c.setLineWidth(1.5)
    p = c.beginPath()
    p.moveTo(*points[0])
    for xy in points[1:]:
        p.lineTo(*xy)
    c.drawPath(p)
    x0, y0 = points[-2]
    x, y = points[-1]
    dx, dy = x - x0, y - y0
    norm = (dx*dx + dy*dy) ** .5
    ux, uy = dx/norm, dy/norm
    path = c.beginPath()
    path.moveTo(x, y)
    path.lineTo(x - ux*11 - uy*5, y - uy*11 + ux*5)
    path.lineTo(x - ux*11 + uy*5, y - uy*11 - ux*5)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    lx, ly, lw = label_box
    para(label, lx, ly, lw, 14, 17.5, BLUE, data=data, canvas_obj=c)


def references_text(ids):
    return ' · '.join('[' + i + ']' for i in ids)


def draw_notes(c, x, top, width, prompt, data, size=9.5, bottom=52):
    para(prompt, x, top, width, size, size*1.25, MUTED, data=data, canvas_obj=c)
    for y in [top - 25, top - 45, top - 65]:
        if y >= bottom:
            line(c, x, y, x+width, y, .4)


def draw_cuaderno(path, data, sources, concepts):
    c = canvas.Canvas(str(path), pagesize=letter, pageCompression=1, invariant=1)
    c.setTitle(data['titulo'] + ' - páginas Carta')
    c.setAuthor('Material de estudio')
    width, height = letter
    left, right = 22*MM, 18*MM
    content_width = width-left-right
    source_by_id = {f['id']:f for f in sources}
    for page in data['paginas']:
        c.setFillColor(BLUE)
        c.rect(left, height-54, 34, 3, fill=1, stroke=0)
        para(data['titulo'], left+45, height-46, content_width-45, 9, 11, MUTED,
             data=data, canvas_obj=c)
        page_title = ((page['conceptos'][0] + '  ') if len(page['conceptos']) == 1 else '') + page['titulo']
        top = para(page_title, left, height-78, content_width, 23, 27,
                   BLUE, True, data, c, bottom=180) - 17
        if page['numero'] == 1:
            top = para(data['pregunta'], left, top, content_width, 12, 15.2,
                       BLUE, True, data, c, bottom=180) - 12
            # El alcance se conserva completo en la primera página de fuentes.
        if page['tipo'] == 'conceptos':
            for n, cid in enumerate(page['conceptos']):
                item = concepts[cid]
                if n:
                    line(c,left,top+2,left+content_width,top+2)
                    top -= 16
                if item['titulo'] != page['titulo']:
                    top = para(cid + '  ' + item['titulo'], left, top, content_width,
                               13, 16, BLUE, True, data, c, bottom=180) - 8
                else:
                    # El ID acompaña la cabecera sin duplicar el título.
                    pass
                top = para(item['entradilla'], left, top, content_width,
                           11.5, 14.5, INK, False, data, c, bottom=180) - 12
                for block in item['bloques']:
                    block_markup = '<b>' + markup(block['subtitulo'], data) + '.</b> ' + markup(block['texto'], data)
                    top = para(block_markup, left, top, content_width,
                               11.5, 14.5, INK, False, data, c, bottom=180, html=True) - 6
                    if block['fuentes'] and not re.search(r'\[F\d', block['texto']):
                        top = para(references_text(block['fuentes']), left, top, content_width,
                                   9, 11, MUTED, False, data, c, bottom=180) - 9
                    else:
                        top -= 6
                # El prompt de cada concepto se consume al pie de su desarrollo.
                if item['notas_prompt'] != page['notas_prompt']:
                    top = para(item['notas_prompt'], left, top, content_width,
                               10, 12.5, MUTED, False, data, c, bottom=180) - 8
        else:
            if page['numero'] == min(p['numero'] for p in data['paginas'] if p['tipo'] == 'fuentes'):
                top = para(data['alcance'], left, top, content_width, 10, 12.5,
                           MUTED, False, data, c, bottom=180) - 18
            for fid in page['fuentes']:
                source = source_by_id[fid]
                url = source.get('url_o_identificador') or ''
                title = escape(str(source['titulo']))
                if str(url).startswith('https://'):
                    title = '<link href="' + escape(url, {'"':'&quot;'}) + '">' + title + '</link>'
                top = para('['+fid+'] '+title, left, top, content_width, 11, 13.5,
                           BLUE, True, data, c, 180, html=True) - 5
                institution = source.get('autor_institucion') or 'Autor no indicado'
                date = source.get('fecha_edicion')
                details = str(institution) + ('. Edición/reforma: '+str(date) if date else '')
                top = para(details, left, top, content_width, 9.5, 12,
                           MUTED, False, data, c, 180) - 4
                locator = source.get('localizadores', [])
                if isinstance(locator, list):
                    locator = '; '.join(str(v) for v in locator)
                top = para(str(locator), left, top, content_width, 9.5, 12,
                           INK, False, data, c, 180) - 4
                # El URL completo permanece accesible y seleccionable en el PDF.
                top = para(str(url), left, top, content_width, 9, 11.3,
                           MUTED, False, data, c, 180) - 13
        line(c,left,162,left+content_width,162,.7)
        draw_notes(c,left,149,content_width,page['notas_prompt'],data,bottom=62)
        para(data['id'] + ' · v' + data['version'] + ' · ' + data['fecha_revision'],
             left, 37, content_width-35, 8, 10, MUTED, data=data, canvas_obj=c)
        c.setFillColor(BLUE)
        c.setFont('Helvetica-Bold', 9)
        c.drawRightString(width-right, 28, str(page['numero']))
        c.showPage()
    c.save()


def draw_zone(c, zone, rect, data, concepts, columns=1, shade=False):
    x,y,w,h = rect
    pad=24 if shade else 0
    if shade:
        c.setFillColor(PALE)
        c.rect(x,y,w,h,fill=1,stroke=0)
    xx=x+pad
    ww=w-2*pad
    top=y+h-pad
    top=para(zone['id']+'  '+zone['titulo'],xx,top,ww,29,34,BLUE,True,data,c,y+35)-20
    if columns == 1:
        for index,cid in enumerate(zone['conceptos']):
            item=concepts[cid]
            top=para(cid+'  '+item['sintesis']['titulo'],xx,top,ww,21,25.5,BLUE,True,data,c,y+26)-7
            top=para(item['sintesis']['texto'],xx,top,ww,19,24,INK,False,data,c,y+26)-9
            top=para(references_text(item['sintesis']['fuentes'])+'  ·  p. '+str(item['pagina']),
                     xx,top,ww,14,17.5,MUTED,False,data,c,y+15)-18
    else:
        colw=(ww-(columns-1)*36)/columns
        maxbottom=top
        for index,cid in enumerate(zone['conceptos']):
            item=concepts[cid]
            cx=xx+index*(colw+36)
            cy=top
            cy=para(cid+'  '+item['sintesis']['titulo'],cx,cy,colw,21,25.5,BLUE,True,data,c,y+26)-7
            cy=para(item['sintesis']['texto'],cx,cy,colw,19,24,INK,False,data,c,y+26)-9
            cy=para(references_text(item['sintesis']['fuentes'])+'  ·  p. '+str(item['pagina']),
                    cx,cy,colw,14,17.5,MUTED,False,data,c,y+15)-18
            maxbottom=min(maxbottom,cy)
        top=maxbottom
    return top


def zone_connection(mapa, zone_from, zone_to):
    candidates=[r for r in mapa['relaciones'] if r['desde'] in zone_from['conceptos']
                and r['hacia'] in zone_to['conceptos']]
    if candidates:
        r=candidates[0]
        return r['relacion']
    return 'Ruta de lectura: '+zone_from['id']+' a '+zone_to['id']


def draw_pizarra(path, data, sources, concepts, mapa):
    size=landscape(A1)
    c=canvas.Canvas(str(path),pagesize=size,pageCompression=1,invariant=1)
    c.setTitle(data['titulo']+' - pizarra conectada')
    c.setAuthor('Material de estudio')
    W,H=size
    m=60
    para(data['titulo'],m,H-61,W-2*m,52,59,BLUE,True,data,c,H-210)
    para(data['pizarra']['subtitulo'],m,H-139,W-2*m,22,28,INK,False,data,c,H-240)
    zones=data['pizarra']['zonas']
    # Inicio y comparación; después defensa; al final decisión y aplicación.
    # Los corredores de cien puntos permiten recorrer el mapa sin cruzar texto.
    zrects=[(m,1100,1060,370),(m+1180,1100,W-2*m-1180,370),
            (m,635,950,365),(m+1050,635,570,365),
            (m+1720,635,W-2*m-1720,365),(m,170,W-2*m,365)]
    draw_zone(c,zones[0],zrects[0],data,concepts,columns=len(zones[0]['conceptos']),shade=True)
    draw_zone(c,zones[1],zrects[1],data,concepts,columns=len(zones[1]['conceptos']))
    draw_zone(c,zones[2],zrects[2],data,concepts,columns=len(zones[2]['conceptos']))
    draw_zone(c,zones[3],zrects[3],data,concepts)
    draw_zone(c,zones[4],zrects[4],data,concepts)
    draw_zone(c,zones[5],zrects[5],data,concepts,columns=len(zones[5]['conceptos']))
    arrow(c,[(m+1072,1280),(m+1160,1280)],
          zone_connection(mapa,zones[0],zones[1]),data,(m+1070,1340,100))
    arrow(c,[(m+1520,1090),(m+1520,1050),(m+470,1050),(m+470,1010)],
          zone_connection(mapa,zones[1],zones[2]),data,(m+720,1080,700))
    arrow(c,[(m+965,900),(m+1030,900)],
          zone_connection(mapa,zones[2],zones[3]),data,(m+960,969,80))
    arrow(c,[(m+1635,900),(m+1700,900)],
          zone_connection(mapa,zones[3],zones[4]),data,(m+1630,969,80))
    arrow(c,[(m+1970,625),(m+1970,588),(m+1120,588),(m+1120,545)],
          zone_connection(mapa,zones[4],zones[5]),data,(m+1300,620,590))
    # Espacios útiles junto al tema de cada nivel, sin añadir explicaciones nuevas.
    for zi in (0,1,2,3,4):
        x,y,w,h=zrects[zi]
        prompt=concepts[zones[zi]['conceptos'][-1]]['notas_prompt']
        # La frase invita a escribir; dos guías discretas quedan dentro de la zona.
        para(prompt,x+24 if zi==0 else x,y+65,w-48 if zi==0 else w,
             14,17.5,MUTED,False,data,c,y+15)
        line(c,x+24 if zi==0 else x,y+18,x+w-24 if zi==0 else x+w,y+18,.5)
    # Bajo C11 se conserva espacio para resolver, sin mostrar la respuesta antes.
    z6x,z6y,z6w,z6h=zrects[5]
    cw=(z6w-3*36)/4
    for i,cid in enumerate(zones[5]['conceptos']):
        xx=z6x+i*(cw+36)
        line(c,xx,z6y+16,xx+cw,z6y+16,.5)
    sources_pages=[str(p['numero']) for p in data['paginas'] if p['tipo']=='fuentes']
    para('Fuentes y localizadores: cuaderno, pp. '+', '.join(sources_pages)+'. '+
         ' · '.join(f['id'] for f in sources),m,115,W-2*m,14,18,MUTED,False,data,c,75)
    para(data['id']+' · v'+data['version']+' · Revisión '+data['fecha_revision'],
         m,62,W-2*m,14,18,MUTED,False,data,c,25)
    c.save()


def markdown(data,sources,mapa):
    chunks=['# '+data['titulo'],f"Tema: {data['id']} · Versión: {data['version']} · Revisión: {data['fecha_revision']}",
            '## Pregunta y alcance',data['pregunta'],data['alcance']]
    for item in data['conceptos']:
        chunks += ['## '+item['apartado'],item['entradilla']]
        for block in item['bloques']:
            chunks += ['### '+block['subtitulo'],block['texto']+' '+references_text(block['fuentes'])]
        chunks += ['### Síntesis intencional del lienzo',item['sintesis']['titulo'],
                   item['sintesis']['texto']+' '+references_text(item['sintesis']['fuentes']),
                   'Para anotar: '+item['notas_prompt']]
    chunks+=['## Reglas compartidas']
    chunks += [r['id']+': '+str(r['valor'])+' '+r['unidad']+' · '+r['aplica_a'] for r in data['reglas_criticas']]
    chunks+=['## Conexiones del mapa']
    chunks += [r['desde']+' '+r['relacion']+' '+r['hacia']+'. '+r['justificacion'] for r in mapa['relaciones']]
    chunks+=['## Fuentes']
    for source in sources:
        chunks += ['### '+source['id']+' · '+source['titulo'],
                   str(source.get('autor_institucion')),
                   str(source.get('url_o_identificador')),
                   'Localizadores: '+json.dumps(source.get('localizadores'),ensure_ascii=False)]
    return resolved('\n\n'.join(chunks)+'\n',data)


def update_manifest(root,data):
    manifest_path=root/'manifest.json'
    manifest=read_json(manifest_path)
    if manifest['id'] != data['id'] or manifest['version'] != data['version']:
        raise ValueError('El manifiesto no coincide con la identidad/versión del contenido')
    inputs=['contenido.json','fuentes.json','mapa.json','cobertura.json']
    inputs += [str(p.relative_to(root)) for p in sorted((root/'editables').rglob('*'))
               if p.is_file() and '__pycache__' not in p.parts]
    outputs=['salidas/pizarra.pdf','salidas/cuaderno.pdf','contenido.md']
    generation={'entradas':[{'ruta':p,'sha256':digest_file(root/p)} for p in inputs],
                'salidas':[{'ruta':p,'sha256':digest_file(root/p)} for p in outputs],
                'entorno':{'python':sys.version.split()[0], 'reportlab':reportlab.Version,
                           'tipografia':'Helvetica, fuentes estándar PDF'}}
    manifest['generacion']=generation
    manifest['contenido_canonico']='contenido.json'
    manifest['vista_contenido']='contenido.md'
    manifest['estado']='borrador'
    manifest.setdefault('auditoria',{})['generacion_verificada']=None
    for field in ('contenido','visual','correspondencia'):
        manifest['auditoria'][field]={'estado':'pendiente','evidencia':'Nueva generación: revisar los archivos con los hashes actuales.'}
    files=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:
            continue
        rel=str(p.relative_to(root))
        if rel.startswith(('tmp/','qa/','renders/')):
            continue
        func='salida' if rel in outputs else 'fuente_editable' if rel in inputs else 'documentacion'
        files.append({'ruta':rel,'funcion':func,'sha256':digest_file(p)})
    manifest['archivos']=files
    manifest['reproduccion']={'comando':'python3 editables/generar.py .',
                              'dependencias':['Python >=3.9','reportlab =='+reportlab.Version]}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def self_test(data,sources,mapa,coverage):
    tests=[]
    variants=[]
    changed=copy.deepcopy(data)
    changed['conceptos'][0]['bloques'][0]['texto'] += ' Cambio sustantivo de prueba.'
    variants.append(('explicacion_sustantiva',changed))
    changed=copy.deepcopy(data)
    if not changed['reglas_criticas']:
        raise ValueError('Se necesita un dato compartido para probar continuidad')
    changed['reglas_criticas'][0]['valor']=999
    variants.append(('dato_compartido',changed))
    changed=copy.deepcopy(data)
    changed['conceptos'][0]['sintesis']['texto']='Toda omisión concede automáticamente lo solicitado.'
    variants.append(('premisa_invertida',changed))
    for label,variant in variants:
        try:
            validate(variant,sources,mapa,coverage)
        except ValueError as exc:
            if not str(exc).startswith('Cambió una explicación'):
                raise
            tests.append({'prueba':label,'resultado':'bloqueada correctamente antes de generar','motivo':str(exc)})
        else:
            raise ValueError('Se aceptó una modificación no revisada: '+label)
    changed=copy.deepcopy(data)
    changed['conceptos'][0]['desarrollo_retirado']='No debe ignorarse'
    try:
        validate(changed,sources,mapa,coverage)
    except ValueError:
        tests.append({'prueba':'campo_desconocido','resultado':'rechazado'})
    else:
        raise ValueError('Campo desconocido aceptado silenciosamente')
    return tests


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tema',nargs='?',default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument('--huella',action='store_true',help='Imprime la huella; no revisa ni aprueba contenido')
    ap.add_argument('--self-test',action='store_true',help='Ensayo en memoria sin alterar el canónico')
    args=ap.parse_args()
    root=Path(args.tema).resolve()
    data=read_json(root/'contenido.json')
    if args.huella:
        print(review_digest(data))
        return
    sources=read_json(root/'fuentes.json')
    mapa=read_json(root/'mapa.json')
    coverage=read_json(root/'cobertura.json')
    concepts=validate(data,sources,mapa,coverage)
    if args.self_test:
        print(json.dumps(self_test(data,sources,mapa,coverage),ensure_ascii=False,indent=2))
        return
    # Ambos PDF se reemplazan solo tras generar correctamente los dos.
    (root/'salidas').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pizarras-generacion-') as td:
        temporary=Path(td)
        draw_cuaderno(temporary/'cuaderno.pdf',data,sources,concepts)
        draw_pizarra(temporary/'pizarra.pdf',data,sources,concepts,mapa)
        for name in ('cuaderno.pdf','pizarra.pdf'):
            shutil.copyfile(temporary/name,root/'salidas'/name)
    (root/'contenido.md').write_text(markdown(data,sources,mapa),encoding='utf-8')
    update_manifest(root,data)
    print(json.dumps({'estado':'generado_pendiente_auditoria','cuaderno_paginas':len(data['paginas']),
                      'lienzos':1,'salidas':['salidas/pizarra.pdf','salidas/cuaderno.pdf']},ensure_ascii=False))


if __name__=='__main__':
    try:
        main()
    except (ValueError,KeyError) as exc:
        print('GENERACIÓN DETENIDA: '+str(exc),file=sys.stderr)
        sys.exit(2)
