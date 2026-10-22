"""Pruebas del contrato; usa PIZARRAS_VALIDATOR para probar otra instalación."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(os.environ.get("PIZARRAS_VALIDATOR", str(
    Path(__file__).resolve().parents[1] / "skills/pizarras-de-estudio/scripts/validar_paquete.py")))
# Compilar en memoria evita crear __pycache__ en la skill sometida a prueba.
MODULO = {"__name__": "validador_bajo_prueba"}
exec(compile(SCRIPT.read_text(encoding="utf-8"), str(SCRIPT), "exec"), MODULO)
validar = MODULO["validar"]


class PaqueteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "tema"
        self.root.mkdir()
        self.write("contenido.json", {"id": "ejemplo", "version": "1.0.0", "texto": "Ejemplo"})
        self.write("contenido.md", "# Ejemplo\nTema: ejemplo · Versión: 1.0.0\n\n## C01 · Inicio\n[F01, §1]\n\n## C02 · Resultado\nTexto.\n")
        self.fuentes = [{"id": "F01", "titulo": "Fuente", "autor_institucion": "Autor",
                         "tipo": "Libro", "fecha_edicion": None, "url_o_identificador": "ISBN-ejemplo",
                         "consulta": "2026-10-22", "alcance_leido": "§1", "localizadores": ["§1"],
                         "afirmaciones_respaldadas": ["C01"], "estado": "consultada", "limites": None}]
        self.mapa = {"schema_version": "1.0", "tema_id": "ejemplo", "version": "1.0.0",
                     "conceptos": [{"id": "C01", "titulo": "Inicio", "apartado": "C01 · Inicio"},
                                   {"id": "C02", "titulo": "Resultado", "apartado": "C02 · Resultado"}],
                     "relaciones": [{"desde": "C01", "hacia": "C02", "relacion": "permite",
                                     "fuentes": ["F01"], "justificacion": "C01 explica el vínculo"}],
                     "remisiones": [{"concepto_id": c, "paginas_cuaderno": [1], "zona_pizarra": c}
                                    for c in ("C01", "C02")]}
        self.cobertura = [{"entrada_id": "E01", "punto": "Pregunta inicial", "conceptos": ["C01", "C02"],
                           "estado": "incluido", "motivo": ""}]
        self.write("fuentes.json", self.fuentes)
        self.write("mapa.json", self.mapa)
        self.write("cobertura.json", self.cobertura)
        self.write("editables/generar.py", "# Fuente editable de prueba\n")
        self.write("salidas/pizarra.pdf", b"%PDF-fixture-estructural-pizarra")
        self.write("salidas/cuaderno.pdf", b"%PDF-fixture-estructural-cuaderno")
        self.manifest = {"schema_version": "1.1", "id": "ejemplo", "titulo": "Ejemplo", "version": "1.0.0",
                         "version_skill": "1.1.0", "fecha_revision": "2026-10-22", "estado": "revisado",
                         "alcance": "Ejemplo mínimo", "contenido_canonico": "contenido.json",
                         "vista_contenido": "contenido.md", "entradas": [{"id": "E01", "nombre": "Pregunta"}],
                         "reproduccion": {"comando": "python3 editables/generar.py", "dependencias": ["Python 3"]},
                         "pendientes": [], "auditoria": {t: {"estado": "aprobada", "evidencia": "Revisión documentada"}
                                                          for t in ("contenido", "visual", "correspondencia")}}
        self.refresh()

    def write(self, ruta, valor):
        p = self.root / ruta
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(valor, bytes):
            p.write_bytes(valor)
        else:
            p.write_text(valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False), encoding="utf-8")

    def refresh(self, snapshot=True):
        self.manifest["archivos"] = [{"ruta": p.relative_to(self.root).as_posix(), "funcion": "Fixture",
                                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                     for p in sorted(self.root.rglob("*")) if p.is_file() and p.name != "manifest.json"]
        if snapshot:
            self.manifest["generacion"] = {"entradas": [], "salidas": []}
            for r in self.manifest["archivos"]:
                vista = self.manifest.get("vista_contenido")
                derivada = r["ruta"] == vista and vista != self.manifest.get("contenido_canonico")
                destino = "salidas" if r["ruta"].startswith("salidas/") or derivada else "entradas"
                self.manifest["generacion"][destino].append({k: r[k] for k in ("ruta", "sha256")})
        self.write("manifest.json", self.manifest)

    def errors(self, *codigos):
        r = validar(self.root)
        self.assertFalse(r["ok"], r)
        self.assertFalse(r["paquete_doble_validado"])
        self.assertTrue(set(codigos) <= {x["codigo"] for x in r["errores"]}, r)
        return r

    def test_valido_cli_solo_lectura(self):
        antes = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r = json.loads(p.stdout)
        self.assertTrue(r["ok"] and r["paquete_doble_validado"])
        self.assertEqual(r["validacion"], "estructural")
        self.assertIn("No acredita veracidad", r["limites"])
        self.assertNotIn("contenido.md", {x["ruta"] for x in self.manifest["generacion"]["entradas"]})
        self.assertIn("contenido.md", {x["ruta"] for x in self.manifest["generacion"]["salidas"]})
        self.assertEqual(antes, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_canonico_markdown(self):
        self.manifest.update(contenido_canonico="contenido.md", vista_contenido=None)
        (self.root / "contenido.json").unlink()
        self.refresh()
        self.assertTrue(validar(self.root)["ok"])

    def test_salida_corrupta(self):
        self.write("salidas/cuaderno.pdf", b"cambiado")
        self.errors("hash_distinto")

    def test_contenido_cambia_sin_regenerar(self):
        self.write("contenido.json", {"id": "ejemplo", "version": "1.0.0", "texto": "Cambio sustantivo"})
        self.refresh(snapshot=False)
        self.errors("hash_distinto", "snapshot_registro")

    def test_falta_formato(self):
        (self.root / "salidas/cuaderno.pdf").unlink()
        self.refresh()
        self.errors("salida", "snapshot_salida")

    def test_referencias_rotas(self):
        self.mapa["relaciones"][0].update(hacia="C99", fuentes=["F99"])
        self.mapa["remisiones"][0]["concepto_id"] = "C99"
        self.write("mapa.json", self.mapa)
        self.refresh()
        self.errors("referencia")

    def test_ids_y_rutas_repetidos(self):
        self.mapa["conceptos"].append(self.mapa["conceptos"][0])
        self.fuentes.append(self.fuentes[0])
        self.write("mapa.json", self.mapa)
        self.write("fuentes.json", self.fuentes)
        self.refresh()
        self.manifest["archivos"].append(self.manifest["archivos"][0])
        self.write("manifest.json", self.manifest)
        self.errors("id_repetido", "ruta_repetida")

    def test_rutas_escapan(self):
        for ruta in ("../secreto", "/tmp/secreto", "C:/secreto", "dir/../secreto", "dir\\secreto"):
            with self.subTest(ruta=ruta):
                self.manifest["archivos"].append({"ruta": ruta, "funcion": "X", "sha256": "0" * 64})
                self.write("manifest.json", self.manifest)
                self.errors("ruta_insegura")
                self.manifest["archivos"].pop()

    def test_symlink_escape_y_alias(self):
        externo = self.root.parent / "externo"
        externo.write_text("secreto")
        p = self.root / "enlace"
        try:
            p.symlink_to(externo)
        except OSError as exc:
            self.skipTest(f"Este sistema no permite symlinks: {exc}")
        self.refresh()
        self.errors("ruta_insegura")
        p.unlink()
        p.symlink_to(self.root / "contenido.md")
        self.refresh()
        self.errors("ruta_repetida")

    def test_snapshot_alterado_y_autorreferencia(self):
        self.manifest["generacion"]["entradas"][0]["sha256"] = "0" * 64
        self.manifest["generacion"]["entradas"].append({"ruta": "manifest.json", "sha256": "0" * 64})
        self.write("manifest.json", self.manifest)
        self.errors("hash_distinto", "ruta_insegura")

    def test_falso_revisado_auditoria_y_pendientes(self):
        self.manifest["pendientes"] = ["Comprobar conclusión"]
        self.manifest["auditoria"]["visual"]["evidencia"] = " "
        self.write("manifest.json", self.manifest)
        self.errors("pendientes", "auditoria")
        self.manifest["pendientes"] = [{"descripcion": "Mejorar tono opcional", "sustantivo": False}]
        self.manifest["auditoria"]["visual"]["evidencia"] = "Revisada"
        self.write("manifest.json", self.manifest)
        r = validar(self.root)
        self.assertTrue(r["ok"], r)
        self.assertIn("pendiente_no_sustantivo", {a["codigo"] for a in r["avisos"]})
        self.manifest["reproduccion"] = {"comando": "", "dependencias": None}
        self.write("manifest.json", self.manifest)
        self.errors("reproduccion")

    def test_versiones_difieren(self):
        self.mapa["version"] = "2.0.0"
        self.write("mapa.json", self.mapa)
        self.write("contenido.json", {"id": "otro", "version": "2.0.0"})
        self.refresh()
        self.errors("version")

    def test_fuente_pendiente_en_cita_agrupada(self):
        self.fuentes.append(dict(self.fuentes[0], id="F02", estado="pendiente"))
        self.write("fuentes.json", self.fuentes)
        self.write("contenido.md", (self.root / "contenido.md").read_text().replace("[F01, §1]", "[F01; F02]"))
        self.refresh()
        self.errors("fuente_pendiente")
        self.fuentes[1]["estado"] = "consultada"
        for campo, vacio in (("titulo", ""), ("autor_institucion", None), ("tipo", " "),
                             ("url_o_identificador", None), ("consulta", None), ("alcance_leido", ""),
                             ("localizadores", []), ("afirmaciones_respaldadas", None)):
            with self.subTest(campo=campo):
                anterior = self.fuentes[1][campo]
                self.fuentes[1][campo] = vacio
                self.write("fuentes.json", self.fuentes)
                self.refresh()
                self.errors("fuente_evidencia")
                self.fuentes[1][campo] = anterior

    def test_paginas_y_apartados(self):
        self.mapa["conceptos"][0]["apartado"] = "Encabezado inexistente"
        for pagina in (True, 0, -1, 1.5, "1"):
            with self.subTest(pagina=pagina):
                self.mapa["remisiones"][0]["paginas_cuaderno"] = [pagina]
                self.write("mapa.json", self.mapa)
                self.refresh()
                self.errors("pagina", "apartado")

    def test_borrador_incompleto_y_corrupcion_siempre_error(self):
        for estado in ("borrador", "parcial"):
            self.manifest["estado"] = estado
            self.manifest["pendientes"] = ["Revisar fuente"]
            self.write("manifest.json", self.manifest)
            r = validar(self.root)
            self.assertTrue(r["ok"], r)
            self.assertFalse(r["paquete_doble_validado"])
            self.assertTrue(r["avisos"])
        self.write("contenido.json", "null")
        self.errors("hash_distinto", "canonico")

    def test_historico_no_es_paquete_doble(self):
        self.manifest = {"schema_version": "1.0", "estado": "referencia_historica",
                         "archivos": [self.manifest["archivos"][-1]]}
        self.write("manifest.json", self.manifest)
        r = validar(self.root)
        self.assertTrue(r["ok"])
        self.assertFalse(r["paquete_doble_validado"])
        self.assertIn("historico", {a["codigo"] for a in r["avisos"]})
        self.write(self.manifest["archivos"][0]["ruta"], b"cambio")
        self.errors("hash_distinto")

    def test_cobertura_completa_y_exclusiones(self):
        self.manifest["entradas"].append({"id": "E02", "nombre": "Página adicional"})
        self.cobertura[0].update(estado="corregido", motivo="")
        self.write("cobertura.json", self.cobertura)
        self.refresh()
        self.errors("cobertura", "cobertura_ausente")
        self.manifest["entradas"][1].update(relevante=False, sin_contenido="Portada sin contenido de estudio")
        self.cobertura[0]["motivo"] = "Se corrigió el cálculo con fuente F01"
        self.write("cobertura.json", self.cobertura)
        self.refresh()
        self.assertTrue(validar(self.root)["ok"])

    def test_cobertura_pendiente_o_referencia_rota(self):
        self.cobertura[0].update(entrada_id="E99", estado="pendiente", conceptos=["C99"])
        self.write("cobertura.json", self.cobertura)
        self.refresh()
        self.errors("cobertura_entrada", "cobertura_pendiente", "referencia")

    def test_snapshot_omite_editable(self):
        self.manifest["generacion"]["entradas"] = [r for r in self.manifest["generacion"]["entradas"]
                                                     if not r["ruta"].startswith("editables/")]
        self.write("manifest.json", self.manifest)
        self.errors("snapshot_entrada")
        self.refresh()
        self.manifest["generacion"]["salidas"] = [r for r in self.manifest["generacion"]["salidas"] if r["ruta"] != "contenido.md"]
        self.write("manifest.json", self.manifest)
        self.errors("snapshot_salida")

    def test_json_y_tipos_invalidos_devuelven_json(self):
        self.mapa["conceptos"][0]["apartado"] = []
        self.mapa["relaciones"][0]["desde"] = {}
        self.write("mapa.json", self.mapa)
        self.refresh()
        self.errors("apartado", "referencia")
        for valor in ("{", "null", "[]", '{"estado": "revisado", "archivos": null}'):
            with self.subTest(valor=valor):
                self.write("manifest.json", valor)
                p = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
                self.assertEqual(p.returncode, 1, p.stderr)
                self.assertFalse(json.loads(p.stdout)["ok"])
                self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
