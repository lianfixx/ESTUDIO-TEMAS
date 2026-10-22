# Cambios

## 1.1.0 · 2026-10-22
- Corregido el fallo real de fuente doble: el generador anterior solo comprobaba encabezados Markdown, mientras duplicaba a mano textos y cifras. Ahora consume `contenido.json`; Markdown es una vista derivada. Los resultados se calculan y las referencias provienen de `fuentes.json`.
- Migración de manifiesto a schema 1.1: declara canónico, vista, cobertura, entradas/salidas con SHA-256 y entorno tipográfico; mapa conserva schema 1.0. Versiones piloto y skill: 1.1.0.
- Cada regeneración actualiza hashes y deja auditorías pendientes. La aprobación exige revisión externa del snapshot vigente. La generación determinista evita cambios de bytes por fecha interna del PDF.
- Regresión en copia temporal: mutaciones de datos, texto compartido, versión y referencia se comprueban en ambos PDF y en la vista; no basta comparar archivos.
- Lienzo: «LA MEDIANA SE CONSERVA», marca de inicio discreta, vínculos hacia «¿PARA QUÉ?» y «SI n ES PAR», pie remite a págs. 1-3. Más líneas de resolución en el lienzo y el cuaderno.
- Se preservan los dos diseños, C01-C07 y F01. Tipografías configurables con alternativa Vera de ReportLab. Piloto interno, sin publicación ni importación remota por este trabajo.

## 1.0.0 · 2026-10-22
- Creación desde encargo textual y datos hipotéticos, sin originales adicionales.
- Se distingue sustituir un valor con n fijo de retirar una observación.
- Cálculos exactos y revisión independiente coincidentes.
- Revisión visual: se corrigió una línea de anotación que tocaba el pie de página 3; se amplió espacio de respuesta en página 2; se ajustaron conectores semánticos del lienzo.
- Se retiró metodología interna de la página de estudio y se conserva aquí y en auditoría.
- Alcance local por instrucción expresa; no se publica ni se importa a Goodnotes.
