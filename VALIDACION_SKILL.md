# Validación de Pizarras de estudio 1.0.0

Fecha: 22 de octubre de 2026.

> Registro histórico de la primera validación. La [auditoría posterior 1.1.0](AUDITORIA_2026-10-22.md)
> encontró que el generador del piloto comprobaba los IDs, pero no propagaba
> cambios del contenido canónico, y que la regeneración podía dejar hashes y
> aprobaciones obsoletos. Las comprobaciones descritas aquí no demostraban esa
> continuidad. Los defectos están corregidos y cubiertos por las pruebas nuevas;
> este registro se conserva para no ocultar el alcance de la validación inicial.

## Estructura y continuidad

- Inicialización y validación del paquete con el validador de skills: aprobadas.
- Enlaces internos de la skill y sintaxis de plantillas JSON: comprobados.
- Revisión independiente de portabilidad: se detectó que las listas de `mapa.json`
  no especificaban campos; se corrigió incorporando el contrato de nodos,
  relaciones y remisiones en `archivo-y-continuidad.md`.
- Formatos y archivo: la decisión del usuario quedó incorporada en la skill,
  instrucciones raíz, plan e índice. Se distingue acceso de lectura, permisos de
  escritura e importación a Goodnotes.

## Casos de comportamiento

Se usaron sesiones independientes con la skill y el encargo concreto, sin
proporcionar respuestas esperadas. No se escribieron sistemas remotos durante
las pruebas. Los ejercicios internos no se publican como apuntes del usuario.

| Caso | Encargo | Resultado observado |
| --- | --- | --- |
| Apunte incompleto | Artículo y persona ilegibles; plazo recordado como 15 o 30 días; sin país ni procedimiento | Conservó lo incierto, no eligió una cifra ni supuso relación entre los fragmentos. Solicitó país y norma/procedimiento y no creó PDF con contenido inventado. |
| Jurídico editorial | Extractos de ocho y seis votos sin fechas; conclusión de invalidez con cinco y jurisprudencia automática con tres precedentes; sin búsqueda por petición del caso | No asignó fechas ni jurisdicción. Separó decisión, razones, efectos y obligatoriedad; mantuvo las conclusiones como pendientes de comprobación. No citó normas no consultadas ni generó los PDF. |
| Estadística con doble salida | Media y mediana de cinco tiempos hipotéticos, efecto de un dato alto, ejercicio y respuesta separada | Consultó OpenStax, verificó los cálculos y generó un lienzo A1 conectado y tres páginas Carta distintas del lienzo, con espacio para anotaciones y código editable. Se inspeccionaron las cuatro páginas; se corrigió una línea que interfería con el pie de página y se retiró metodología interna del material de estudio. |

Los dos casos anteriores comprueban el tratamiento de incertidumbre y los límites
editoriales. No equivalen a investigación jurídica completa ni a validación de
normas vigentes.

El caso de estadística permitió comprobar generación real, selección de una
fuente académica, cálculos independientes y revisión visual. La versión corregida
de la página afectada volvió a abrirse. El lienzo cuenta con conexiones rotuladas;
el cuaderno desarrolla las fórmulas y deja la respuesta del ejercicio separada.

## Persistencia de la skill

La instalación de Work Mode se validó, se confirmó en Git y se sincronizó con
éxito en el commit `02e89e3`. Su carpeta y la copia portable de este repositorio
se compararon antes de la publicación. Este registro no acredita por sí mismo
importación a Goodnotes ni disponibilidad de herramientas en otros proveedores.

## Referencia aprobada

Se recuperó y abrió la pizarra aprobada de ISAI y amparo. Se conserva el PDF
original sin modificaciones, con hash SHA-256 y estado `referencia_historica`.
La inspección fija el estilo observado, no actualiza sus afirmaciones jurídicas.

## Alcance

Esta validación reduce errores de estructura, continuidad e invención observados
en estos casos. No garantiza que cualquier IA ejecute siempre bien el método ni
que toda fuente futura sea accesible. Cada tema conserva su propia auditoría.
