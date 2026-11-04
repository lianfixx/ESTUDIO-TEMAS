@AGENTS.md

# Claude Code en este repositorio

- Es el mismo método para todas las IA; no mantener otra versión independiente de estas instrucciones. Leer `skills/pizarras-de-estudio/SKILL.md` (se carga desde `.claude/skills/pizarras-de-estudio`, invocable como `/pizarras-de-estudio`) y el manifiesto del tema antes de trabajar.
- Frenos activos en `.claude/settings.json` (política en `.claude/hooks/policy.json`, pruebas en `.claude/hooks/test_guard.py`). Si un freno bloquea algo legítimo, explícaselo a Emi; no lo desactives ni lo rodees.
- Reglas por tipo de archivo en `.claude/rules/` (se cargan solas al tocar esos archivos).
- Plan y entrevista, subagentes, `/goal`, `/loop` y navegador: `skills/pizarras-de-estudio/references/claude-code.md`.
