#!/usr/bin/env python3
"""Comprueba propagación real sin alterar el piloto ni sus salidas finales.

Requiere reportlab (generación) y pypdf (lectura de texto y enlaces).
Ejecutar: python3 editables/probar_regresion.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
from copy import deepcopy
from fractions import Fraction
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
    require(manifest["schema_version"] == "1.2", "El manifiesto debe usar schema 1.2")
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
        original_content = load(root / "contenido.json")
        original_map = load(root / "mapa.json")
        original_sources = load(root / "fuentes.json")
        require(original_content["schema_version"] == "1.1",
                "El contenido debe usar schema 1.1, con referencias a bloques")

        def run(*options, success=True):
            process = subprocess.run(
                [sys.executable, str(root / "editables/generar.py"),
                 "--root", str(root), *options],
                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if success:
                require(process.returncode == 0,
                        "Falló la generación temporal:\n" + process.stdout + process.stderr)
            else:
                require(process.returncode != 0, "Se aceptó una entrada que debía rechazarse")
            return process

        def generated_hashes():
            return {name: digest(root / name) for name in (
                "salidas/pizarra.pdf", "salidas/cuaderno.pdf", "contenido.md",
                "revision/calculos.json", "manifest.json", "revision/auditoria.json")}

        def restore():
            save(root / "contenido.json", original_content)
            save(root / "mapa.json", original_map)
            save(root / "fuentes.json", original_sources)

        def pending_snapshot():
            manifest = validate_hashes(root)
            audit = load(root / "revision/auditoria.json")
            require(manifest["estado"] == "borrador", "Generar no puede aprobar la revisión")
            for name, document in (("manifiesto", manifest["auditoria"]),
                                   ("auditoría", audit)):
                require("generacion_verificada" in document and
                        document["generacion_verificada"] is None,
                        name + ": regenerar debe dejar snapshot explícitamente null")
            for key in ("contenido", "visual", "correspondencia", "reproduccion", "archivo"):
                require(audit[key]["estado"] == "pendiente", "Auditoría reaprobada al generar")
            return manifest

        run()
        pending_snapshot()
        baseline_view = (root / "contenido.md").read_text(encoding="utf-8")
        baseline_pdf_hashes = {name: digest(root / "salidas" / f"{name}.pdf")
                               for name in ("pizarra", "cuaderno")}

        content = deepcopy(original_content)
        content["datos"]["principal"][-1] = 90
        content["datos"]["ejercicio"][-1] = 78
        content["textos"]["comun"]["titulo"] += " REGR-TEXTO"
        explanation = ("Elegir depende de la pregunta: el total y el centro "
                       "responden cosas distintas. REGR-EXPLICACION")
        content["textos"]["compartidos"]["elegir"] = explanation
        content["version"] = "1.2.0-prueba"
        save(root / "contenido.json", content)
        concept_map = deepcopy(original_map)
        concept_map["version"] = content["version"]
        save(root / "mapa.json", concept_map)
        sources = deepcopy(original_sources)
        sources[0]["titulo"] += " REGR-FUENTE"
        sources[0]["url_o_identificador"] = "https://example.org/fuente-regresion"
        save(root / "fuentes.json", sources)
        # La vista se corrompe adrede: debe reemplazarse, no consumirse como fuente.
        (root / "contenido.md").write_text("VISTA-OBSOLETA-NO-CANONICA\n", encoding="utf-8")
        run()

        for name, expected_pages in (("pizarra", 1), ("cuaderno", 3)):
            pdf = root / "salidas" / f"{name}.pdf"
            text, urls, pages = read_pdf(pdf)
            tight = compact(text)
            require(pages == expected_pages, f"Cambió la composición de {name}")
            require(digest(pdf) != baseline_pdf_hashes[name], f"{name} no cambió")
            for token in ("REGR-TEXTO", "REGR-FUENTE", "1.2.0-prueba"):
                require(token in text, f"{name}: no propagó {token}")
            require(compact(explanation) in tight,
                    f"{name}: no propagó la explicación sustantiva compartida")
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
            result[name] = {"paginas": pages, "propagacion": "correcta",
                            "explicacion_sustantiva": "compartida y presente"}

        view = (root / "contenido.md").read_text(encoding="utf-8")
        require(view != baseline_view, "La vista no cambió")
        require("VISTA-OBSOLETA-NO-CANONICA" not in view, "No se regeneró la vista")
        for token in ("90", "78", "REGR-TEXTO", "REGR-FUENTE", "1.2.0-prueba", explanation):
            require(token in view, f"La vista no propagó {token}")
        manifest = pending_snapshot()
        require(manifest["version"] == "1.2.0-prueba", "Versión obsoleta en manifiesto")

        # La misma generación no demuestra una revisión: manifest-only exige evidencia
        # coincidente y conserva el estado pendiente si nadie la aprobó.
        before = generated_hashes()
        run("--manifest-only", success=False)
        require(generated_hashes() == before, "manifest-only fallido modificó las salidas")
        audit = load(root / "revision/auditoria.json")
        audit["generacion_verificada"] = manifest["generacion"]
        save(root / "revision/auditoria.json", audit)
        run("--manifest-only")
        checked = validate_hashes(root)
        require(checked["estado"] == "borrador", "Snapshot coincidente no debe autoaprobar")
        require(checked["auditoria"]["generacion_verificada"] == checked["generacion"],
                "El manifiesto perdió el snapshot verificado")
        for key in ("contenido", "visual", "correspondencia", "reproduccion", "archivo"):
            audit[key]["estado"] = "aprobada"
            audit[key]["evidencia"] = "Aprobación simulada solo en la copia temporal de prueba."
        save(root / "revision/auditoria.json", audit)
        run("--manifest-only")
        checked = validate_hashes(root)
        require(checked["estado"] == "revisado", "No aplica el estado con evidencia coincidente")
        require(checked["auditoria"]["generacion_verificada"] == checked["generacion"],
                "Estado revisado sin snapshot de generación coincidente")
        content["textos"]["compartidos"]["elegir"] += " Cambio posterior."
        save(root / "contenido.json", content)
        before = generated_hashes()
        run("--manifest-only", success=False)
        require(generated_hashes() == before, "Snapshot obsoleto modificó las salidas")
        run()
        pending_snapshot()
        result["auditoria"] = "null al regenerar; coincidencia exigida; sin autoaprobación"

        restore()
        content = deepcopy(original_content)
        content["datos"]["principal"] = [10, 20, 20, 20, 80]
        content["datos"]["comparacion"]["base"] = 100
        content["datos"]["sustitucion_ejercicio"] = 100
        save(root / "contenido.json", content)
        run()
        calculations = load(root / "revision/calculos.json")
        require(Fraction(calculations["resultados"]["principal"]["media"]) == 30,
                "Media de repetidos incorrecta")
        require(Fraction(calculations["resultados"]["retirado"]["mediana"]) == 20,
                "Retirar conserva aquí la mediana 20")
        require(Fraction(str(calculations["cambio_media"]).replace(",", ".")) == -4,
                "Cambio de la media principal incorrecto")
        require(Fraction(str(calculations["cambio_media_ejercicio"]).replace(",", ".")) == Fraction(32, 5),
                "Cambio del ejercicio incorrecto")
        for name in ("pizarra", "cuaderno"):
            text, _, _ = read_pdf(root / "salidas" / f"{name}.pdf")
            require("media baja" in " ".join(text.lower().split()), f"{name}: dirección principal incorrecta")
            require(not re.search(r"(?:sube|baja)\s*-", text, re.I),
                    f"{name}: dirección con magnitud negativa")
            if name == "cuaderno":
                require("media sube" in " ".join(text.lower().split()), "Ejercicio ascendente descrito como descenso")
                require(re.search(r"(?:mediana[^.]*conserva|conserva[^.]*mediana|mediana[^.]*sigue)[^.]*20", text, re.I),
                        "No se explica que retirar conserva la mediana con repetidos")
        result["repetidos_y_direcciones"] = "base 100: media baja 4; sustitución 100: sube 6,4; retiro conserva mediana 20"

        restore()
        content = deepcopy(original_content)
        content["datos"]["comparacion"]["base"] = 80
        content["datos"]["sustitucion_ejercicio"] = 68
        save(root / "contenido.json", content)
        run()
        calculations = load(root / "revision/calculos.json")
        require(Fraction(str(calculations["cambio_media"]).replace(",", ".")) == 0 and
                Fraction(str(calculations["cambio_media_ejercicio"]).replace(",", ".")) == 0,
                "Cambios nulos mal calculados")
        for name in ("pizarra", "cuaderno"):
            text, _, _ = read_pdf(root / "salidas" / f"{name}.pdf")
            require("media no cambia" in " ".join(text.lower().split()),
                    f"{name}: dirección neutra incorrecta")
        result["cambio_nulo"] = "la media no cambia en ambos escenarios"

        restore()
        content = deepcopy(original_content)
        content["datos"]["principal"] = [10.1, 15.2, 20.3, 25.4, 80.5]
        content["datos"]["comparacion"] = {"base": 30.6, "aumentado": 180.7}
        content["datos"]["ejercicio"] = [12.1, 16.1, 20.1, 24.1, 68.1]
        content["datos"]["sustitucion_ejercicio"] = 28.2
        save(root / "contenido.json", content)
        run()
        calculations = load(root / "revision/calculos.json")
        expected = {"base": (Fraction(508, 25), Fraction(203, 10)),
                    "principal": (Fraction(303, 10), Fraction(203, 10)),
                    "aumentado": (Fraction(2517, 50), Fraction(203, 10)),
                    "retirado": (Fraction(71, 4), Fraction(71, 4)),
                    "ejercicio": (Fraction(281, 10), Fraction(201, 10)),
                    "sustitucion": (Fraction(503, 25), Fraction(201, 10))}
        for scenario, (mean, median) in expected.items():
            actual = calculations["resultados"][scenario]
            require(Fraction(actual["media"]) == mean and Fraction(actual["mediana"]) == median,
                    "Aritmética decimal inexacta: " + scenario)
        require(Fraction(str(calculations["cambio_media"]).replace(",", ".")) == Fraction(499, 50),
                "Delta decimal inexacto")
        for name in ("pizarra", "cuaderno"):
            text, _, _ = read_pdf(root / "salidas" / f"{name}.pdf")
            require("151,5/5=30,3min" in compact(text), f"{name}: decimal mal mostrado")
        result["decimales"] = "fracciones exactas y coma decimal en ambos PDF"

        # Todas las entradas inválidas deben fallar antes de reescribir un resultado.
        rejected = []
        invalid = [("principal_bool", ("principal", 0), True),
                   ("principal_nan", ("principal", 0), float("nan")),
                   ("principal_infinito", ("principal", 0), float("inf")),
                   ("ejercicio_bool", ("ejercicio", 0), False),
                   ("comparacion_bool", ("comparacion", "base"), True),
                   ("comparacion_nan", ("comparacion", "base"), float("nan")),
                   ("comparacion_infinito", ("comparacion", "aumentado"), float("inf")),
                   ("sustitucion_bool", ("sustitucion_ejercicio",), True),
                   ("sustitucion_nan", ("sustitucion_ejercicio",), float("nan")),
                   ("sustitucion_infinito", ("sustitucion_ejercicio",), float("inf")),
                   ("negativo", ("principal", 0), -1),
                   ("mas_de_dos_decimales", ("principal", 0), 10.001),
                   ("fuera_de_escala", ("principal", 0), 1000),
                   ("centro_incompatible", ("sustitucion_ejercicio",), 1),
                   ("principal_sin_maximo_estricto", ("principal",), [20, 20, 20, 20, 20]),
                   ("ejercicio_sin_maximo_estricto", ("ejercicio",), [20, 20, 20, 20, 20])]
        for label, path, value in invalid:
            content = deepcopy(original_content)
            target = content["datos"]
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            save(root / "contenido.json", content)
            before = generated_hashes()
            process = run(success=False)
            require("ValueError" in process.stderr,
                    label + ": debe rechazarse explícitamente por validación")
            if label.endswith("sin_maximo_estricto"):
                require("máximo estricto" in process.stderr,
                        label + ": falta explicación de la premisa incumplida")
            require(generated_hashes() == before, label + ": rechazo tardío, modificó salidas")
            rejected.append(label)
        content = deepcopy(original_content)
        content["secciones"][4]["parrafos"] = ["Excepción sustantiva que no puede ignorarse."]
        save(root / "contenido.json", content)
        before = generated_hashes()
        process = run(success=False)
        require("parrafos" in process.stderr, "No identifica el campo antiguo rechazado")
        require(generated_hashes() == before, "Campo antiguo: rechazo tardío")
        rejected.append("secciones.parrafos_antiguo")
        for label, reference, expected_error in (
                ("bloque_huerfano", "cuaderno.nuevo", "no utilizado"),
                ("referencia_inexistente", "cuaderno.inexistente", "inexistente")):
            content = deepcopy(original_content)
            if label == "bloque_huerfano":
                content["textos"]["cuaderno"]["nuevo"] = "Matiz que debe llegar al PDF."
            content["secciones"][4]["bloques"].append(reference)
            save(root / "contenido.json", content)
            before = generated_hashes()
            process = run(success=False)
            require(expected_error in process.stderr.lower(),
                    label + ": falta rechazo explícito y reconocible")
            require(generated_hashes() == before, label + ": rechazo modificó salidas")
            rejected.append(label)
        result["rechazos_antes_de_publicar_salidas"] = rejected

    current_hashes = {str(path.relative_to(original)): digest(path)
                      for path in original.rglob("*") if path.is_file()}
    require(current_hashes == original_hashes, "La prueba modificó el piloto original")
    print(json.dumps({"estado": "aprobada", "pruebas": result,
                      "vista_derivada": "regenerada sin consumir su contenido previo",
                      "hashes_manifest": "correctos", "piloto_original": "sin cambios",
                      "limites": "Regresión funcional del piloto; no demuestra equivalencia semántica de síntesis ni reemplaza inspección visual."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
