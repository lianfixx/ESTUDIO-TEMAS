# Auditoría antes de entregar

Registrar estados reales (`pendiente`, `parcial`, `aprobada`, `no_aplica`) con
evidencia breve y fecha. Una casilla completada no demuestra revisión.

## Contenido

- Contrastar con todas las entradas: cobertura, transcripción, omisiones, cifras,
  nombres, dudas y correcciones. Cerrar `cobertura.json`: cada punto relevante
  llega a un concepto o tiene una exclusión motivada; lectura no equivale a cobertura.
- Confirmar fuentes leídas, localizadores y relación afirmación-fuente; distinguir
  hechos, teorías, inferencias y ejemplos.
- Comprobar vigencia/alcance en Derecho, cálculos/unidades donde proceda y contexto
  e interpretación en otras disciplinas.
- Revisar bases, tecnicismos, condiciones y excepciones al nivel requerido;
  eliminar redundancias y añadidos fuera del alcance.
- Mantener dudas decisivas visibles junto al punto. Si afectan la conclusión,
  entregar solo lo comprobado como parcial.

## Presentación

Renderizar la versión final de ambos PDF. Abrir cada página y cada lienzo.
Examinar lienzo completo y zonas a escala de lectura; usar recortes de inspección
si no cabe. Revisar páginas al 100 % y legibilidad en grises. Comprobar márgenes,
espacio para escribir, letra, acentos, símbolos, tablas, flechas, fórmulas y enlaces.
Examinar precisión del titular, punto de inicio, conexiones de los conceptos
centrales y espacio de escritura junto al ejercicio. Un lienzo sin recortes puede
seguir siendo ambiguo o pedagógicamente incompleto.
Contrastar IDs, remisiones, versión y conclusiones con el contenido canónico.
Un resumen puede abreviar, pero no borrar una excepción decisiva. No aceptar
recortes del lienzo como páginas de estudio.

## Reproducción y archivo

Confirmar editables que realmente produzcan los PDF, dependencias y comando.
Probar continuidad en una copia temporal: cambiar una frase o dato compartido en
la fuente canónica y comprobar que llega a ambos formatos, o que el generador
detiene una síntesis incompatible con explicación concreta. Que el script encuentre
IDs no prueba que use el contenido. Restaurar la muestra y no publicar el cambio
de prueba. Ejecutar este ensayo al crear o modificar el generador, no repetirlo
en cada corrección tipográfica si ya hay evidencia válida.

Ejecutar `scripts/validar_paquete.py` sobre el paquete final. Verificar registro
de generación, hashes, IDs, rutas, versiones, fuentes y remisiones. El validador
no abre fuentes, no comprueba el número real de páginas de un PDF ni interpreta diagramas: nunca presentar su salida como prueba
de veracidad, revisión jurídica o legibilidad.

Después de regenerar, actualizar hashes y marcar revisiones afectadas como
pendientes. Aprobarlas solo tras revisar los archivos finales. Registrar hashes
de los PDF inspeccionados en la evidencia de auditoría cuando sea posible.
Si el original es un PDF legado sin fuente editable, señalarlo; no crear un
editable ficticio ni prometer reproducción exacta.
Verificar manifiesto, índice, rutas, hashes y cambios. Revisar el diff y los
archivos para el repositorio público. No incluir credenciales ni datos reservados
por arrastre. Publicar material autorizado, excluir o anonimizar lo demás y
registrar exclusiones sin revelar esos datos.

Confirmar commit remoto y rutas. Si falla, conservar trabajo y decir qué falta.
No marcar importación Goodnotes sin evidencia de cuenta/cuaderno/documento destino.

## Estado final

Marcar `revisado` solo cuando ambas salidas, editables y verificaciones exigidas
estén terminadas. Usar `parcial`, `borrador` o `referencia_historica` según el caso.
Registrar revisión sustantiva y visual por separado. Comunicar resultado y límites
útiles; no volcar toda la bitácora sobre el usuario.
