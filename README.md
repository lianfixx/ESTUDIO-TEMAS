# ESTUDIO-TEMAS

Apuntes de estudio claros, fundamentados y fáciles de continuar con otra IA.

Cada tema nuevo tiene dos salidas complementarias:

- **Pizarra grande conectada:** para entender el conjunto, recorrer relaciones y ampliar en Goodnotes.
- **Páginas de estudio:** tamaño Carta, con explicación, ejemplos y espacio para imprimir y anotar.

Ambas parten de una fuente canónica editable y de las mismas fuentes verificadas. La
profundidad depende del tema; no se rellena ni se comprime todo en una sola hoja.

Método actual: **1.2.0**, con [correcciones de fondo](AUDITORIA_FONDO_2026-10-22.md),
validador de integridad y [piloto reproducible](validacion/piloto-media-mediana/INDICE.md).
El piloto prueba el método; se conserva separado de los apuntes del usuario.

## Empezar o continuar

Pedir a la IA que lea [AGENTS.md](AGENTS.md), la
[skill Pizarras de estudio](skills/pizarras-de-estudio/SKILL.md) y el
[índice](INDICE.md). Después aportar los apuntes o indicar el tema.

Por ejemplo: «Usa la skill de este repositorio para convertir estos apuntes en
una pizarra grande y páginas para estudiar. Verifica las fuentes, conserva los
editables y guarda el trabajo en el tema correspondiente».

La skill es un conjunto de instrucciones en Markdown y formatos abiertos. Puede
leerse con ChatGPT, Claude u otra IA sin depender de esta conversación. Cada
servicio necesita sus propias herramientas y acceso al repositorio para guardar
cambios. Leer la skill no concede credenciales ni garantiza importación a Goodnotes.

## Archivos y versiones

Los trabajos nuevos se guardan en `temas/<tema>/`, con contenido, fuentes,
relaciones, diseño editable, ambos PDF y un manifiesto del estado real. El historial
de Git conserva versiones anteriores. No se reemplazan los originales. El manifiesto
identifica la fuente canónica, los archivos usados para generar y las revisiones
que corresponden a los PDF actuales; generar un PDF no equivale a aprobarlo.
Las aprobaciones identifican la generación exacta revisada. Los bloques de
contenido realmente usados y las explicaciones que dependen de datos deben
permanecer coherentes después de una modificación.

Desde la raíz del repositorio se pueden ejecutar las comprobaciones:

```bash
python3 -m unittest discover -s validacion -p 'test_*.py' -v
python3 skills/pizarras-de-estudio/scripts/validar_paquete.py validacion/piloto-media-mediana
python3 validacion/piloto-media-mediana/editables/probar_regresion.py
```

Las dos primeras usan solo Python estándar. La regresión requiere ReportLab y
pypdf; trabaja en una copia temporal. El [procedimiento del piloto](validacion/piloto-media-mediana/editables/README.md)
explica la generación y revisión. La comprobación estructural no sustituye la
lectura de fuentes ni la inspección visual.

Las fuentes externas se identifican con enlaces y localizadores. El repositorio
es público: los apuntes de estudio no deben arrastrar datos reservados de asuntos
reales ni documentos ajenos que no puedan redistribuirse.

## Referencia de estilo

La [pizarra aprobada de ISAI y amparo](referencias/estilo-aprobado/Pizarra_ISAI_y_Amparo.pdf)
se conserva sin cambios como ejemplo de tono y presentación. Es un documento
anterior al estándar de doble salida; no se presenta como investigación jurídica
actualizada ni como un tema completo bajo el nuevo método. Su
[registro](referencias/estilo-aprobado/manifest.json) precisa el alcance.

El [plan](PLAN_PIZARRAS_DE_ESTUDIO.md) conserva el diseño acordado y las decisiones
de formato y archivo del 22 de octubre de 2026.
