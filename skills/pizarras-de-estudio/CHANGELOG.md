# Cambios de Pizarras de estudio

## 2026-11-04 · 1.3.1 · registro obligatorio y trabajo entre IA

- Agente: Claude Code (sesión en la nube; modelo según la sesión)
- Solicitud: Emi, 4/11/2026: auditar y documentar las mejoras, hacerlas funcionar igual con ChatGPT, Gemini u otra IA, y documentar siempre todo cambio, use la IA que use, bajo las mismas reglas.
- Cambios: capa común `ia/` (protocolo común 1.0.0 basado en el de Mes, `REGLAS.md` generadas de `politica.json`, frenos para Claude Code, hooks de git para cualquier IA, workflow `registro-ia.yml`, `INSTRUCCIONES_PROYECTO.md` para ChatGPT y Gemini, plantillas de petición y entrega); `GEMINI.md`; sección «Trabajo entre IA» en `AGENTS.md`; `.claude/settings.json` apunta a `ia/guard.py` (se retira `.claude/hooks/`); auditoría en `ia/AUDITORIA_2026-11-04.md`. Skill 1.3.1: sección «Registro y continuidad entre IA» y nota de portabilidad en `references/claude-code.md`; el método no cambia.
- Archivos: ver `ia/AUDITORIA_2026-11-04.md`, sección «Archivos cambiados».
- Verificación: `python3 ia/test_guard.py` → aprobado; `python3 ia/verificar.py reglas --check` → aprobado; `validar_paquete.py` sobre el tema publicado → ok; pruebas de `validacion/` → aprobado.
- Revisión independiente: 17 hallazgos sobre el código común; corregidos los reproducidos, con pruebas de regresión (detalle en `ia/AUDITORIA_2026-11-04.md`).
- Pendiente: activar los hooks de git en cada copia (`sh ia/instalar.sh`); opcionalmente exigir el check `registro-ia` con protección de rama en GitHub.

## 1.3.0 · 2026-11-04

- SKILL.md: nueva sección «Terminado y trabajo en Claude Code» con criterio de
  terminado verificable, cuándo hacer la entrevista inicial (solo con un título o
  tema sin apuntes, sobre objetivo, nivel y pregunta central) y qué pasos merecen
  máxima profundidad.
- Nueva referencia `references/claude-code.md`: frenos activos del repositorio,
  modo plan y entrevista, reparto entre subagentes con un solo consolidador,
  `/goal`, navegador, atajos de sesión y uso de `/insights`.
- `assets/manifest.json` registra `version_skill` 1.3.0 para temas nuevos.

El método no cambió: reglas de investigación, Derecho, privacidad, publicación,
estilo, auditoría y el contrato del validador siguen igual. El esquema del
manifiesto sigue en `schema_version` 1.2 y el del mapa en 1.0; la versión de la
skill y la del esquema son independientes. Los temas publicados con
`version_skill` 1.2.0 siguen válidos y no requieren regenerarse ni revisarse de
nuevo por este cambio.

## 1.2.0 y anteriores · 2026-10-22

Registradas en `AUDITORIA_FONDO_2026-10-22.md`, `AUDITORIA_2026-10-22.md` y
`VALIDACION_SKILL.md`, en la raíz de ESTUDIO-TEMAS.
