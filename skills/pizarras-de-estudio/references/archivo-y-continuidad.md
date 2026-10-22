# Archivo, continuidad y trabajo entre IA

## Destino y autorización vigente

Usar `lianfixx/ESTUDIO-TEMAS` como repositorio del método y de los trabajos de estudio. El 22 de octubre de 2026 Emi autorizó guardar también las pizarras y permitir que otras IA con la skill puedan usarlas, guardarlas y modificarlas. Entregar siempre dos formatos: lienzo grande conectado y páginas normales para imprimir, estudiar y anotar. No volver a preguntar estas decisiones.

Esta autorización permite guardar y actualizar apuntes de estudio ordinarios. El repositorio es público: antes de subir documentos, imágenes o metadatos, comprobar su contenido real. No publicar por inadvertencia nombres de clientes, datos personales, firmas, domicilios, identificadores privados o constancias reservadas. Anonimizar las copias de estudio sin alterar los originales; conservar el material reservado en su destino privado y registrar solo una referencia no sensible. Si quitar un dato cambia el sentido, continuar con las partes independientes y consultar únicamente esa decisión. No publicar material de terceros que no se pueda redistribuir: guardar su referencia y enlace, no una copia íntegra.

## Entrada para cualquier IA

Mantener en la raíz del repositorio:

- `AGENTS.md`: punto de entrada neutral que remita a la skill y al índice.
- `INDICE.md`: título, carpeta, versión, fecha de revisión, estado y enlaces de cada tema.
- `skills/pizarras-de-estudio/`: copia canónica del método portable.

Las instrucciones deben poder leerse como Markdown sin depender de la memoria de una conversación, un proveedor o herramientas con nombres fijos. La IA necesita acceso de lectura para consultar; para guardar necesita herramientas y permisos de escritura válidos. Tener la skill no concede credenciales ni garantiza que un servicio pueda importar el archivo. Describir la limitación concreta y conservar el trabajo cuando falte una capacidad.

## Una carpeta por tema

Usar nombres estables sin espacios ni acentos, por ejemplo `temas/isai-y-amparo/`. No crear otra carpeta por cada corrección. Conservar las versiones anteriores mediante Git.

| Archivo o carpeta | Función |
| --- | --- |
| `contenido.md` | Contenido canónico con identificadores estables de apartados, preguntas y afirmaciones importantes. |
| `fuentes.json` | Fuentes realmente consultadas, sus localizadores y su relación con las afirmaciones. |
| `mapa.json` | Conceptos, conexiones con significado y referencias a los apartados que desarrollan cada relación. |
| `editables/` | Diseño abierto del lienzo y de las páginas; SVG, HTML/CSS, código o formato equivalente que permita regenerar ambos. |
| `salidas/pizarra.pdf` | Lienzo grande, legible al ampliar, con navegación o referencias al desarrollo. |
| `salidas/cuaderno.pdf` | Páginas Carta imprimibles con espacio para anotaciones. |
| `manifest.json` | Identidad, versión, fecha, alcance, estado, archivos y hashes SHA-256. |
| `CAMBIOS.md` | Correcciones breves con motivo, fuente y efecto sobre las dos salidas. |

Agregar `originales/` solo para entradas publicables y necesarias; no duplicar fuentes externas ni archivos que ya tengan una ubicación canónica. Mantener un breve procedimiento de regeneración junto al diseño editable, con dependencias y comandos comprobados; usar rutas relativas. Si se requiere una herramienta propietaria, conservar además una exportación abierta y declarar qué se puede editar sin ella.

El `manifest.json` debe identificar al menos `id`, `titulo`, `version`, `fecha_revision`, `estado`, `alcance`, `pendientes`, `archivos` y `version_skill`. En `archivos`, registrar ruta, función y SHA-256 de cada entrega y fuente editable; excluir el propio manifiesto de su lista de hashes. No usar rutas absolutas, tokens, URLs firmadas ni IDs privados como única forma de recuperar el trabajo. Estados útiles: `borrador`, `parcial`, `revisado` y `referencia_historica`. Elegirlos por evidencia, no por el hecho de existir un PDF.

En `fuentes.json`, conservar un ID por fuente, título, institución o autor, fecha o edición disponible, URL o identificador público, fecha real de consulta, localizador y qué respalda. Registrar qué fue leído y qué queda inaccesible. No convertir una URL guardada o un resultado de búsqueda en una fuente verificada.

## Revisar una vez, producir dos formatos

### Contrato de los archivos abiertos, versión 1.0

Usar el manifiesto de `assets/manifest.json`. `archivos` contiene objetos con
`ruta` relativa a la carpeta del tema, `funcion` y `sha256` real de los bytes.
`entradas` identifica material recibido, cobertura de lectura y dudas. Mantener
las auditorías de contenido, visual y correspondencia separadas. No incluir el
propio manifiesto en sus hashes. Los valores `null` en plantillas son desconocidos
pendientes de completar, no resultados verificados.

En `mapa.json`, completar `tema_id` y `version` iguales al manifiesto, y estas listas:

- `conceptos`: objetos con `id` único (por ejemplo `C01`), `titulo` y `apartado`
  que identifique un encabezado existente en `contenido.md`.
- `relaciones`: objetos con `desde` y `hacia` (IDs existentes), `relacion`
  (verbo o frase precisa), `fuentes` (IDs existentes en `fuentes.json`) y
  `justificacion` (pasaje del contenido que explica el vínculo). En vínculos
  puramente organizativos o ejemplos propios, las fuentes pueden estar vacías,
  pero la justificación debe identificarlos como tales. No usar esa excepción
  para presentar una afirmación externa sin respaldo.
- `remisiones`: objetos con `concepto_id`, `paginas_cuaderno` (lista de números
  enteros, contados desde 1) y `zona_pizarra` (rótulo o ancla visible). Dejar una
  lista vacía mientras no exista el PDF; no inventar páginas futuras.

No repetir IDs ni aceptar referencias a conceptos o fuentes inexistentes.
Se pueden añadir campos sin cambiar el significado de los anteriores. Cambiar
`schema_version` y documentar la migración si se altera el contrato. Guardar
`fuentes.json` como lista con el contrato de `investigacion-y-fuentes.md`.

Corregir primero `contenido.md` y el registro de fuentes; actualizar después el mapa y regenerar las dos salidas. Mostrar el mismo identificador de tema y versión en ambos PDF. El lienzo sintetiza y conecta; el cuaderno desarrolla y permite escribir. No mantener dos textos independientes que puedan contradecirse ni convertir la pizarra en páginas simplemente recortándola.

Antes de marcar `revisado`, comprobar la correspondencia entre conceptos del mapa y apartados, la integridad de referencias y la revisión visual de todas las páginas. Si solo se pudo actualizar una salida, registrar el desfase, conservar estado `parcial` y no presentar el conjunto como final. Una modificación solo de estilo también requiere regenerar la salida afectada y registrar que el contenido no cambió.

## Recuperar, modificar y sincronizar

1. Leer `AGENTS.md`, la skill canónica, `INDICE.md` y el manifiesto del tema. Abrir los archivos actuales; no reconstruirlos desde resúmenes antiguos.
2. Registrar el SHA inicial de la rama y revisar las instrucciones aplicables y los cambios pendientes. Usar una rama de trabajo si el repositorio lo exige o hay modificaciones simultáneas.
3. Modificar únicamente el alcance encargado. Conservar originales, atribuciones y cambios ajenos. No borrar temas ni reescribir el historial como parte de una actualización ordinaria.
4. Revisar diferencias, fuentes, hashes y las dos salidas. Actualizar versión, cambios e índice. Hacer un commit coherente con mensaje concreto.
5. Guardar mediante Git autenticado o API de archivos y commits con control del SHA esperado. Nunca usar `push --force`. Si cambió el remoto, leer los cambios, integrarlos y volver a comprobar los archivos afectados; no eliminar la protección del SHA para lograr que una escritura pase.
6. Verificar el éxito de la escritura y que la rama remota apunta al commit esperado; comprobar que los archivos anunciados forman parte de ese commit. Solo entonces decir que quedó guardado en GitHub. Si falla, informar qué quedó local y qué falta subir, sin marcar sincronización exitosa.

Guardar el hash del commit de cada publicación en la respuesta o registro de ejecución externo al mismo commit, evitando referencias circulares. No duplicar todo el historial en carpetas `v1`, `v2`, `final` y `final-final`.

## Skill instalada y copia canónica

Tratar `skills/pizarras-de-estudio/` de `ESTUDIO-TEMAS` como la referencia portable del método. La instalación en el entorno de cada IA es una copia de uso. Antes de modificar o reemplazar una copia, comparar su versión y sus diferencias con el repositorio; conservar cambios locales no integrados y resolver conflictos de forma explícita.

Cuando el usuario solicite mejorar el método, validar el paquete, actualizar la copia canónica y sincronizar la instalación disponible. En Work Mode seguir además el procedimiento vigente de persistencia de skills. Comprobar por separado ambos guardados; un commit en GitHub no prueba que la skill quedó instalada, ni una instalación local prueba que GitHub recibió los cambios.
