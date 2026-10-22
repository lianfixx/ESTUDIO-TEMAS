# Correcciones de fondo de Pizarras de estudio 1.2.0

Fecha: 22 de octubre de 2026. Alcance: método, continuidad del contenido,
generador del piloto, validador y explicación de los resultados. La revisión
anterior no había probado los casos descritos abajo; esta actualización corrige
esa insuficiencia y conserva el historial sin ocultarla.

## Defectos reproducidos

| Defecto en 1.1.0 | Reproducción y consecuencia | Corrección 1.2.0 |
| --- | --- | --- |
| Prosa canónica ignorada por los PDF | Añadir una condición a `secciones[].parrafos` de C05 cambiaba el Markdown; ambos PDF permanecían idénticos y la regresión anterior aprobaba. | Eliminar ese desarrollo duplicado. Las secciones referencian bloques usados por las composiciones; los campos antiguos, referencias inexistentes o bloques declarados sin uso no pueden aceptarse silenciosamente. Probar una explicación sustantiva compartida, además de datos y título. |
| Cálculos nuevos con explicación vieja | `base=100`, `principal=[10,20,20,20,80]` y sustitución del ejercicio por `100` eran admitidos. Aparecían «sube -4», «baja -6,4» y una afirmación de cambio de mediana cuando se mantenía en 20. | Derivar la explicación de la comparación real y comprobar si la mediana retirada cambia. Mantener explícitos los supuestos admitidos por el piloto y rechazar los incompatibles. |
| Aprobación antigua aceptada | Después de regenerar y restaurar la aprobación anterior, bastaba actualizar hashes documentales para que el validador devolviera un paquete revisado, pese a que el registro de la auditoría era distinto. | El manifiesto 1.2 exige `auditoria.generacion_verificada` igual a `generacion`, incluidas entradas, salidas y entorno. Actualizar hashes no renueva una aprobación. |
| Vista que ocultaba el canónico | Un canónico Markdown con otro tema, versión 9.9.9 y cita F99 inexistente podía ocultarse con una segunda vista correcta y aprobar. | Markdown exige `vista_contenido: null` y se comprueba directamente. JSON exige una vista Markdown derivada y distinta. |

Los casos se reprodujeron en copias temporales. Ninguna modificación de prueba
se publicó como material de estudio. La regresión se amplía con estos casos
porque el título correcto y los números recalculados no prueban, por sí solos,
que el desarrollo y las conclusiones sigan siendo correctos.

## Qué se comprobó del fondo académico

Una revisión independiente contrastó el contenido canónico, su vista y el texto
de ambos PDF. Recalculó los seis escenarios desde los datos y abrió la
[sección original de OpenStax](https://openstax.org/books/introductory-statistics-2e/pages/2-5-measures-of-the-center-of-the-data).
La integración también abrió esa fuente. Las reglas y referencias utilizadas
son pertinentes al alcance introductorio.

No se detectaron errores conceptuales en los datos originales: media/mediana
20/20, 30/20, 50/20 y 17,5/17,5 en la comparación; 28/20 y 20/20 en el ejercicio.
Se conservan las diferencias entre posición y valor, sustituir y retirar, dato
alto y error, resistencia e invariancia, y ejemplo hipotético y población.

Otra revisión independiente no detectó reglas sustantivas incorrectas en los
protocolos de investigación y Derecho. No se añadieron citas rituales, requisitos
jurídicos fijos ni temas ajenos para aparentar profundidad. Las correcciones se
concentraron en los mecanismos que sí podían volver incorrecto o incompleto un
material después de editarlo.

## Verificación

El validador supera **27 pruebas** con casos válidos y negativos. Los siete casos
nuevos cubren las dos formas de canónico, migración 1.1, evidencia ausente o vacía,
aprobación antigua, entorno o tipos diferentes y auditoría pendiente con `null`.

Un [caso nuevo en una sesión independiente](validacion/caso-mediana-traslacion.md)
comprobó la conducta del método sin compartir el diagnóstico ni la respuesta
esperada: corrigió tres afirmaciones falsas sobre mediana, retirada y suma de
una constante; explicó sus pasos, comprobó una fuente primaria y respetó el
encargo limitado a texto. El caso se conserva separado de los apuntes del usuario.

La regresión final del generador está aprobada: propaga una explicación
sustantiva a ambos PDF, además de datos, versión y fuentes; comprueba aumentos,
descensos, igualdad, valores centrales repetidos y decimales exactos. Incluye
19 rechazos de entradas o bloques incompatibles antes de reemplazar las salidas.
La prueba se ejecutó también desde la copia portable, sin alterar el piloto.

El paquete final pasó el validador sin errores ni avisos. Se comprobaron la
igualdad de los registros de generación y auditoría, 13 archivos JSON y 51 enlaces
locales. La skill instalada y su copia portable coinciden. La referencia histórica
conserva exactamente sus bytes originales.

Se inspeccionaron 14 imágenes de los PDF finales: páginas y lienzo en color y
grises, más seis zonas del lienzo. La integración abrió además el lienzo completo
y las tres páginas Carta. No se observaron recortes ni solapamientos. Se conserva
cuerpo de 11 puntos y cuatro líneas de resolución en la página del ejercicio;
los matices incorporados no se acomodaron a costa del espacio para estudiar.

Los hashes SHA-256 de las salidas revisadas son:

- Pizarra: `c3b50f90dc411c6b137c3c5a5a1ef4d1fbfa2f553b137c696a27aa4527f6c615`.
- Cuaderno: `6c2226db188d5456ba64b23e9c5052ca092215e7333adacb288b2757c26336cd`.

Resultado: defectos reproducidos corregidos y verificaciones finales aprobadas
dentro de este alcance. No quedan hallazgos conocidos pendientes de esta revisión.

## Uso y continuidad

Leer el [procedimiento del piloto](validacion/piloto-media-mediana/editables/README.md)
antes de modificarlo. Su estructura interna de contenido cambia; no basta copiar
el número de versión sobre el JSON antiguo. Tampoco basta rellenar la evidencia
de auditoría con el registro actual: primero deben revisarse los cambios reales.

La comprobación automática no determina si dos síntesis distintas dicen lo
mismo ni si una fuente respalda una interpretación nueva. Esas revisiones siguen
siendo sustantivas y explícitas. La explicación compartida debe propagarse; una
síntesis propia de un formato debe contrastarse con el desarrollo al modificarla.

Se conservan la pizarra y las páginas Carta, los datos hipotéticos y la referencia
histórica original de ISAI y amparo. No se hizo impresión física ni importación
en Goodnotes, ni se verificó de nuevo el contenido jurídico de esa referencia.
El estado revisado se refiere al alcance y los archivos identificados, no a una
garantía de ausencia universal de errores.

Evidencia final: [manifiesto](validacion/piloto-media-mediana/manifest.json),
[auditoría](validacion/piloto-media-mediana/revision/auditoria.json),
[regresión](validacion/piloto-media-mediana/revision/regresion.json),
[pruebas del validador](validacion/test_validar_paquete.py) y
[registro anterior 1.1.0](AUDITORIA_2026-10-22.md).
