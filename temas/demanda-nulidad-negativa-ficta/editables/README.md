# Regenerar los dos formatos

El único texto editable es `../contenido.json`. `contenido.md` es una vista
generada; no se edita por separado. Las fuentes se mantienen en `fuentes.json`.

Desde la carpeta del tema:

```bash
python3 editables/generar.py .
python3 editables/generar.py . --self-test
```

Requiere Python 3.9 o superior y ReportLab 5.0.0. Emplea fuentes PDF estándar
Helvetica y Helvetica-Bold; no depende de una fuente instalada ni de un servicio
de diseño. La pizarra es A1 horizontal; el cuaderno tiene páginas Carta originales,
con cuerpo 11.5 pt y espacio inferior para escribir.

## Cambios sustantivos

Las síntesis son intencionales y diferentes de los desarrollos. Para evitar que
una edición deje una síntesis desactualizada, el canónico registra una huella de
`conceptos` y `reglas_criticas`. Cambiar cualquiera de estos campos detiene la
generación. Se debe revisar la correspondencia de todas las síntesis afectadas,
condiciones, excepciones y premisas. Solo después se obtiene la huella:

```bash
python3 editables/generar.py . --huella
```

Se escribe ese resultado en `revision_sintesis.sha256`, con una nota real de la
revisión en `revision_sintesis.nota`. Imprimir la huella no certifica contenido ni
es aprobación automática. Los datos variables se insertan mediante tokens como
`{{R01}}`, cuyo valor y unidad se leen de `reglas_criticas`.

El ensayo de continuidad modifica en memoria una explicación sustantiva, un dato
compartido y una premisa central. Los tres deben detenerse con un mensaje de
revisión necesaria, antes de generar un PDF incoherente. También comprueba el
rechazo de un campo no consumido. No altera los archivos del tema.

## Composición y auditoría

Cada concepto aparece una vez en una página del cuaderno y una vez en una zona
del lienzo. El generador rechaza destinos inexistentes, fuentes inexistentes,
campos desconocidos y texto que desborda; no reduce la tipografía para ocultarlo.
Las fuentes completas se distribuyen explícitamente entre páginas de referencias.

`mapa.json` aporta las conexiones. Las flechas entre zonas usan relaciones reales
cuando existen; una conexión puramente organizativa se rotula «Ruta de lectura».
El archivo abierto `generar.py` define posiciones, estilos y líneas; no contiene
explicaciones jurídicas ni cifras normativas.

Cada ejecución correcta registra los hashes reales de entradas y salidas y deja
las auditorías pendientes. Deben renderizarse y abrirse todas las páginas y todas
las zonas A1, comprobarse grises y correspondencia, ejecutarse el validador de la
skill y aprobarse la generación exacta. La generación no aprueba su propio trabajo.
