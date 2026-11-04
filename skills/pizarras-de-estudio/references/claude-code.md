# Trabajo en Claude Code

Complemento operativo; no cambia el método. Ante una contradicción, prevalece SKILL.md.

## Frenos activos (hooks)

1. Antes de un `git commit` que toque `temas/<slug>/`, se ejecuta
   `python3 skills/pizarras-de-estudio/scripts/validar_paquete.py temas/<slug>`
   por cada tema tocado; si falla, el commit se bloquea.
2. Antes de cada commit se buscan secretos y datos personales (CURP, tarjetas)
   en el diff, porque el repositorio es público.
3. Se pide confirmación antes de `git push` y se bloquea `git push --force`.
4. Si el commit cambia SKILL.md, se comprueba que siga siendo compatible con claude.ai.

Solo actúan en Claude Code dentro de este repositorio; no existen en claude.ai,
ChatGPT, Codex ni otra IA. No sustituyen las reglas de la skill: pasar el validador
no acredita fuentes ni legibilidad, la búsqueda automática no reemplaza la revisión
de privacidad y derechos, y confirmar un push no sustituye comprobar que la tarea
actual lo autoriza.

## Plan y entrevista

Modo plan (Shift+Tab): recuperar el tema, inventariar entradas y proponer conceptos,
fuentes y composición sin escribir. Entrevista solo si Emi da únicamente un título o
tema sin apuntes:

> Antes del plan, entrevístame sobre objetivo, nivel y pregunta central de este tema.
> Una pregunta a la vez y solo lo que cambie alcance o significado. No preguntes
> formatos ni destino: ya están fijados. Después muéstrame el plan.

## Reparto en paralelo

- Quien consolida fija antes un inventario único de entradas y de IDs `C..` y `F..`.
- Investigación: un subagente por subtema o fuente. Entrega afirmaciones con fuente
  y localizador real para `fuentes.json` y `cobertura.json`, y lo que no pudo leer.
- Auditoría visual: un subagente por salida (pizarra, cuaderno), con hallazgos por
  página o zona. No aprueba ni toca el manifiesto.
- Un único consolidador escribe canónico, fuentes, mapa y cobertura, regenera,
  registra aprobaciones y declara la cobertura final. Ningún subagente hace commit,
  push, publica ni marca el tema como revisado.

## /goal

```text
/goal Terminar temas/<slug> según el criterio de terminado de la skill: validar_paquete.py devuelve "paquete_doble_validado": true, avisos revisados, todas las páginas y zonas del lienzo revisadas. Sin push hasta que yo lo autorice.
```

## /loop y ejecución programada

No hacen falta: no hay nada que vigilar cada cierto tiempo. Si se usan, no se activan
al instalar la skill y ningún prompt programado publica, hace push ni escribe a terceros.

## Navegador

- Playwright (navegador aparte): renderizar editables HTML/CSS o SVG y capturar
  páginas y zonas del lienzo a escala de lectura. Si no muestra el PDF final,
  rasterizarlo con una herramienta de PDF: la revisión vale sobre el PDF entregado.
- Claude in Chrome (tu Chrome con tus sesiones): fuentes académicas que requieren
  la sesión institucional de Emi y, si Goodnotes ofrece versión web en su cuenta,
  comprobar ahí una importación. Ver el documento en el destino es la evidencia.
- Nunca para eludir accesos, muros de pago o bloqueos; registrar lo inaccesible.

## En la sesión

- `/context`: ver cuánto ocupan fuentes y PDF leídos.
- `/compact conservar inventario, IDs, fuentes leídas y pendientes`: liberar espacio sin perder el estado.
- `/clear`: empezar otro tema.
- `/rewind` (o Esc Esc): volver antes de una edición equivocada del canónico.
- `!python3 skills/pizarras-de-estudio/scripts/validar_paquete.py temas/<slug>`: validar sin gastar razonamiento.

## Mejora continua

`/insights` en Claude Code local ayuda a detectar patrones de uso. Sus sugerencias
son candidatas: solo entran si Emi pide mejorar el método y se sigue el procedimiento
de [archivo-y-continuidad.md](archivo-y-continuidad.md#skill-instalada-y-copia-canónica).
