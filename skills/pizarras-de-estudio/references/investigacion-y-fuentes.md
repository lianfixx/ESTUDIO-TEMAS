# Investigación y fuentes

## Delimitar y leer

Crear lista de entradas con identificador, nombre, páginas o fragmentos,
estado de lectura y dudas localizadas. Leer íntegramente el material entregado.
La exhaustividad se refiere al alcance acordado y las entradas recibidas, no
a toda la literatura disponible. Si falta un archivo citado, buscarlo en la
fuente autorizada; no completar su contenido o apariencia por memoria.

Conservar literalmente fechas, cifras, nombres y referencias en el registro de
entrada. Corregir en el desarrollo solo con evidencia e identificar la corrección
sin atribuir un error al usuario cuando su origen sea incierto.

## Investigar según la afirmación

Preferir fuentes primarias para hechos y reglas: publicaciones oficiales,
resoluciones completas, datos originales, investigación y documentación técnica
oficial. Para teoría usar libros académicos, universidades y trabajos de autores
identificables. Valorar calidad, pertinencia, edición, contexto y límites: una
fuente oficial no prueba cualquier conclusión.

Usar divulgación como orientación, sin sustituir una fuente primaria accesible.
No imponer un número de citas. Consultar versión vigente para afirmaciones sobre
el presente y versión histórica para hechos anteriores. Separar fecha real de
consulta, publicación, vigencia y fecha de los apuntes.

Leer el pasaje con contexto, anexos, notas y tablas que condicionen la afirmación.
No afirmar lectura íntegra de una obra si se leyeron secciones. No citar páginas
vistas solo en buscadores. Comprobar el destino de enlaces. Si una fuente no
responde, conservar la incertidumbre, no sustituirla silenciosamente.

## Registro de evidencia

Guardar `fuentes.json` como lista de registros con `id`, `titulo`,
`autor_institucion`, `tipo`, `fecha_edicion`, `url_o_identificador`, `consulta`,
`alcance_leido`, `localizadores`, `afirmaciones_respaldadas`, `estado` y `limites`.
Usar `null` en datos desconocidos. Estados: `consultada`, `pendiente` o
`historica_no_reverificada`. Una URL guardada no acredita consulta.
Cada afirmación sustantiva en `contenido.md` debe permitir llegar al pasaje fuente.

Distinguir aporte del usuario, hecho verificado, teoría/modelo, interpretación,
inferencia y ejemplo hipotético. En el material visible escribir naturalmente
«En este supuesto…» o «El autor sostiene…» donde importe. No presentar inferencias
como texto literal. Las citas textuales deben ser fieles y breves.

Resolver contradicciones identificando si provienen de fechas, jurisdicciones,
definiciones, métodos o calidad de evidencia distintos. Presentar las posturas
con su alcance cuando no se resuelvan; no elegir por mayoría de buscadores.
Un punto central incierto impide marcar el tema completo como verificado, aunque
las partes independientes puedan avanzarse.

## Adaptar a la materia

- Derecho: aplicar `derecho.md`; no verificar solo un artículo aislado.
- Matemáticas/datos: definir variables, unidades y supuestos; comprobar cálculos;
  distinguir datos observados y ejemplos construidos. Mostrar pasos útiles.
- Ciencias: diferenciar resultado empírico, hipótesis, teoría y consenso; señalar
  método, población y límites cuando determinen el alcance.
- Historia/humanidades: identificar periodo, fuente e interpretación; evitar
  anacronismos y falsas citas, mostrar debates relevantes.
- Administración: explicar función, supuestos y límites del modelo; no tratar
  recomendaciones contextuales como leyes universales.

No rellenar todos estos campos en la pizarra si no aportan. La teoría debe ayudar
a entender el tema concreto.
