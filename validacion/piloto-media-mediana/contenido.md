<!-- VISTA DERIVADA: editar contenido.json y regenerar. -->
# Media y mediana: qué cambia con un traslado largo

MEDIA Y MEDIANA

Tema: media-mediana · Versión: 1.2.0 · Revisión: 2026-10-22

## Alcance
Introducción a media y mediana con tiempos hipotéticos, sustituciones y eliminación; fórmulas explicadas, límites y ejercicio con respuesta separada.

Cada sección referencia bloques consumidos por los PDF. Los textos de pizarra y cuaderno pueden tener distinta extensión: su correspondencia conceptual requiere revisión manual. Las referencias compartidas usan una sola definición.

## C01 · Dos preguntas sobre el centro

**pizarra.t86**: C01 · LOS MISMOS DATOS

**pizarra.t92**: n = 5 traslados. Cada observación tiene el mismo peso.

**cuaderno.t150**: <b>Ejemplo hipotético:</b> tiempos de 10, 15, 20, 25, 80 minutos. Hay n = 5 traslados, con el mismo peso. No son una encuesta ni una predicción.

## C02 · Media: todas las magnitudes cuentan

**pizarra.t79**: C02 · MEDIA

**pizarra.t80**: Suma las duraciones y reparte el total entre los 5 traslados.

**pizarra.t81**: (10 + 15 + 20 + 25 + 80) / 5

**pizarra.t82**: 150 / 5 = 30 min

**pizarra.t83**: Usa todas las magnitudes. El total puede recuperarse: 5 × 30 = 150 min.

**cuaderno.t151**: C02 · Media: repartir el total

**cuaderno.t152**: La media aritmética suma todas las duraciones y divide entre la cantidad de traslados. Responde a cuánto tocaría por traslado si repartiéramos el total por igual. [F01, §2.5]

**cuaderno.t154**: <b>Media = (x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>n</sub>) / n</b><br/>x<sub>i</sub>: duración de cada traslado; n: cantidad de datos.<br/>Suma y media se expresan en minutos; n es un conteo.<br/><b>(10 + 15 + 20 + 25 + 80) / 5 = 150 / 5 = 30 min</b>

**cuaderno.t155**: Ningún traslado duró 30 min: la media no necesita ser un dato observado. El total se recupera: 5 × 30 = 150 min.

## C03 · Mediana: orden y posición

**pizarra.t94**: C03 · MEDIANA

**pizarra.t95**: Ordena de menor a mayor y ubica el centro.

**pizarra.t96**: Posición: (5 + 1) / 2 = 3

**pizarra.t97**: Dato central = 20 min

**pizarra.t98**: 2 valores menores y 2 mayores. La posición 3 no significa 3 minutos.

**pizarra.t112**: C03 · SI n ES PAR

**pizarra.t113**: Promedia los valores de las posiciones n/2 y n/2 + 1.<br/><br/>No promedies las posiciones.

**cuaderno.t156**: C03 · Mediana: encontrar el centro

**cuaderno.t157**: Ordena de menor a mayor. Con n <b>impar</b>, toma el valor de la posición <b>(n + 1) / 2</b>. Aquí (5 + 1) / 2 = 3; el valor central es <b>20 min</b>. La posición 3 no es una duración. [F01, §2.5]

**cuaderno.t158**: Con n <b>par</b>, promedia los valores de las posiciones <b>n/2</b> y <b>n/2 + 1</b>; el + 1 pertenece a la segunda posición. Con 10, 15, 20, 25: mediana = (15 + 20) / 2 = <b>17,5 min</b>. Puede no ser un dato observado. [F01, §2.5, ej. 2.26]

**cuaderno.t179**: Una precisión sobre la mediana

**cuaderno.t180**: Con datos repetidos, al menos la mitad queda en o por debajo de la mediana y al menos la mitad en o por encima. Esto se sigue de ordenar. La mediana resiste la magnitud de un extremo mientras no cambien los valores centrales; no es inmune a cualquier cambio. Al retirar 80, la mediana cambia de 20 a 17,5 min.

## C04 · Qué cambia por el dato alto

**pizarra.t105**: C04 · SUSTITUIR EL MÁXIMO SIN MOVER EL CENTRO

**pizarra.t108**: De 30 a 80, el total aumenta 50 min: la media sube 50/5 = 10 min. La mediana sigue en 20 porque no cambia el dato central.

**pizarra.t114**: Retirar 80 cambia n a 4: media = 70 / 4 = 17,5 min; mediana = (15 + 20) / 2 = 17,5 min.

**pizarra.t115**: Retirar ≠ sustituir

**cuaderno.t164**: Suma, media y mediana en minutos. Cálculos propios.

**cuaderno.t165**: Con n fijo y una sustitución: <b>cambio de media = cambio del dato / n</b>; se deduce de la fórmula de media. De 30 a 80, el total aumenta 50 min; la media sube 50/5 = 10 min. La mediana sigue en 20. Retirar 80 cambia n: la mediana cambia de 20 a 17,5 min. La fórmula con n fijo ya no se aplica sin ajuste.

| Escenario | n | Suma | Media | Mediana |
|---|---:|---:|---:|---:|
| 10, 15, 20, 25, 30 | 5 | 100 | 20 | 20 |
| 10, 15, 20, 25, 80 | 5 | 150 | 30 | 20 |
| 10, 15, 20, 25, 180 | 5 | 250 | 50 | 20 |
| 10, 15, 20, 25 | 4 | 70 | 17,5 | 17,5 |

## C05 · Cómo elegir y qué no dicen

**pizarra.t110**: C05 · ¿PARA QUÉ?

**pizarra.t111**: Para repartir el tiempo total, usa la media; para ubicar el centro, la mediana. No hay una ganadora universal. Informar ambas permite compararlas: 30 frente a 20 min. [F01, §2.5, ej. 2.27]

**pizarra.t119**: C05 · LÍMITES QUE IMPORTAN

**pizarra.t120**: 80 es un dato alto; no demuestra un error. No se elimina por elevar la media.<br/><br/>La mediana resiste estos cambios mientras se conserve el centro; no es inmutable.

**pizarra.t121**: Ninguna medida describe toda la variación ni permite generalizar desde 5 tiempos hipotéticos. Conserva el contexto y la lista de datos.

**cuaderno.t166**: C05 · Elegir sin perder contexto

**cuaderno.t167**: Para repartir el tiempo total, usa la media; para ubicar el centro, la mediana. No hay una ganadora universal. Informar ambas permite compararlas: 30 frente a 20 min. [F01, §2.5, ej. 2.27]

**cuaderno.t168**: 80 es un <b>dato alto</b>: no prueba error ni atipicidad formal sin criterio y contexto. No lo retires solo por elevar la media. Ninguna medida describe toda la variación: conserva los datos, de 10 a 80 min (separación: 70 min). Son 5 tiempos hipotéticos: no permiten generalizar a una población ni predecir el siguiente viaje.

**cuaderno.t184**: Los tiempos de traslado de estas páginas son ejemplos hipotéticos. No son datos empíricos ni predicciones.

## C06 · Ejercicio breve

**pizarra.t122**: C06 · PRUEBA TÚ

**pizarra.t123**: 12, 16, 20, 24, 68 min.<br/>Calcula media y mediana. Luego sustituye 68 por 28: ¿qué cambia y por qué?<br/><br/>¿Que la mediana no cambie prueba que el traslado largo no importa?

**pizarra.t124**: Respuesta separada: cuaderno, pág. 3.

**cuaderno.t170**: <b>C06 · Ejercicio breve</b><br/>12, 16, 20, 24, 68 min. Calcula media y mediana. Sustituye 68 por 28: ¿qué cambia y por qué? ¿La mediana estable prueba que el traslado largo no importa?<br/><font color="#164A72">Respuesta en la página 3. Anota aquí tus pasos:</font>

## C07 · Respuesta separada

**cuaderno.t175**: Respuesta del ejercicio

**cuaderno.t176**: <b>1.</b> Suma = 12 + 16 + 20 + 24 + 68 = <b>140 min</b>.<br/>Media = 140/5 = <b>28 min</b>. Mediana = dato central = <b>20 min</b>.

**cuaderno.t177**: <b>2.</b> Al sustituir 68 por 28, la suma es <b>100 min</b>.<br/>Media = 100/5 = <b>20 min</b>. Mediana = <b>20 min</b>.<br/>La media baja 40/5 = 8 min; el valor central no cambia.

**cuaderno.t178**: <b>3.</b> No. La mediana no describe la magnitud del extremo ni el total. Un traslado más largo aumenta el total y la media si los demás se mantienen. Su importancia práctica depende de la pregunta.

## Fuentes

F01. Barbara Illowsky y Susan Dean; OpenStax, Rice University. Introductory Statistics 2e, §2.5: Measures of the Center of the Data. Edición: 2023-12-13. https://openstax.org/books/introductory-statistics-2e/pages/2-5-measures-of-the-center-of-the-data
Consulta: 2026-10-22. Alcance leído: Página abierta: definiciones y fórmulas de media; regla de mediana impar/par; ejemplos 2.26 y 2.27; datos bibliográficos. No se leyó íntegramente el libro. Prefacio abierto para institución y acceso.
Los cálculos, supuestos de traslado e inferencias didácticas son propios. La fuente no valida una población ni estos tiempos hipotéticos. Sin fuente inaccesible utilizada.

## Límites de verificación

- No se leyó el libro completo: secciones pertinentes y bibliografía de página abierta.
- No hay observaciones empíricas: todos los tiempos son hipotéticos.
- No se hizo impresión física; revisión de PDF renderizado en color y grises.
- No se comprobó importación en Goodnotes.
- No se conservaron copias íntegras de fuentes académicas; se guardó la referencia y el alcance leído.
