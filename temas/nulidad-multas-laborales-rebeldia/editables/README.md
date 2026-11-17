# Regenerar los dos formatos

El único texto editable es `../contenido.json`. `contenido.md` es una vista generada; no se edita por separado. Las fuentes están en `fuentes.json` y las relaciones y remisiones en `mapa.json`.

Desde la carpeta del tema:

```bash
python3 editables/generar.py .
```

Requiere Python 3.9 o superior, Playwright para Python con Chromium, pypdf, fontTools, y las tipografías Inter y Caladea instaladas en el sistema. Inter se convierte a TrueType al generar, para que el PDF no lleve fuentes Type 3. La pizarra es A1 horizontal; el cuaderno usa páginas Carta con margen derecho de anotación.

## Qué comprueba el generador

- Que cada concepto tenga sus campos, una zona existente y un apartado igual a su título.
- Que toda marca de fuente exista en `fuentes.json` y que `mapa.json` coincida con el contenido.
- Que ningún texto desborde su caja ni un rótulo de flecha tape una zona. No reduce la letra para esconderlo: se detiene.
- Que cada concepto quede en la página del cuaderno que declara `contenido.json`, porque la pizarra remite a esas páginas.

Cada generación pública registra los hashes en `manifest.json` y deja las auditorías pendientes. La generación no aprueba su propio trabajo.

## Edición privada

La edición pública sustituye las variables `{{...}}` con los valores de `contenido.json`, que no identifican al cliente. La edición privada usa un archivo con los valores reales, que no se guarda en este repositorio:

```bash
python3 editables/generar.py . --privado RUTA/datos_privados.json --salida RUTA_FUERA_DEL_REPOSITORIO
```

El generador se niega a escribirla dentro del tema y no toca el manifiesto ni la vista Markdown.

## Flechas

Las flechas de la pizarra salen de las relaciones de `mapa.json` con `"lienzo": true`. Su rótulo es el campo `etiqueta`; la explicación completa está en `relacion` y `justificacion`.
