#!/usr/bin/env python3
"""Comprueba propagación real sin alterar el piloto ni sus salidas finales.

Requiere reportlab (generación) y pypdf (lectura de texto y enlaces).
Ejecutar: python3 editables/probar_regresion.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

from pypdf import PdfReader


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def compact(text):
    return re.sub(r"\s+", "", text)


def read_pdf(path):
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    urls = []
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            action = annotation.get("/A")
            if action:
                action = action.get_object()
                if action.get("/URI"):
                    urls.append(str(action["/URI"]))
    return text, urls, len(reader.pages)


def validate_hashes(root):
    manifest = load(root / "manifest.json")
    require(manifest["schema_version"] == "1.1", "El manifiesto debe usar schema 1.1")
    require(manifest["contenido_canonico"] == "contenido.json", "Falta el canónico declarado")
    require(manifest["vista_contenido"] == "contenido.md", "Falta la vista derivada declarada")
    generation = manifest["generacion"]
    inputs = {entry["ruta"] for entry in generation["entradas"]}
    outputs = {entry["ruta"] for entry in generation["salidas"]}
    require({"contenido.json", "fuentes.json", "mapa.json", "editables/generar.py"} <= inputs,
            "No están declaradas todas las entradas mínimas de generación")
    require({"salidas/pizarra.pdf", "salidas/cuaderno.pdf", "contenido.md"} <= outputs,
            "No están declaradas las tres salidas obligatorias")
    require("contenido.md" not in inputs, "La vista derivada no puede ser otra fuente")
    for entries in (generation["entradas"], generation["salidas"], manifest["archivos"]):
        paths = [entry["ruta"] for entry in entries]
        require(len(paths) == len(set(paths)), "Hay rutas duplicadas en el manifiesto")
        for entry in entries:
            path = Path(entry["ruta"])
            require(not path.is_absolute() and ".." not in path.parts, "Ruta no portable")
            require(path.as_posix() != "manifest.json", "Hash circular del manifiesto")
            require((root / path).is_file(), f"Archivo ausente: {path}")
            require(digest(root / path) == entry["sha256"], f"Hash incorrecto: {path}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    original = args.root.resolve()
    original_hashes = {str(path.relative_to(original)): digest(path)
                       for path in original.rglob("*") if path.is_file()}
    result = {}
    with TemporaryDirectory(prefix="media-mediana-regresion-") as directory:
        root = Path(directory) / "tema"
        shutil.copytree(original, root, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "*.png", "*.pdf"))

        def generate():
            process = subprocess.run(
                [sys.executable, str(root / "editables/generar.py"), "--root", str(root)],
                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            require(process.returncode == 0,
                    "Falló la generación temporal:\n" + process.stdout + process.stderr)

        generate()
        baseline_view = (root / "contenido.md").read_text(encoding="utf-8")
        baseline_pdf_hashes = {name: digest(root / "salidas" / f"{name}.pdf")
                               for name in ("pizarra", "cuaderno")}
        validate_hashes(root)

        content = load(root / "contenido.json")
        content["datos"]["principal"][-1] = 90
        content["datos"]["ejercicio"][-1] = 78
        content["textos"]["comun"]["titulo"] += " REGR-TEXTO"
        content["version"] = "1.1.0-prueba"
        save(root / "contenido.json", content)
        concept_map = load(root / "mapa.json")
        concept_map["version"] = content["version"]
        save(root / "mapa.json", concept_map)
        sources = load(root / "fuentes.json")
        sources[0]["titulo"] += " REGR-FUENTE"
        sources[0]["url_o_identificador"] = "https://example.org/fuente-regresion"
        save(root / "fuentes.json", sources)
        # Esta vista se corrompe adrede: el generador debe reemplazarla y no leerla.
        (root / "contenido.md").write_text("VISTA-OBSOLETA-NO-CANONICA\n", encoding="utf-8")
        generate()

        for name, expected_pages in (("pizarra", 1), ("cuaderno", 3)):
            pdf = root / "salidas" / f"{name}.pdf"
            text, urls, pages = read_pdf(pdf)
            tight = compact(text)
            require(pages == expected_pages, f"Cambió la composición de {name}")
            require(digest(pdf) != baseline_pdf_hashes[name], f"{name} no cambió")
            for token in ("REGR-TEXTO", "REGR-FUENTE", "1.1.0-prueba"):
                require(token in text, f"{name}: no propagó {token}")
            require("160/5=32min" in tight, f"{name}: no recalculó la media principal")
            require(re.search(r"(?:Dato central\s*=|valor central es)\s*20\s+min", text),
                    f"{name}: falta la mediana principal de 20 min")
            require("https://example.org/fuente-regresion" in urls,
                    f"{name}: no propagó el enlace de la fuente")
            require("VISTA-OBSOLETA-NO-CANONICA" not in text,
                    f"{name}: leyó la vista derivada como fuente")
            if name == "pizarra":
                require("12,16,20,24,78min" in tight, "Pizarra: ejercicio obsoleto")
                require("Media=150/5=30min" not in tight,
                        "Pizarra: se reveló la solución del ejercicio")
            else:
                require("12+16+20+24+78=150min" in tight,
                        "Cuaderno: no recalculó la suma del ejercicio")
                require("Media=150/5=30min" in tight,
                        "Cuaderno: no recalculó la media del ejercicio")
            result[name] = {"paginas": pages, "propagacion": "correcta"}

        view = (root / "contenido.md").read_text(encoding="utf-8")
        require(view != baseline_view, "La vista no cambió")
        require("VISTA-OBSOLETA-NO-CANONICA" not in view, "No se regeneró la vista")
        for token in ("90", "78", "REGR-TEXTO", "REGR-FUENTE", "1.1.0-prueba"):
            require(token in view, f"La vista no propagó {token}")
        manifest = validate_hashes(root)
        require(manifest["version"] == "1.1.0-prueba", "Versión obsoleta en manifiesto")

    current_hashes = {str(path.relative_to(original)): digest(path)
                      for path in original.rglob("*") if path.is_file()}
    require(current_hashes == original_hashes, "La prueba modificó el piloto original")
    print(json.dumps({"estado": "aprobada", "pruebas": result,
                      "vista_derivada": "regenerada sin consumir su contenido previo",
                      "hashes_manifest": "correctos", "piloto_original": "sin cambios"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
