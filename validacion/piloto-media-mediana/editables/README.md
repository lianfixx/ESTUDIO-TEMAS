# Regeneración del piloto 1.2.0

Desde la carpeta del tema: `python3 editables/generar.py`.

`contenido.json` (schema 1.1) es el canónico. Edita los valores en `datos` y las explicaciones en `textos`: por ejemplo `textos.compartidos.elegir` cambia la explicación de elección en ambas composiciones, porque `pizarra.t111` y `cuaderno.t167` lo referencian mediante `{"ref":"compartidos.elegir"}`. `secciones[].bloques` solo agrupa referencias a bloques realmente dibujados; no almacena una segunda explicación. La generación comprueba consumo por los PDF antes de reemplazarlos: un bloque declarado sin usar o una referencia inexistente detiene la operación. La vista Markdown no cuenta como consumo PDF.

Migración desde contenido schema 1.0: trasladar los matices de `secciones[].parrafos` a los bloques de `textos` que se dibujan, reemplazar `parrafos` por `bloques` y subir el schema a 1.1. El campo antiguo se rechaza explícitamente aunque el schema se cambie: nunca se ignora. No basta añadir una clave de texto para ampliar el diseño; si no cabe en un bloque existente, adaptar su consumidor de composición y revisar las salidas. Los bloques propios de cada formato pueden tener distinta extensión; pertenecer a la misma sección no demuestra equivalencia: exige revisión semántica manual. En esta migración se conservaron en el cuaderno las unidades de la fórmula, la regla par precisa, los datos repetidos, los límites de inferencia y la diferencia entre dato alto, error y atipicidad formal.

`contenido.md` es una vista derivada: no editar. `fuentes.json` aporta bibliografía; `mapa.json` (schema 1.0) y `cobertura.json` se validan antes de generar. Versiones e identidad del mapa deben coincidir con el canónico. El código compone, calcula y deriva el sentido de los cambios; no mantiene párrafos docentes alternativos.

## Alcance del piloto

Admite cinco duraciones por ejemplo, números JSON finitos de 0 a 999,99 y hasta dos decimales, sin booleanos. Principal y ejercicio requieren un máximo estricto por la premisa del traslado largo; se admiten repeticiones centrales. La aritmética parte de `Fraction(str(numero))`: evita restar flotantes antes de convertir; los resultados decimales se muestran sin redondeo. Se sustituye un máximo sin alterar los valores centrales; `aumentado` debe ser al menos el máximo principal. Las entradas incompatibles se rechazan con motivo antes de reemplazar salidas. Base y sustitución del ejercicio pueden producir aumento, descenso o igualdad: el texto deriva de la diferencia real. Retirar puede cambiar o conservar la mediana, incluso con repeticiones. Este soporte numérico no garantiza que cualquier explicación editada quepa en el diseño fijo: revisar todas las páginas al cambiarla. No es un generador general de estadística.

## Dependencias y salidas

Python 3 y `reportlab`. Usa DejaVu Sans del sistema o Bitstream Vera incluida en ReportLab, con aviso. `--font-dir RUTA` o `PIZARRAS_FONT_DIR` permiten elegir las fuentes (`DejaVuSans.ttf` y `DejaVuSans-Bold.ttf`, o `Vera.ttf` y `VeraBd.ttf`). `--root RUTA` permite trabajar en una copia. No requiere servicios remotos. El entorno y los hashes de las fuentes se registran sin rutas absolutas.

Produce pizarra A1 horizontal, cuaderno de tres páginas Carta, Markdown derivado y cálculos. El PDF es determinista en idéntico entorno. Cada regeneración deja el manifiesto schema 1.2 en borrador, cinco auditorías pendientes y `generacion_verificada: null` tanto en `manifest.auditoria` como en `revision/auditoria.json`, aunque coincidan los bytes con una revisión previa.

## Regresión

Instalar `pypdf` y ejecutar `python3 editables/probar_regresion.py`. Usa una copia temporal. Muta una explicación sustantiva compartida, los datos, versión, bibliografía y URL; verifica ambos PDF y Markdown. Comprueba direcciones inversas y nulas, repetidos, decimales exactos, rechazo de valores no finitos/booleanos/fuera de soporte y textos huérfanos o antiguos. También verifica el contrato de snapshots. Los casos modificados son pruebas funcionales; no material adicional de estudio ni una revisión visual automática.

## Revisión final

Renderizar todas las páginas, el lienzo y sus zonas en una carpeta temporal fuera del repositorio. Ejemplo: `pdftoppm -r 100 -png salidas/cuaderno.pdf /tmp/cuaderno` y `pdftoppm -r 40 -png salidas/pizarra.pdf /tmp/pizarra`. Inspeccionar color, grises, fórmulas, remisiones, enlaces y espacio de anotación. No conservar PNG ni pycache en el paquete.

Registrar evidencia real en `revision/auditoria.json`: `generacion_verificada` debe ser idéntico a `manifest.generacion`. Después, `python3 editables/generar.py --manifest-only` actualiza inventario y copia el snapshot al campo obligatorio `manifest.auditoria.generacion_verificada`. Rechaza snapshot ausente, nulo u obsoleto; no aprueba estados pendientes. Solo cinco auditorías aprobadas y snapshot coincidente permiten `estado: revisado`. Cambiar cualquier entrada o salida exige regenerar y revisar de nuevo.

Límites conservados: sin impresión física, sin importación en Goodnotes, sin nueva lectura completa del libro y sin datos empíricos.
