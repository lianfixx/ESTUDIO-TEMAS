<!-- VISTA DERIVADA: editar contenido.json y regenerar. -->
# Media y mediana: qué cambia con un traslado largo

MEDIA Y MEDIANA

Tema: media-mediana · Versión: 1.1.0 · Revisión: 2026-10-22

## Pregunta y alcance
¿Cómo resumen la media y la mediana los mismos tiempos, y por qué un dato alto influye de forma distinta? Nivel introductorio. Datos hipotéticos aportados: 10, 15, 20, 25, 80 minutos. Una observación por traslado, mismo peso para cada una, n = 5. No son una encuesta ni una predicción.

## C01 · Dos preguntas sobre el centro

La media aritmética suma los valores y divide entre su cantidad. La mediana ocupa el centro de la lista ordenada; con cantidad par se promedian los dos valores centrales. [F01, §2.5, párrafos iniciales y regla posterior a la nota]

En este ejemplo, la media responde a «¿cuánto tocaría por traslado si repartiéramos el tiempo total por igual?». La mediana responde a «¿qué duración queda en el centro al ordenar?». Estas son interpretaciones didácticas de las definiciones.

## C02 · Media: todas las magnitudes cuentan

Fórmula: media = (x₁ + x₂ + ... + xₙ) / n. xᵢ representa la duración de cada traslado; n, la cantidad de traslados. La suma y el resultado se expresan en minutos; n es un conteo. [F01, §2.5, definición y fórmulas de media]

Ejemplo: (10 + 15 + 20 + 25 + 80) / 5 = 150 / 5 = 30 min. Ningún traslado duró 30 min: la media no necesita ser un dato observado. El total se recupera como 5 × 30 = 150 min. Cálculo propio verificado.

## C03 · Mediana: orden y posición

Primero ordena de menor a mayor. Si n es impar, toma el valor en la posición (n + 1) / 2. Si n es par, calcula (valor en posición n/2 + valor en posición n/2 + 1) / 2; el «+ 1» pertenece a la segunda posición. La posición no es la duración. [F01, §2.5, regla de la mediana y ejemplo 2.26]

Aquí (5 + 1) / 2 = 3: el dato central es 20 min. Hay 2 datos menores y 2 mayores. Con repeticiones, no exijas mitades estrictamente menores y mayores: al menos la mitad está en o por debajo de la mediana y al menos la mitad en o por encima. Esta precisión se sigue de la regla de ordenación.

## C04 · Qué cambia por el dato alto

Comparación construida con n fijo: 10, 15, 20, 25, 30 suma 100 min y tiene media 20 min y mediana 20 min. Sustituir 30 por 80 añade 50 min al total. La media aumenta 50 / 5 = 10 min y pasa a 30. La mediana sigue en 20 porque el dato central no cambia. En general, con n fijo y una sola sustitución, cambio de media = cambio del dato / n. Es una consecuencia algebraica de C02.

Si 80 pasa a 180: suma 250, media 50 y mediana 20 min. La mediana es resistente a la magnitud de un extremo mientras no cambien las posiciones centrales; no es inmune a cualquier cambio. [F01, §2.5, párrafo inicial sobre extremos; aplicación calculada]

Retirar 80 es otra comparación: cambia n. La media es 70 / 4 = 17,5 min. La mediana es (15 + 20) / 2 = 17,5 min. No se puede aplicar sin ajuste la fórmula de cambio con n fijo. La mediana par puede no ser un dato observado.

| Escenario | n | Suma | Media | Mediana |
|---|---:|---:|---:|---:|
| 10, 15, 20, 25, 30 | 5 | 100 | 20 | 20 |
| 10, 15, 20, 25, 80 | 5 | 150 | 30 | 20 |
| 10, 15, 20, 25, 180 | 5 | 250 | 50 | 20 |
| 10, 15, 20, 25 | 4 | 70 | 17,5 | 17,5 |

## C05 · Cómo elegir y qué no dicen

Si interesa el reparto del tiempo total, usa la media y conserva el dato largo. Si interesa la posición central sin que domine su magnitud, la mediana es útil. Informar ambas muestra la diferencia: 30 frente a 20 min. No hay una medida universalmente superior; la elección responde a la pregunta. [F01, §2.5, definición y ejemplo 2.27; interpretación de este supuesto]

Llamamos a 80 «dato alto»: no lo declaramos error ni valor atípico formal sin criterio y contexto. No se debe retirarlo solo porque eleva la media. Los 5 valores son hipotéticos; no permiten concluir cómo se traslada una población ni predecir el siguiente viaje. Ninguna medida describe por sí sola toda la variación. Aquí conviene conservar también los datos: mínimo 10 y máximo 80 min, una separación de 70 min. Son límites del supuesto, no un análisis de población.

## C06 · Ejercicio breve

Otros 5 traslados hipotéticos duran 12, 16, 20, 24, 68 min.
1. Calcula media y mediana y muestra tus pasos.
2. Sustituye 68 por 28. ¿Qué cambia y por qué?
3. ¿Que la mediana no cambie demuestra que el traslado largo no importa?
Respuestas separadas: cuaderno, página 3. La pizarra no muestra la solución del ejercicio.

## C07 · Respuesta separada

1. Suma = 140 min. Media = 140 / 5 = 28 min. Mediana = dato central = 20 min.
2. Nueva suma = 100 min. Media = 100 / 5 = 20 min. Mediana = 20 min. La media baja (68 - 28) / 5 = 8 min; la posición central no cambia.
3. No. La mediana no describe la magnitud del extremo ni el total. El traslado largo sí aumenta el total y la media. Su importancia práctica depende de la pregunta.

## Síntesis de las composiciones

Los textos siguientes pertenecen al mismo contenido canónico; el código solo decide su disposición.

### Pizarra

**t73**: Media y mediana - Pizarra conectada

**t75**: ¿Qué cambia cuando un traslado dura mucho más?

**t76**: Ejemplo hipotético • tiempos en minutos • un dato por traslado

**t79**: C02 · MEDIA

**t80**: Suma las duraciones y reparte el total entre los 5 traslados.

**t81**: (10 + 15 + 20 + 25 + 80) / 5

**t82**: 150 / 5 = 30 min

**t83**: Usa todas las magnitudes. El total puede recuperarse: 5 × 30 = 150 min.

**t84**: [F01, §2.5] · Desarrollo: pág. 1

**t86**: C01 · LOS MISMOS DATOS

**t92**: n = 5 traslados. Cada observación tiene el mismo peso.

**t94**: C03 · MEDIANA

**t95**: Ordena de menor a mayor y ubica el centro.

**t96**: Posición: (5 + 1) / 2 = 3

**t97**: Dato central = 20 min

**t98**: 2 valores menores y 2 mayores. La posición 3 no significa 3 minutos.

**t99**: [F01, §2.5] · Desarrollo: pág. 1

**flecha100**: sumar

**flecha101**: ordenar

**flecha103**: cambiar solo el mayor

**t105**: C04 · CAMBIA LA MAGNITUD; LA MEDIANA SE CONSERVA

**t108**: De 30 a 80 se suman 50 min: la media sube 50 / 5 = 10 min. La mediana sigue en 20 porque no cambia el dato central.

**t110**: C05 · ¿PARA QUÉ?

**t111**: Total repartido: media.<br/><br/>Posición central: mediana.<br/><br/>En este caso, informar ambas hace visible la diferencia.

**t112**: C03 · SI n ES PAR

**t113**: Promedia los valores de las posiciones n/2 y n/2 + 1.<br/><br/>No promedies las posiciones.

**t114**: Retirar 80 cambia n a 4: media = 70 / 4 = 17,5 min; mediana = (15 + 20) / 2 = 17,5 min.

**t115**: Retirar ≠ sustituir

**flecha117**: se interpreta con límites

**flecha118**: practicar con otros datos

**t119**: C05 · LÍMITES QUE IMPORTAN

**t120**: 80 es un dato alto; no demuestra un error. No se elimina por elevar la media.<br/><br/>La mediana resiste estos cambios, pero no es inmutable: retirar un dato puede mover el centro.

**t121**: Ninguna medida describe toda la variación ni permite generalizar desde 5 tiempos hipotéticos. Conserva el contexto y la lista de datos.

**t122**: C06 · PRUEBA TÚ

**t123**: 12, 16, 20, 24, 68 min.<br/>Calcula media y mediana. Luego sustituye 68 por 28: ¿qué cambia y por qué?<br/><br/>¿Que la mediana no cambie prueba que el traslado largo no importa?

**t124**: Respuesta separada: cuaderno, pág. 3.

**t125**: TUS CONEXIONES

**t126**: ¿Qué pregunta resolverías con cada medida?

**t129**: F01 · Barbara Illowsky y Susan Dean; OpenStax, Rice University. Introductory Statistics 2e, §2.5: Measures of the Center of the Data (2023). Referencia y enlace: cuaderno, pág. 3.

**t130**: media-mediana · v1.1.0 · 2026-10-22 · Datos hipotéticos. Fórmulas completas y matices: cuaderno, págs. 1-3.

**inicio**: EMPIEZA AQUÍ

**pregunta**: según la pregunta

**paridad**: si cambia la cantidad

### Cuaderno

**t148**: Media y mediana - Cuaderno de estudio

**pagina1_titulo**: Dos maneras de resumir

**pagina1_subtitulo**: C01-C03 · El mismo conjunto, dos preguntas diferentes.

**t150**: <b>Ejemplo hipotético:</b> tiempos de 10, 15, 20, 25, 80 minutos. Hay n = 5 traslados y cada observación tiene el mismo peso.

**t151**: C02 · Media: repartir el total

**t152**: La media aritmética suma todas las duraciones y divide entre la cantidad de traslados. Responde a cuánto tocaría por traslado si repartiéramos el total por igual. [F01, §2.5]

**t154**: <b>Media = (x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>n</sub>) / n</b><br/>x<sub>i</sub> es cada duración; n es la cantidad de datos.<br/><b>(10 + 15 + 20 + 25 + 80) / 5 = 150 / 5 = 30 min</b>

**t155**: Ningún traslado duró 30 min: la media no necesita ser un dato observado. El total se recupera: 5 × 30 = 150 min.

**t156**: C03 · Mediana: encontrar el centro

**t157**: Ordena de menor a mayor. Con n <b>impar</b>, toma el valor de la posición <b>(n + 1) / 2</b>. Aquí (5 + 1) / 2 = 3; el valor central es <b>20 min</b>. La posición 3 no es una duración. [F01, §2.5]

**t158**: Con n <b>par</b>, toma los valores en las posiciones <b>n/2</b> y <b>n/2 + 1</b>; súmalos y divide entre 2. Con 10, 15, 20, 25: mediana = (15 + 20) / 2 = <b>17,5 min</b>. [F01, §2.5, ej. 2.26]

**pagina2_titulo**: Qué cambia por el dato alto

**pagina2_subtitulo**: C04-C06 · Sustituir conserva n; retirar lo cambia.

**t164**: Suma, media y mediana en minutos. Cálculos propios.

**t165**: Con n fijo: <b>cambio de media = cambio del dato / n</b>. De 30 a 80 se añaden 50 min; la media sube 50/5 = 10 min. La mediana no cambia porque el dato central sigue siendo 20. Retirar 80 cambia n y también la mediana.

**t166**: C05 · Elegir sin perder contexto

**t167**: Para el total repartido, sirve la media; para la posición central, la mediana. [F01, §2.5, ej. 2.27] No hay una ganadora universal. 80 es un <b>dato alto</b>, no un error demostrado: no lo retires solo por elevar la media.

**t168**: Ninguna describe toda la variación: los datos van de 10 a 80 min. 5 tiempos hipotéticos no permiten generalizar a una población.

**t170**: <b>C06 · Ejercicio breve</b><br/>12, 16, 20, 24, 68 min. Calcula media y mediana. Sustituye 68 por 28: ¿qué cambia y por qué? ¿La mediana estable prueba que el traslado largo no importa?<br/><font color="#164A72">Respuesta en la página 3. Anota aquí tus pasos:</font>

**pagina3_titulo**: Respuestas y fuentes

**pagina3_subtitulo**: C07 · Consulta esta página después de resolver el ejercicio.

**t175**: Respuesta del ejercicio

**t176**: <b>1.</b> Suma = 12 + 16 + 20 + 24 + 68 = <b>140 min</b>.<br/>Media = 140/5 = <b>28 min</b>. Mediana = dato central = <b>20 min</b>.

**t177**: <b>2.</b> Al sustituir 68 por 28, la suma es <b>100 min</b>.<br/>Media = 100/5 = <b>20 min</b>. Mediana = <b>20 min</b>.<br/>La media baja (68 - 28)/5 = <b>8 min</b>; la posición central no cambia.

**t178**: <b>3.</b> No. La mediana no describe la magnitud del extremo ni el total. El traslado largo sí aumenta el total y la media. Su importancia práctica depende de la pregunta.

**t179**: Una precisión sobre la mediana

**t180**: Con datos repetidos, al menos la mitad queda en o por debajo de la mediana y al menos la mitad en o por encima. Esto se sigue de ordenar los valores. Resistir el cambio de un extremo no significa ser inmutable: al retirar 80, nuestra mediana pasó de 20 a 17,5 min.

**t181**: Fuente académica abierta

**t182**: <b>F01.</b> Barbara Illowsky y Susan Dean; OpenStax, Rice University. <i>Introductory Statistics 2e, §2.5: Measures of the Center of the Data.</i> Edición: 2023-12-13. Definiciones, fórmulas, regla par/impar y ejemplos 2.26-2.27.

**t184**: Los tiempos de traslado de estas páginas son ejemplos hipotéticos. No son datos empíricos ni predicciones.

**pregunta_final**: Una pregunta que me queda

**notas**: Notas y conexiones

**enlace_fuente**: <link href="https://openstax.org/books/introductory-statistics-2e/pages/2-5-measures-of-the-center-of-the-data" color="#164A72"><u>Abrir la sección consultada</u></link> · Consulta: 2026-10-22.

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
