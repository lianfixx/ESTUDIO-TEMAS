# Auditoría profunda de Pizarras de estudio 1.1.0

Fecha: 22 de octubre de 2026. Resultado: defectos detectados corregidos y
comprobaciones finales aprobadas. No se detectaron pendientes que impidan usar
el método dentro del alcance revisado.

Se revisaron por separado el método de investigación, el diseño, la integridad
de archivos y la continuidad entre IA. Las revisiones independientes se
contrastaron con los archivos reales y con un piloto de estadística. No basta
con que las instrucciones describan bien el comportamiento: también se probó
que el generador y el validador lo cumplan.

## Hallazgos y correcciones

| Hallazgo comprobado | Efecto | Corrección y evidencia |
| --- | --- | --- |
| El generador inicial solo buscaba los IDs en Markdown; repetía textos y valores en el código. Cambiar el canónico dejaba los PDF iguales. | Otra IA podía editar los apuntes y entregar salidas obsoletas. | `contenido.json` es ahora el canónico y `contenido.md` una vista derivada. Datos y cálculos proceden del JSON; bibliografía y enlaces proceden de `fuentes.json`. La regresión modifica datos, texto, versión y fuente y comprueba su aparición real en ambos PDF. |
| La regeneración podía dejar hashes y auditorías anteriores. | Un archivo nuevo podía parecer revisado con evidencia antigua. | Registro de generación con hashes de entradas y salidas, actualización del inventario e invalidación de aprobaciones. La actualización posterior del manifiesto exige que la auditoría corresponda exactamente al registro actual; no aprueba por sí misma. |
| Registrar la lectura de una entrada no demostraba que sus puntos relevantes llegaran al material final. | Omisiones difíciles de detectar. | `cobertura.json` conecta cada punto con conceptos o documenta la exclusión. Lo pendiente sustantivo impide cerrar el paquete como revisado. |
| Título ambiguo sobre el centro, conexiones incompletas, remisión parcial y poco espacio de ejercicio en el piloto. | Podía confundirse la estabilidad de la mediana con la de cualquier medida y dificultarse el estudio. | Título explícito, inicio visible, conexiones útiles, remisión a páginas 1–3 y más líneas junto al ejercicio. Se inspeccionaron los PDF finales en color, grises y detalle. |
| Faltaba explicitar la revisión de cambios posteriores al presentar un criterio judicial como vigente. | Riesgo de tratar una autoridad histórica como actual. | El protocolo jurídico exige comprobar modificaciones, sustituciones y cambios posteriores pertinentes en fuentes oficiales. Esta auditoría no afirma haber investigado un asunto jurídico nuevo. |
| Un estudio aislado podía confundirse con evidencia suficiente de consenso científico. | Generalización excesiva. | El protocolo exige evidencia académica de síntesis cuando se afirma consenso, además de alcance, limitaciones, correcciones y retractaciones pertinentes. |

## Comprobaciones realizadas

| Comprobación | Resultado y alcance |
| --- | --- |
| Estructura de la skill | Validador de skills aprobado; instrucciones, recursos, enlaces y JSON comprobados. |
| Validador de paquetes | 20 pruebas aprobadas: casos válidos Markdown/JSON, corrupción, cambios sin regenerar, archivos ausentes, versiones, cobertura, referencias, fuentes incompletas, citas agrupadas, rutas, enlaces simbólicos, tipos inválidos, lectura sin escrituras y referencias históricas. |
| Piloto real | Validador estructural aprobado sin errores ni avisos. Identidad y versión 1.1.0 coherentes; manifiesto 1.1 y mapa 1.0. |
| Propagación real | Regresión ejecutada en copia temporal: texto, datos, cálculos, versión, título y URL de fuente cambian en pizarra y cuaderno. La vista derivada se reconstruye y el original queda intacto. |
| Reproducción | Ambos PDF repiten sus bytes con las mismas entradas y entorno; también se comprobó la alternativa tipográfica Vera. Cambiar el entorno requiere nueva revisión visual. |
| Contenido del piloto | Cálculos contrastados independientemente. Se distingue sustituir de retirar, mediana resistente de inmutable y dato alto de error. Registro y uso de la sección pertinente de OpenStax comprobados. |
| Diseño | Un lienzo A1 horizontal y tres páginas Carta. Revisión independiente de 14 vistas: páginas, lienzo general, seis zonas y versiones en grises. Además, comprobación final del lienzo completo y las tres páginas por quien integra la entrega. |
| Referencia histórica | PDF aprobado de ISAI y amparo conservado byte por byte y tratado como referencia de estilo; su contenido jurídico no se presenta como actualizado. |
| Continuidad | Documentación neutral para otras IA, rutas relativas, fuente declarada, procedimiento de regeneración, historial y comprobación de versiones. Se conserva la interfaz añadida por la plataforma. |

## Evidencia reproducible

- [Piloto de media y mediana](validacion/piloto-media-mediana/INDICE.md):
  [pizarra](validacion/piloto-media-mediana/salidas/pizarra.pdf) y
  [cuaderno](validacion/piloto-media-mediana/salidas/cuaderno.pdf).
- [Registro de auditoría del piloto](validacion/piloto-media-mediana/revision/auditoria.json),
  [regresión](validacion/piloto-media-mediana/revision/regresion.json),
  [estructura](validacion/piloto-media-mediana/revision/estructura.json) y
  [manifiesto](validacion/piloto-media-mediana/manifest.json).
- [Pruebas del validador](validacion/test_validar_paquete.py) y
  [procedimiento de regeneración](validacion/piloto-media-mediana/editables/README.md).

Los comandos de comprobación están en el [README](README.md). Las capturas
temporales de revisión no se incluyen en el repositorio; se pueden regenerar
desde los PDF conservados. La auditoría identifica los archivos inspeccionados
y el registro de generación correspondiente. El piloto es un caso de prueba
con datos hipotéticos, no un apunte encargado por el usuario.

## Límites que siguen siendo explícitos

El validador comprueba estructura e integridad, no la verdad de las explicaciones,
la lectura efectiva de una fuente, el contenido real de las páginas PDF ni la
legibilidad. Esas comprobaciones se hicieron por separado en el piloto y deben
repetirse cuando corresponda en cada tema. No se hizo impresión física ni se
probó importación en Goodnotes. No se leyó íntegramente el libro de OpenStax ni
se volvió a investigar el contenido jurídico de la referencia histórica.

Esta versión corrige fallos reales y hace comprobable la continuidad; no promete
que cualquier IA ejecute siempre bien el método. Para guardar, otra IA necesita
sus propias herramientas y permisos. El éxito de los guardados se verifica en
los repositorios y se informa fuera de este mismo commit, para evitar una
referencia circular.

El [registro 1.0.0](VALIDACION_SKILL.md) se mantiene con una nota explícita sobre
lo que aquellas pruebas no demostraron. No se reescribe una validación histórica
como si hubiera cubierto los defectos descubiertos después.
