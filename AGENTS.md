# Instrucciones para cualquier IA

1. Leer `skills/pizarras-de-estudio/SKILL.md` y los recursos pertinentes antes de
   transformar apuntes o continuar un tema.
2. Leer `INDICE.md`, el manifiesto y los archivos actuales del tema. La versión
   remota prevalece sobre recuerdos; comparar cambios locales antes de reemplazar.
3. Entregar pizarra grande conectada y páginas normales para imprimir/anotar,
   provenientes de una fuente canónica declarada y de las mismas fuentes.
   Respetar si el usuario acota expresamente una fase o salida. Guardar editables
   reproducibles y cobertura de los puntos relevantes recibidos.
4. Registrar incertidumbre y fuentes realmente leídas. No inventar ni declarar
   verificaciones, importaciones o escrituras que no ocurrieron.
5. Guardar trabajos en `temas/<slug>/`, actualizar índice y cambios, preservar
   historial y comprobar el commit remoto. No forzar pushes ni borrar trabajo ajeno.
6. Usar herramientas/permisos disponibles. Si falta escritura o diseño, conservar
   lo realizado y señalar el límite, sin prometer capacidades inexistentes.
7. Antes de marcar un tema como revisado, comprobar los hashes y el registro de
   generación, pasar `skills/pizarras-de-estudio/scripts/validar_paquete.py`
   y revisar contenido, correspondencia y todas las páginas renderizadas.
   Al cambiar el generador, comprobar propagación en una copia temporal. Una
   generación nueva debe invalidar las aprobaciones afectadas.

Método vigente: 1.2.0. Consultar `AUDITORIA_FONDO_2026-10-22.md` para los defectos
corregidos y los límites de las pruebas. Los casos de `validacion/` son pruebas
del método y no deben registrarse como apuntes solicitados por el usuario.

Una corrección sustantiva no puede quedarse solo en la vista Markdown. Comprobar
su destino real en las salidas y las síntesis relacionadas. No conservar una
explicación de aumento, disminución o invariancia si los datos nuevos la contradicen.
El manifiesto 1.2 requiere `auditoria.generacion_verificada` concordante con la
generación efectivamente revisada; no actualizar esa evidencia sin revisar.

La autorización del 22-oct-2026 abarca el método y los futuros materiales de
estudio. No volver a preguntar formatos o archivo. Revisar datos y derechos antes
de publicar originales privados en este repositorio público, conforme a la skill.
