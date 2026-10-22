---
name: pizarras-de-estudio
description: >-
  Convertir apuntes, fotos, anotaciones, documentos o temas de cualquier materia en
  una pizarra grande conectada y páginas imprimibles para estudiar y anotar, con
  redacción natural, investigación verificable y fuentes oficiales o académicas.
  Usar al pedir pizarras de estudio, pasar apuntes a Goodnotes, desarrollar un tema
  con este método, corregir materiales o continuar ESTUDIO-TEMAS, también con
  Claude u otra IA. Mantener editables, fuentes y versiones en GitHub.
---

# Pizarras de estudio

Convertir lo que aporta Emi en material que permita entender, relacionar y estudiar.
Ser completo dentro del tema pedido: investigar las bases necesarias y explicar
los tecnicismos sin relleno, errores inventados ni lenguaje grandilocuente.

## Decisiones acordadas

- Producir **dos salidas complementarias** por tema: pizarra grande conectada para
  explorar y ampliar, y páginas normales para leer, imprimir y anotar.
- Usar el mismo contenido revisado, fuentes y versión. No agrandar una página ni
  recortar un lienzo para simular dos formatos. Añadir hojas o lienzos si ayudan.
- Usar español natural, claro y humano, precisión técnica y referencias discretas.
- Guardar la skill y los trabajos en `lianfixx/ESTUDIO-TEMAS`. Emi autorizó ambos
  formatos y el archivo de futuros trabajos el 22 de octubre de 2026. No volver
  a preguntar estas preferencias. Aplicar el protocolo de privacidad del archivo.
- Permitir continuidad mediante archivos abiertos. Cada IA necesita herramientas
  y permisos propios; tener la skill no concede acceso de escritura ni a Goodnotes.

## Recursos

Leer [investigacion-y-fuentes.md](references/investigacion-y-fuentes.md) antes de
investigar y [derecho.md](references/derecho.md) para temas jurídicos.
Leer [estilo-y-diseno.md](references/estilo-y-diseno.md) antes de componer,
[archivo-y-continuidad.md](references/archivo-y-continuidad.md) antes de recuperar
o guardar y [auditoria.md](references/auditoria.md) antes de entregar.
Usar [tema.md](assets/tema.md), [manifest.json](assets/manifest.json) y
[mapa.json](assets/mapa.json) como contratos mínimos adaptables, no como plantilla
que imponga secciones irrelevantes.

## 1. Recuperar y leer

Si el tema ya existe, leer índice, manifiesto y archivos actuales. Comprobar versión
y cambios recientes; no reconstruir el estado desde recuerdos. Inventariar fotos,
páginas, documentos y notas. Leer todo lo entregado, incluidas anotaciones
marginales, cuadros y anexos. Revisar OCR contra imagen; marcar `[ilegible]` con
ubicación precisa. No completar por intuición palabras, números o referencias.

Fijar tema, objetivo, nivel y pregunta central. Si solo hay un título, no inventar
apuntes ni opiniones del usuario. Completar las bases necesarias autónomamente.
Preguntar solo si falta algo que cambie alcance, significado, jurisdicción o
conclusión; avanzar con lo independiente. Registrar cobertura, dudas y originales.
No declarar lectura íntegra si falta una entrada. Corregir errores comprobados
en el desarrollo y registrar brevemente qué cambió y por qué.

## 2. Investigar y comprobar

Consultar fuentes oficiales y académicas apropiadas. Abrir y leer las fuentes
citadas; los snippets no cuentan como lectura. Vincular cada afirmación sustantiva
o controvertida con fuente y localizador reales. Distinguir apunte, hecho
comprobado, interpretación y ejemplo hipotético sin llenar la pizarra de etiquetas.

No inventar hechos, artículos, citas, páginas, autores, expedientes, fechas,
enlaces, cálculos ni acciones realizadas. Resolver o delimitar contradicciones.
Si falta una fuente indispensable, identificar qué conclusión sigue provisional;
no presentar el conjunto como final por tener un PDF atractivo.
No fijar normas cambiantes en la skill: verificar fecha, versión, vigencia y
alcance en cada trabajo jurídico conforme a `derecho.md`.

## 3. Explicar y conectar

Organizar según la lógica del tema. Desarrollar concepto, bases teóricas,
funcionamiento, relaciones, fundamento, condiciones, excepciones y consecuencias
cuando aporten. Explicar el término técnico donde aparece. Usar ejemplos y
comparaciones breves para resolver confusiones concretas. No imponer nueve
bloques, cuestionarios ni una cantidad artificial de páginas.

Dar identificadores estables a conceptos (`C01`) y fuentes (`F01`). Registrar
relaciones y remisiones en `mapa.json`; cada flecha debe expresar una relación
comprobada. No sugerir causalidad por cercanía temporal. Añadir preguntas de
repaso y respuestas separadas cuando resulten útiles.

## 4. Componer las dos salidas

Crear `contenido.md` como explicación canónica y `fuentes.json` como evidencia.
Conservar también diseño abierto o código que produzca cada PDF: SVG, HTML/CSS
o script con dependencias y comando probado. Un PDF solo no es una fuente editable.
Evitar cuentas o enlaces temporales como única vía para continuar.

Diseñar una pizarra amplia, conectada y legible. Componer aparte páginas Carta
(A4 si se pide), con márgenes y espacio para escribir. Conservar la claridad,
blanco y azul sobrio de la referencia aprobada sin copiar su cuadrícula.
Mantener correspondencia entre conceptos, fuentes, advertencias y versión.
El lienzo puede sintetizar, con remisiones al desarrollo; no omitir una excepción
o condición que cambie el sentido.

Usar las herramientas de PDF/documentos disponibles y renderizar el resultado.
No usar imágenes generadas para texto, normas, citas o diagramas exactos.
Si faltan herramientas de diseño, conservar contenido y editables como borrador
y decir qué salida falta; no afirmar que los PDF existen.

## 5. Auditar y guardar

Aplicar `auditoria.md`: revisar todas las páginas y cada zona del lienzo a escala
de lectura. Corregir recortes, superposiciones, citas ilegibles y remisiones.
Contrastar ambos formatos con el contenido canónico. Guardar contenido, fuentes,
mapa, editables, PDF, manifiesto y cambios; actualizar índice. Preservar historial
y aportaciones ajenas. Verificar commit remoto y rutas antes de afirmar guardado.

Comprobar capacidades actuales de Goodnotes. Generar un archivo o enlace no
equivale a importarlo en una cuenta. Declarar importación solo con evidencia del
destino. Si no hay integración suficiente, entregar PDF importables y una
instrucción breve; no intentar eludir incompatibilidades del servicio.

## 6. Entregar

Mostrar los dos PDF y enlace verificado al tema en GitHub. Mencionar correcciones
importantes y dudas sustantivas. Separar revisión de contenido, revisión visual,
guardado en GitHub e importación en Goodnotes; afirmar solo estados comprobados.
No atribuir el trabajo a Emi ni garantizar instalación automática en cualquier IA.
