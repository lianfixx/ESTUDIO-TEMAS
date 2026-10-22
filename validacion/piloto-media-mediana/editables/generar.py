#!/usr/bin/env python3
"""Dos composiciones desde contenido.json. contenido.md es una vista derivada.
Python 3 + ReportLab; los pasos de auditoría son externos a la generación.
"""
from pathlib import Path
from fractions import Fraction
import argparse, hashlib, json, math, os, re, shutil, sys
from tempfile import TemporaryDirectory
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A1, landscape, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

BLUE=colors.HexColor('#164A72'); INK=colors.HexColor('#1D2A35'); LIGHT=colors.HexColor('#EEF5FA'); LINE=colors.HexColor('#A6BAC9'); PALE=colors.HexColor('#F8FAFC')

def read_json(path): return json.loads(path.read_text(encoding='utf-8'))
def write_json(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def fmt(value):
    v=Fraction(value)
    if v.denominator==1:return str(v.numerator)
    # Los datos decimales, medias de cinco y medianas de dos terminan en decimal.
    sign='-' if v<0 else '';n=abs(v.numerator);whole,rest=divmod(n,v.denominator);digits=[]
    while rest:
        digit,rest=divmod(rest*10,v.denominator);digits.append(str(digit))
        if len(digits)>12:raise ValueError('Resultado fuera de la precisión decimal del piloto.')
    return sign+str(whole)+','+''.join(digits)
def stats(vals):
    v=sorted(Fraction(x) for x in vals);n=len(v)
    med=v[n//2] if n%2 else (v[n//2-1]+v[n//2])/2
    return dict(datos=[int(x) if x.denominator==1 else str(x) for x in v],n=n,suma=str(sum(v)),media=str(sum(v)/n),mediana=str(med))
def context_for(name,vals):
    v=sorted(vals); s=stats(v);n=len(v)
    result={name+'_'+k:fmt(s[k]) for k in ('n','suma','media','mediana')}
    result.update({name+'_lista':', '.join(map(fmt,v)),name+'_suma_expr':' + '.join(map(fmt,v)),name+'_mayor':fmt(v[-1]),name+'_minimo':fmt(v[0]),name+'_rango':fmt(v[-1]-v[0]),name+'_posicion':fmt((n+1)//2),name+'_menores':str(sum(Fraction(x)<Fraction(s['mediana']) for x in v)),name+'_mayores':str(sum(Fraction(x)>Fraction(s['mediana']) for x in v)),name+'_centro_expr':' + '.join(map(fmt,v[n//2-1:n//2+1]))})
    return result

def resolve_text(key,trail=()):
    USED_TEXTS.add(key)
    if key in trail:raise ValueError('Referencia circular de texto: '+key)
    item=CONTENT['textos']
    try:
        for part in key.split('.'):item=item[part]
    except (KeyError,TypeError):raise ValueError('Bloque de texto inexistente: '+key) from None
    if isinstance(item,dict) and set(item)=={'ref'} and isinstance(item['ref'],str):
        return resolve_text(item['ref'],trail+(key,))
    if not isinstance(item,str):raise ValueError('El bloque debe ser texto o una referencia: '+key)
    return item

def T(key):
    USED_TEXTS.add(key)
    return resolve_text(key).format_map(CTX)

def duration(value,label):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(label+': se requiere un número JSON finito; no se admiten booleanos.')
    result=Fraction(str(value))
    if result<0 or result>Fraction('999.99') or (result*100).denominator!=1:
        raise ValueError(label+': el piloto admite duraciones de 0 a 999,99 con máximo dos decimales.')
    return result

def change_phrase(delta,n):
    if delta==0:return 'no cambia (0 min)'
    return ('sube ' if delta>0 else 'baja ')+fmt(abs(delta))+'/'+str(n)+' = '+fmt(abs(delta)/n)+' min'

def configure_fonts(directory=None):
    global NORMAL,BOLD,FONT_INFO
    requested=directory or os.environ.get('PIZARRAS_FONT_DIR')
    candidates=[Path(requested)] if requested else []
    candidates += [Path('/usr/share/fonts/truetype/dejavu'),Path(reportlab.__file__).resolve().parent/'fonts']
    for folder in candidates:
        for normal,bold in [('DejaVuSans.ttf','DejaVuSans-Bold.ttf'),('Vera.ttf','VeraBd.ttf')]:
            paths=[folder/normal,folder/bold]
            if all(p.is_file() for p in paths):
                NORMAL,BOLD='TemaNormal','TemaBold'
                for name,path in zip((NORMAL,BOLD),paths):pdfmetrics.registerFont(TTFont(name,str(path)))
                pdfmetrics.registerFontFamily(NORMAL,normal=NORMAL,bold=BOLD,italic=NORMAL,boldItalic=BOLD)
                FONT_INFO=[{'familia':'DejaVu Sans' if normal.startswith('DejaVu') else 'Bitstream Vera','archivo':p.name,'sha256':sha(p)} for p in paths]
                if requested and folder!=Path(requested):print('Aviso: tipografías solicitadas no disponibles; se usa '+normal,file=sys.stderr)
                elif normal=='Vera.ttf':print('Tipografía alternativa: Bitstream Vera incluida en ReportLab.',file=sys.stderr)
                return
    raise RuntimeError('No hay tipografías compatibles. Instala DejaVu Sans o indica --font-dir (DejaVuSans.ttf/DejaVuSans-Bold.ttf o Vera.ttf/VeraBd.ttf).')

def load(root):
    global ROOT,OUT,CONTENT,META,SOURCES,MAP,COVERAGE,SCENARIOS,CTX,URL,USED_TEXTS
    ROOT=root.resolve();OUT=ROOT/'salidas';OUT.mkdir(exist_ok=True);(ROOT/'revision').mkdir(exist_ok=True)
    CONTENT=read_json(ROOT/'contenido.json');META=CONTENT;SOURCES=read_json(ROOT/'fuentes.json');MAP=read_json(ROOT/'mapa.json');COVERAGE=read_json(ROOT/'cobertura.json')
    USED_TEXTS=set()
    if any('parrafos' in s for s in CONTENT.get('secciones',[])):
        raise ValueError('Campo antiguo secciones[].parrafos: migra su explicación a textos renderizados y referencia esos bloques; no se ignora.')
    if CONTENT.get('schema_version')!='1.1':raise ValueError('contenido.json requiere schema 1.1, con secciones[].bloques.')
    for section in CONTENT['secciones']:
        if not isinstance(section.get('bloques'),list) or not section['bloques']:raise ValueError('Cada sección requiere bloques renderizados.')
        for ref in section['bloques']:
            if not isinstance(ref,str) or ref.split('.')[0] not in ('pizarra','cuaderno'):raise ValueError('La sección debe referir bloques de pizarra/cuaderno.')
            resolve_text(ref)
    ids=[x['id'] for x in CONTENT['secciones']]; mids=[x['id'] for x in MAP['conceptos']]; fids=[x['id'] for x in SOURCES]
    if len(ids)!=len(set(ids)) or set(ids)!=set(mids) or len(mids)!=len(set(mids)):raise ValueError('Conceptos canónicos y mapa no coinciden o se repiten.')
    if len(fids)!=len(set(fids)):raise ValueError('IDs de fuentes repetidos.')
    if (MAP['tema_id'],MAP['version'])!=(META['id'],META['version']):raise ValueError('La identidad y versión del mapa deben coincidir con contenido.json.')
    headers={x['id']+' · '+x['titulo'] for x in CONTENT['secciones']}
    if any(x['apartado'] not in headers for x in MAP['conceptos']):raise ValueError('Apartado del mapa inexistente.')
    for rel in MAP['relaciones']:
        if rel['desde'] not in ids or rel['hacia'] not in ids or not set(rel['fuentes'])<=set(fids):raise ValueError('Relación con referencia inexistente.')
    for rem in MAP['remisiones']:
        if rem['concepto_id'] not in ids or not all(isinstance(p,int) and 1<=p<=3 for p in rem['paginas_cuaderno']):raise ValueError('Remisión inválida.')
    for item in COVERAGE:
        if not set(item['conceptos'])<=set(ids) or item['entrada_id'] not in {x['id'] for x in META['entradas']}:raise ValueError('Cobertura con referencia inexistente.')
    d=CONTENT['datos']
    if not all(isinstance(d[k],list) and len(d[k])==5 for k in ('principal','ejercicio')):raise ValueError('Este piloto requiere cinco duraciones en cada ejemplo.')
    principal=sorted(duration(x,'datos.principal') for x in d['principal']);ejercicio=sorted(duration(x,'datos.ejercicio') for x in d['ejercicio'])
    if any(values[-1]<=values[-2] for values in (principal,ejercicio)):
        raise ValueError('Este piloto requiere un máximo estricto en principal y ejercicio por la premisa del traslado largo; admite repeticiones centrales.')
    comparison={k:duration(d['comparacion'][k],'datos.comparacion.'+k) for k in ('base','aumentado')}
    replacement=duration(d['sustitucion_ejercicio'],'datos.sustitucion_ejercicio')
    # Esta composición compara cinco traslados y cambia solo el máximo.
    for value in comparison.values():
        if value<principal[-2]:raise ValueError('La sustitución debe conservar los valores centrales.')
    if comparison['aumentado']<principal[-1]:raise ValueError('El escenario aumentado debe ser mayor o igual que el máximo principal.')
    if replacement<ejercicio[-2]:raise ValueError('La sustitución del ejercicio debe conservar los valores centrales.')
    SCENARIOS={'base':principal[:-1]+[comparison['base']],'principal':principal,'aumentado':principal[:-1]+[comparison['aumentado']],'retirado':principal[:-1],'ejercicio':ejercicio,'sustitucion':ejercicio[:-1]+[replacement]}
    CTX=dict(META)
    for name,values in SCENARIOS.items():CTX.update(context_for(name,values))
    delta=principal[-1]-comparison['base'];exercise_delta=replacement-ejercicio[-1]
    old_median=Fraction(stats(principal)['mediana']);removed_median=Fraction(stats(principal[:-1])['mediana'])
    CTX.update(cambio_suma=fmt(delta),cambio_media=fmt(delta/len(principal)),cambio_media_ejercicio=fmt(exercise_delta/len(ejercicio)),cambio_total_frase=('el total no cambia' if delta==0 else ('el total aumenta ' if delta>0 else 'el total disminuye ')+fmt(abs(delta))+' min'),cambio_media_frase=change_phrase(delta,len(principal)),ejercicio_media_frase=change_phrase(exercise_delta,len(ejercicio)),retiro_mediana_frase=('la mediana se conserva en '+fmt(old_median)+' min' if old_median==removed_median else 'la mediana cambia de '+fmt(old_median)+' a '+fmt(removed_median)+' min'))
    f=next(s for s in SOURCES if s['id']=='F01');URL=f['url_o_identificador']
    CTX.update(fuente_id=f['id'],fuente_autores=f['autor_institucion'],fuente_titulo=f['titulo'],fuente_fecha_edicion=f['fecha_edicion'],fuente_anio=f['fecha_edicion'][:4],fuente_url=URL,fuente_consulta=f['consulta'])
    observed=Fraction(stats(principal)['media']) in principal
    CTX['media_observada']=T('comun.media_observada' if observed else 'comun.media_no_observada')

def board_rows():
    rows=[[s.format_map(CTX) for s in CONTENT['textos']['comun']['tabla_pizarra']]]
    for name in ('base','principal','aumentado'):
        rows.append([CTX[name+'_mayor']+' min'+(T('comun.caso_pedido') if name=='principal' else '')]+[CTX[name+'_'+k]+' min' for k in ('suma','media','mediana')])
    return rows

def notebook_rows():
    return [CONTENT['textos']['comun']['tabla_cuaderno']]+[[CTX[name+'_lista']]+[CTX[name+'_'+k] for k in ('n','suma','media','mediana')] for name in ('base','principal','aumentado','retirado')]

def markdown_view():
    lines=['<!-- VISTA DERIVADA: editar contenido.json y regenerar. -->','# '+META['titulo'],'',T('comun.titulo'),'',f"Tema: {META['id']} · Versión: {META['version']} · Revisión: {META['fecha_revision']}",'','## Alcance',META['alcance'],'','Cada sección referencia bloques consumidos por los PDF. Los textos de pizarra y cuaderno pueden tener distinta extensión: su correspondencia conceptual requiere revisión manual. Las referencias compartidas usan una sola definición.']
    for section in CONTENT['secciones']:
        lines+=['','## '+section['id']+' · '+section['titulo'],'']
        lines+=['\n\n'.join('**'+ref+'**: '+T(ref) for ref in section['bloques'])]
        if section['id']=='C04':
            rows=notebook_rows();lines+=['','| '+' | '.join(rows[0])+' |','|---|---:|---:|---:|---:|']+['| '+' | '.join(row)+' |' for row in rows[1:]]
    lines+=['','## Fuentes']
    for source in SOURCES:
        lines+=['',f"{source['id']}. {source['autor_institucion']}. {source['titulo']}. Edición: {source['fecha_edicion']}. {source['url_o_identificador']}",f"Consulta: {source['consulta']}. Alcance leído: {source['alcance_leido']}",source['limites']]
    lines+=['','## Límites de verificación','']+['- '+s for s in META['limites']]
    (ROOT/'contenido.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def calculations():
    write_json(ROOT/'revision/calculos.json',{'metodo':'Aritmética racional exacta con Fraction(str(numero)); datos JSON de hasta dos decimales, sin redondeo binario previo.','resultados':{name:stats(v) for name,v in SCENARIOS.items()},'cambio_media':CTX['cambio_media'],'cambio_media_ejercicio':CTX['cambio_media_ejercicio']})

INPUTS=['contenido.json','fuentes.json','mapa.json','cobertura.json','editables/generar.py','editables/probar_regresion.py','editables/README.md']
OUTPUTS=['salidas/pizarra.pdf','salidas/cuaderno.pdf','contenido.md','revision/calculos.json']
def snapshot():
    return {'entradas':[{'ruta':r,'sha256':sha(ROOT/r)} for r in INPUTS],'salidas':[{'ruta':r,'sha256':sha(ROOT/r)} for r in OUTPUTS],'entorno':{'python':sys.version.split()[0],'reportlab':reportlab.Version,'tipografias':FONT_INFO}}

def manifest(refresh=False):
    generation=snapshot();audit_path=ROOT/'revision/auditoria.json'
    if refresh:
        audit=read_json(audit_path)
        if audit.get('generacion_verificada')!=generation:raise ValueError('La auditoría no corresponde a los bytes actuales. Regenerar y revisar de nuevo.')
    else:
        audit={'fecha':META['fecha_revision'],'version':META['version'],'generacion_verificada':None,'contenido':{'estado':'pendiente','evidencia':'La generación no constituye una auditoría; revisar resultados y fuentes.'},'visual':{'estado':'pendiente','evidencia':'Renderizar e inspeccionar ambos PDF de esta generación.'},'correspondencia':{'estado':'pendiente','evidencia':'Revisar fuente canónica, mapa, cobertura y ambas salidas.'},'reproduccion':{'estado':'pendiente','evidencia':'Ejecutar la regresión en una copia temporal.'},'archivo':{'estado':'pendiente','evidencia':'Verificar inventario y hashes.'},'limites':META['limites']}
        write_json(audit_path,audit)
    reviewed=audit.get('generacion_verificada')==generation and all(audit.get(k,{}).get('estado')=='aprobada' for k in ('contenido','visual','correspondencia','reproduccion','archivo'))
    pending=[] if reviewed else ['Revisar generación actual y completar auditorías independientes.']
    functions={'contenido.json':'Única fuente canónica de datos, textos, síntesis e identidad','contenido.md':'Vista derivada; no editar','fuentes.json':'Registro de evidencia consultada','mapa.json':'Conceptos, relaciones y remisiones','cobertura.json':'Cobertura de la entrada y destino conceptual','editables/generar.py':'Composición y generación desde el contenido canónico','editables/probar_regresion.py':'Prueba de propagación en copia temporal','editables/README.md':'Dependencias y comandos reproducibles','salidas/pizarra.pdf':'Lienzo A1 horizontal conectado','salidas/cuaderno.pdf':'Tres páginas Carta con respuesta separada','revision/calculos.json':'Resultados calculados desde los datos canónicos','revision/estructura.json':'Revisión técnica de los PDF finales','revision/auditoria.json':'Evidencia de revisión, separada de la generación','revision/regresion.json':'Resultado de la prueba de propagación','CAMBIOS.md':'Historial de correcciones','INDICE.md':'Índice local'}
    files=[{'ruta':r,'funcion':functions.get(r,'Renderizado de revisión visual'),'sha256':sha(ROOT/r)} for r in sorted(functions) if (ROOT/r).is_file()]
    result={**{k:META[k] for k in ('id','titulo','version','version_skill','fecha_revision','alcance','entradas')},'schema_version':'1.2','contenido_canonico':'contenido.json','vista_contenido':'contenido.md','estado':'revisado' if reviewed else 'borrador','archivos':files,'generacion':generation,'reproduccion':{'comando':'python3 editables/generar.py','regresion':'python3 editables/probar_regresion.py','dependencias':['Python 3','reportlab','pypdf para la prueba; PyMuPDF/Poppler para revisión visual','DejaVu Sans, o Bitstream Vera de ReportLab']},'auditoria':{**{k:audit[k] for k in ('contenido','visual','correspondencia','reproduccion','archivo')},'generacion_verificada':audit.get('generacion_verificada')},'pendientes':pending,'goodnotes':{'estado':'no_importado','evidencia':'Piloto interno; no solicitado.'},'destino':'Piloto interno de validación; no publicado por este generador.','limites':META['limites']}
    write_json(ROOT/'manifest.json',result)
class Draw:
    def __init__(self,c,w,h): self.c,self.w,self.h=c,w,h
    def text(self,text,x,y,size=12,bold=False,color=INK):
        self.c.setFillColor(color);self.c.setFont(BOLD if bold else NORMAL,size); self.c.drawString(x,self.h-y-size,text)
    def p(self,text,x,y,w,size=11.5,leading=None,color=INK,bold=False):
        sty=ParagraphStyle('body',fontName=BOLD if bold else NORMAL,fontSize=size,leading=leading or size*1.28,textColor=color,spaceAfter=0)
        p=Paragraph(text,sty);ww,hh=p.wrap(w,10000);p.drawOn(self.c,x,self.h-y-hh);return hh
    def box(self,x,y,w,h,fill=LIGHT):
        self.c.setFillColor(fill);self.c.setStrokeColor(LINE);self.c.setLineWidth(0.8);self.c.roundRect(x,self.h-y-h,w,h,8,fill=1,stroke=1)
    def line(self,x1,y1,x2,y2,color=LINE,width=1):
        self.c.setStrokeColor(color);self.c.setLineWidth(width);self.c.line(x1,self.h-y1,x2,self.h-y2)
    def arrow(self,points,label=None,lx=None,ly=None,size=16):
        c=self.c;c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(2)
        p=c.beginPath();p.moveTo(points[0][0],self.h-points[0][1])
        for x,y in points[1:]:p.lineTo(x,self.h-y)
        c.drawPath(p)
        x,y=points[-1];px,py=points[-2];import math
        angle=math.atan2(y-py,x-px);length=12
        path=c.beginPath();path.moveTo(x,self.h-y)
        for a in [angle+2.65,angle-2.65]:path.lineTo(x+length*math.cos(a),self.h-(y+length*math.sin(a)))
        path.close();c.drawPath(path,fill=1,stroke=0)
        if label:self.text(label,lx,ly,size,color=BLUE)
    def table(self,rows,x,y,widths,size=11,padding=10):
        st=ParagraphStyle('t',fontName=NORMAL,fontSize=size,leading=size*1.2,textColor=INK)
        data=[[Paragraph(str(cell),st) for cell in row] for row in rows]
        t=Table(data,colWidths=widths,rowHeights=None,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('TEXTCOLOR',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),('LINEBELOW',(0,0),(-1,0),1,BLUE),('LINEBELOW',(0,1),(-1,-1),.4,LINE)]))
        _,hh=t.wrap(sum(widths),10000);t.drawOn(self.c,x,self.h-y-hh);return hh

def board():
    w,h=landscape(A1);c=canvas.Canvas(str(OUT/'pizarra.pdf'),pagesize=(w,h),invariant=1);c.setTitle(T('pizarra.t73'));d=Draw(c,w,h)
    d.text(T('comun.titulo'),64,56,55,True,BLUE)
    d.text(T('pizarra.t75'),66,135,30)
    d.text(T('pizarra.t76'),66,188,21)
    # Three core nodes, read from the data outwards
    d.box(64,300,650,390)
    d.text(T('pizarra.t79'),88,324,30,True,BLUE)
    d.p(T('pizarra.t80'),88,378,595,23)
    d.text(T('pizarra.t81'),88,461,25,True)
    d.text(T('pizarra.t82'),88,510,35,True,BLUE)
    d.p(T('pizarra.t83'),88,574,590,21)
    d.text(T('pizarra.t84'),88,655,15)
    d.box(868,315,650,310,PALE)
    d.text(T('pizarra.inicio'),894,279,15,True,BLUE)
    d.text(T('pizarra.t86'),894,340,28,True,BLUE)
    for i,v in enumerate(SCENARIOS['principal']):
        xx=895+i*120
        if i==2:d.box(xx-7,407,98,76,LIGHT)
        number=fmt(v);size=min(40,40*84/max(84,pdfmetrics.stringWidth(number,BOLD,40)))
        d.text(number,xx,419,size,True,BLUE if i==2 else INK)
        d.text(str(i+1)+'°',xx+15,493,19)
    d.p(T('pizarra.t92'),894,550,590,21)
    d.box(1672,300,648,390)
    d.text(T('pizarra.t94'),1696,324,30,True,BLUE)
    d.p(T('pizarra.t95'),1696,378,595,23)
    d.text(T('pizarra.t96'),1696,461,25,True)
    d.text(T('pizarra.t97'),1696,510,35,True,BLUE)
    d.p(T('pizarra.t98'),1696,574,590,21)
    d.text(T('pizarra.t99'),1696,655,15)
    d.arrow([(868,465),(714,465)],T('pizarra.flecha100'),747,417,18)
    d.arrow([(1518,465),(1672,465)],T('pizarra.flecha101'),1540,417,18)
    # Main comparison connected to same observations
    d.arrow([(1193,625),(1193,784)],T('pizarra.flecha103'),1215,703,19)
    d.box(605,785,1174,370)
    d.text(T('pizarra.t105'),629,810,25,True,BLUE)
    rows=board_rows()
    d.table(rows,629,870,[500,200,200,220],21)
    d.p(T('pizarra.t108'),629,1080,1115,21)
    # Distinct side notes explain questions and the parity condition
    d.arrow([(390,690),(390,787)],T('pizarra.pregunta'),408,733,16)
    d.text(T('pizarra.t110'),66,824,25,True,BLUE)
    d.p(T('pizarra.t111'),66,878,470,22)
    d.arrow([(1996,690),(1996,787)],T('pizarra.paridad'),2014,733,16)
    d.text(T('pizarra.t112'),1840,824,25,True,BLUE)
    d.p(T('pizarra.t113'),1840,878,472,22)
    d.p(T('pizarra.t114'),1840,1035,472,20)
    d.text(T('pizarra.t115'),1840,1178,18,color=BLUE)
    # Limits and exercise, connected under comparison
    d.arrow([(800,1155),(800,1216),(430,1216),(430,1240)],T('pizarra.flecha117'),435,1173,18)
    d.arrow([(1193,1155),(1193,1240)],T('pizarra.flecha118'),1215,1188,19)
    d.text(T('pizarra.t119'),66,1263,26,True,BLUE)
    d.p(T('pizarra.t120'),66,1320,695,21)
    d.p(T('pizarra.t121'),66,1473,695,20)
    d.text(T('pizarra.t122'),880,1263,26,True,BLUE)
    d.p(T('pizarra.t123'),880,1310,690,19)
    d.text(T('pizarra.t124'),880,1451,16,color=BLUE)
    for yy in [1500,1540,1580]:d.line(880,yy,1570,yy,width=.6)
    d.text(T('pizarra.t125'),1680,1263,26,True,BLUE)
    d.p(T('pizarra.t126'),1680,1320,610,21)
    for yy in [1400,1450,1500]:d.line(1680,yy,2298,yy)
    d.line(64,h-83,w-64,h-83)
    d.text(T('pizarra.t129'),66,h-70,15)
    d.text(T('pizarra.t130'),66,h-44,14)
    c.linkURL(URL,(64,20,1600,60),relative=0,thickness=0)
    c.save()

def head(d,num,title,sub):
    d.text(T('comun.titulo'),55,42,10,True,BLUE)
    d.text(title,55,66,23,True,BLUE)
    d.p(sub,55,104,500,11,color=INK)
    d.line(55,137,557,137)
    d.line(55,746,557,746)
    d.text(T('comun.pie'),55,756,9)
    d.text(f'{num} / 3',528,756,9)

def notes(d,y=644,title=None):
    title=title or T('cuaderno.notas')
    d.text(title,55,y,10,True,BLUE)
    for yy in [y+30,y+55,y+80]:d.line(55,yy,557,yy,width=.4)

def notebook():
    w,h=letter;c=canvas.Canvas(str(OUT/'cuaderno.pdf'),pagesize=letter,invariant=1);c.setTitle(T('cuaderno.t148'))
    d=Draw(c,w,h);head(d,1,T('cuaderno.pagina1_titulo'),T('cuaderno.pagina1_subtitulo'))
    d.p(T('cuaderno.t150'),55,155,502)
    d.text(T('cuaderno.t151'),55,210,16,True,BLUE)
    d.p(T('cuaderno.t152'),55,239,502)
    d.box(55,300,502,106)
    d.p(T('cuaderno.t154'),70,310,472,11.5,leading=22)
    d.p(T('cuaderno.t155'),55,420,502)
    d.text(T('cuaderno.t156'),55,474,16,True,BLUE)
    d.p(T('cuaderno.t157'),55,505,502,11)
    d.p(T('cuaderno.t158'),55,574,502,11)
    notes(d,648)
    c.showPage()
    d=Draw(c,w,h);head(d,2,T('cuaderno.pagina2_titulo'),T('cuaderno.pagina2_subtitulo'))
    rows=notebook_rows()
    d.table(rows,55,153,[234,34,72,77,85],11,padding=4)
    d.text(T('cuaderno.t164'),55,267,9)
    d.p(T('cuaderno.t165'),55,288,502,11,leading=14)
    d.text(T('cuaderno.t166'),55,365,16,True,BLUE)
    d.p(T('cuaderno.t167'),55,393,502,11,leading=14)
    d.p(T('cuaderno.t168'),55,451,502,11,leading=14)
    d.box(55,546,502,187,PALE)
    d.p(T('cuaderno.t170'),68,557,476,11,leading=15)
    
    for yy in [641,667,693,719]:d.line(70,yy,540,yy,width=.4)
    c.showPage()
    d=Draw(c,w,h);head(d,3,T('cuaderno.pagina3_titulo'),T('cuaderno.pagina3_subtitulo'))
    d.text(T('cuaderno.t175'),55,154,16,True,BLUE)
    d.p(T('cuaderno.t176'),55,186,502)
    d.p(T('cuaderno.t177'),55,238,502)
    d.p(T('cuaderno.t178'),55,306,502)
    d.text(T('cuaderno.t179'),55,367,16,True,BLUE)
    d.p(T('cuaderno.t180'),55,397,502,11)
    d.text(T('cuaderno.t181'),55,493,16,True,BLUE)
    d.p(T('cuaderno.t182'),55,523,502,10)
    d.p(T('cuaderno.enlace_fuente'),55,579,502,10)
    d.p(T('cuaderno.t184'),55,602,502,10)
    notes(d,638,T('cuaderno.pregunta_final'))
    # Only one annotation line fits in footer-safe area
    c.save()

def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--font-dir',type=Path,help='Carpeta con DejaVuSans.ttf/DejaVuSans-Bold.ttf o Vera.ttf/VeraBd.ttf')
    parser.add_argument('--manifest-only',action='store_true',help='Actualizar inventario tras auditoría externa con snapshot coincidente; no genera ni aprueba.')
    args=parser.parse_args();load(args.root);configure_fonts(args.font_dir)
    if not args.manifest_only:
        # Solo los consumidores PDF acreditan uso. El Markdown se deriva después.
        final_out=OUT
        with TemporaryDirectory(prefix='media-mediana-render-') as temporary:
            OUT=Path(temporary);USED_TEXTS.clear();board();notebook()
            declared={ref for section in CONTENT['secciones'] for ref in section['bloques']}
            declared|={group+'.'+key for group in ('pizarra','cuaderno','compartidos') for key in CONTENT['textos'].get(group,{})}
            unused=declared-USED_TEXTS
            if unused:raise ValueError('Bloque declarado no utilizado por ningún PDF: '+', '.join(sorted(unused)))
            for name in ('pizarra.pdf','cuaderno.pdf'):shutil.copyfile(OUT/name,final_out/name)
        OUT=final_out;markdown_view();calculations()
    manifest(refresh=args.manifest_only)
    print('Inventario actualizado.' if args.manifest_only else 'Generados ambos PDF y vista derivada. Auditorías pendientes.')
if __name__=='__main__':main()
