# Regeneración del piloto 1.1.0

Desde la carpeta del tema: `python3 editables/generar.py`.

`contenido.json` es la única fuente canónica de identidad, versión, datos, explicaciones y síntesis para las dos composiciones. Los cálculos y las tablas se derivan de los datos; los textos usan marcadores `{principal_media}`, `{ejercicio_suma}`, etc. `fuentes.json` conserva el registro bibliográfico consumido por ambas salidas. `mapa.json` y `cobertura.json` se leen y validan antes de generar. El código solo compone y calcula. No editar `contenido.md`: se reemplaza como vista derivada, con desarrollo, síntesis y bibliografía.

El diseño del piloto admite cinco duraciones no negativas en cada ejemplo y sustitución del máximo sin alterar las posiciones centrales. Si se cambia el tamaño o esta premisa, el generador falla con una explicación: adaptar composición y textos antes de generar. La identidad y versión de `mapa.json` deben coincidir con `contenido.json`.

Dependencias de generación: Python 3 y `reportlab`. Busca DejaVu Sans en el sistema; si no está disponible usa Bitstream Vera incluida en ReportLab, con aviso. Para elegir una carpeta: `python3 editables/generar.py --font-dir RUTA`; también puede usarse `PIZARRAS_FONT_DIR`. Se esperan `DejaVuSans.ttf` y `DejaVuSans-Bold.ttf`, o `Vera.ttf` y `VeraBd.ttf`. No hay rutas de salida absolutas ni servicios remotos. `--root RUTA` permite trabajar con una copia. El entorno y los hashes tipográficos se registran sin rutas absolutas.

El script produce `salidas/pizarra.pdf` (A1 horizontal), `salidas/cuaderno.pdf` (tres páginas Carta), `contenido.md`, `revision/calculos.json` y el manifiesto con hashes actuales. Usa PDF determinista para el mismo contenido, código y entorno. Regenerar siempre deja estado `borrador` y auditorías pendientes; que los bytes coincidan no acredita una revisión visual.

## Regresión

Instalar además `pypdf` y ejecutar `python3 editables/probar_regresion.py`. La prueba trabaja en una copia temporal, modifica datos, título común, versión y fuente; comprueba en el texto extraído de ambos PDF los cálculos, atribución, URL y versión actualizados. Corrompe la vista Markdown antes de generar para demostrar que no se consume como fuente. Comprueba hashes e integridad del original. El caso modificado es una prueba técnica de propagación, no material revisado para estudiar.

## Revisión final

Renderizar todas las páginas y el lienzo: `pdftoppm -r 100 -png salidas/cuaderno.pdf revision/cuaderno` y `pdftoppm -r 40 -png salidas/pizarra.pdf revision/pizarra-general`. Los recortes de detalle y grises pueden obtenerse con PyMuPDF. Inspeccionar de verdad cada imagen, los cálculos, remisiones, enlaces y cobertura. Las imágenes no son fuentes editables.

Registrar el resultado en `revision/auditoria.json`, incluyendo `generacion_verificada` igual al snapshot `generacion` del manifiesto revisado. Solo entonces `python3 editables/generar.py --manifest-only` refresca el inventario y aplica el estado respaldado por esa evidencia. Esta opción no regenera PDF ni aprueba auditorías: rechaza un snapshot distinto de los bytes y entorno actuales.
