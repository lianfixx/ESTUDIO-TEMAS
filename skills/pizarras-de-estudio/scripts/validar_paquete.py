#!/usr/bin/env python3
"""Valida estructura e integridad; no genera archivos ni acredita veracidad o diseño."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath


class Validador:
    def __init__(self, carpeta):
        self.root = Path(carpeta).resolve()
        self.errores, self.avisos = [], []
        self.estado = None

    def mensaje(self, codigo, texto, aviso=False):
        (self.avisos if aviso else self.errores).append({"codigo": codigo, "mensaje": texto})

    def requerido(self, condicion, codigo, texto):
        if not condicion:
            self.mensaje(codigo, texto, aviso=self.estado in ("borrador", "parcial"))

    def ruta(self, valor, contexto, manifest=False):
        if (not isinstance(valor, str) or not valor or "\\" in valor
                or PureWindowsPath(valor).drive or PurePosixPath(valor).is_absolute()
                or ".." in PurePosixPath(valor).parts or str(PurePosixPath(valor)) != valor
                or valor == "."):
            self.mensaje("ruta_insegura", f"{contexto}: ruta relativa no válida: {valor!r}")
            return None
        try:
            p = (self.root / valor).resolve()
            p.relative_to(self.root)
            if not manifest and p == (self.root / "manifest.json").resolve():
                raise ValueError("autorreferencia al manifiesto")
        except (OSError, RuntimeError, ValueError) as exc:
            self.mensaje("ruta_insegura", f"{contexto}: {valor!r}: {exc}")
            return None
        return p

    def leer(self, ruta, json_obj=False, manifest=False):
        p = self.ruta(ruta, "lectura", manifest)
        if p is None:
            return None
        try:
            texto = p.read_text(encoding="utf-8")
            return json.loads(texto) if json_obj else texto
        except (OSError, UnicodeError, ValueError) as exc:
            self.mensaje("lectura", f"{ruta}: {exc}")
            return None

    def lista(self, valor, contexto):
        if not isinstance(valor, list):
            self.mensaje("tipo", f"{contexto} debe ser una lista")
            return []
        return valor

    def registros(self, valor, contexto, funcion=False):
        encontrados, destinos = {}, set()
        for item in self.lista(valor, contexto):
            if not isinstance(item, dict):
                self.mensaje("tipo", f"{contexto}: cada registro debe ser un objeto")
                continue
            nombre, digest = item.get("ruta"), item.get("sha256")
            p = self.ruta(nombre, contexto)
            if p is None:
                continue
            if nombre in encontrados or p in destinos:
                self.mensaje("ruta_repetida", f"{contexto}: {nombre}")
            encontrados[nombre] = digest
            destinos.add(p)
            if funcion and not texto_no_vacio(item.get("funcion")):
                self.mensaje("funcion", f"{contexto}: falta función en {nombre}")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                self.mensaje("hash_formato", f"{contexto}: SHA-256 no válido en {nombre}")
            try:
                h = hashlib.sha256()
                with p.open("rb") as f:
                    for bloque in iter(lambda: f.read(1024 * 1024), b""):
                        h.update(bloque)
                if h.hexdigest() != digest:
                    self.mensaje("hash_distinto", f"{contexto}: bytes modificados en {nombre}")
            except OSError as exc:
                self.mensaje("archivo_ausente", f"{contexto}: {nombre}: {exc}")
        return encontrados

    def objetos_id(self, valor, contexto):
        resultado = {}
        for item in self.lista(valor, contexto):
            if not isinstance(item, dict) or not texto_no_vacio(item.get("id")):
                self.mensaje("id", f"{contexto}: registro sin ID válido")
            elif item["id"] in resultado:
                self.mensaje("id_repetido", f"{contexto}: {item['id']}")
            else:
                resultado[item["id"]] = item
        return resultado

    def validar(self):
        m = self.leer("manifest.json", json_obj=True, manifest=True)
        if not isinstance(m, dict):
            self.mensaje("manifest", "Se necesita un manifiesto JSON de tipo objeto")
            return self.resultado()
        self.estado = m.get("estado")
        archivos = self.registros(m.get("archivos", []), "archivos", funcion=True)
        if self.estado == "referencia_historica" and m.get("schema_version") == "1.0":
            self.mensaje("historico", "Solo se comprobaron archivos y hashes; no es un paquete doble validado.", True)
            return self.resultado()
        if m.get("schema_version") != "1.2":
            self.mensaje("schema", "El paquete doble requiere manifest schema_version 1.2; "
                         "migrar desde 1.1 exige regenerar y revisar las salidas, no solo cambiar el número.")
        if self.estado not in ("borrador", "parcial", "revisado"):
            self.mensaje("estado", "Estado de paquete doble no válido")
        for campo in ("id", "titulo", "version", "version_skill", "fecha_revision", "alcance"):
            self.requerido(texto_no_vacio(m.get(campo)), "campo", f"Falta {campo} en el manifiesto")
        canon = m.get("contenido_canonico")
        vista = m.get("vista_contenido")
        canon_tipo = None
        texto = ""
        if canon is not None:
            p = self.ruta(canon, "contenido_canonico")
            if p is not None:
                canon_tipo = p.suffix
                if p.suffix not in (".md", ".json"):
                    self.mensaje("canonico", "El contenido canónico debe ser .md o .json")
                elif p.suffix == ".json":
                    datos = self.leer(canon, json_obj=True)
                    if not isinstance(datos, dict):
                        self.mensaje("canonico", "El JSON canónico debe ser un objeto")
                    elif datos.get("id") != m.get("id") or datos.get("version") != m.get("version"):
                        self.mensaje("version", "ID/versión del JSON canónico no coinciden con el manifiesto")
                else:
                    texto = self.leer(canon) or ""
        self.requerido(canon is not None, "canonico", "Falta contenido_canonico")
        if canon_tipo == ".md" and vista is not None:
            self.mensaje("vista", "Con contenido canónico Markdown, vista_contenido debe ser null; "
                         "la vista no puede ocultar el contenido canónico.")
        if canon_tipo == ".json":
            self.requerido(isinstance(vista, str) and vista != canon, "vista",
                           "El contenido canónico JSON requiere una vista Markdown derivada y distinta.")
        if vista is not None and canon_tipo != ".md":
            p = self.ruta(vista, "vista_contenido")
            if p is not None and p.suffix != ".md":
                self.mensaje("vista", "vista_contenido debe ser .md o null")
            elif p is not None:
                texto = self.leer(vista) or ""
        meta = re.search(r"^Tema:\s*(.*?)\s*·\s*Versión:\s*([^\s·]+)", texto, re.M)
        if meta and (meta[1] != m.get("id") or meta[2] != m.get("version")):
            self.mensaje("version", "ID/versión visibles del Markdown no coinciden con el manifiesto")
        obligatorios = {"fuentes.json", "mapa.json", "cobertura.json"}
        obligatorios.update(x for x in (canon, vista) if isinstance(x, str))
        for nombre in obligatorios:
            self.requerido(nombre in archivos, "registro", f"Falta {nombre} en archivos")
        fuentes = self.leer("fuentes.json", True) if (self.root / "fuentes.json").exists() else []
        mapa = self.leer("mapa.json", True) if (self.root / "mapa.json").exists() else {}
        conceptos = self.validar_mapa(mapa, fuentes, texto, m)
        cobertura = self.leer("cobertura.json", True) if (self.root / "cobertura.json").exists() else []
        self.validar_cobertura(cobertura, m.get("entradas", []), conceptos)
        editables = {x for x in archivos if x.startswith("editables/")}
        carpeta_editables = self.ruta("editables", "editables")
        for p in (self.root / "editables").rglob("*") if carpeta_editables else ():
            if p.is_file() and "__pycache__" not in p.parts:
                nombre = p.relative_to(self.root).as_posix()
                editables.add(nombre)
                self.ruta(nombre, "editables")
                self.requerido(nombre in archivos, "registro", f"Editable no registrado: {nombre}")
        self.requerido(bool(editables), "editables", "Faltan fuentes editables")
        salidas = {"salidas/pizarra.pdf", "salidas/cuaderno.pdf"}
        vista_derivada = canon_tipo == ".json" and isinstance(vista, str) and vista != canon
        if vista_derivada:
            salidas.add(vista)
        for nombre in salidas:
            self.requerido(nombre in archivos, "salida", f"Falta {nombre} en archivos")
        gen = m.get("generacion")
        if not isinstance(gen, dict):
            if gen is not None:
                self.mensaje("tipo", "generacion debe ser un objeto")
            self.requerido(False, "generacion", "Falta snapshot de generación")
        else:
            entradas = self.registros(gen.get("entradas", []), "generacion.entradas")
            productos = self.registros(gen.get("salidas", []), "generacion.salidas")
            insumos = obligatorios - ({vista} if vista_derivada else set())
            for nombre in insumos | editables:
                self.requerido(nombre in entradas, "snapshot_entrada", f"Falta entrada de generación: {nombre}")
            for nombre in salidas:
                self.requerido(nombre in productos, "snapshot_salida", f"Falta salida de generación: {nombre}")
            for nombre in entradas.keys() & productos.keys():
                self.mensaje("snapshot_circular", f"Entrada y salida simultáneas: {nombre}")
            for nombre, digest in list(entradas.items()) + list(productos.items()):
                if nombre not in archivos or archivos[nombre] != digest:
                    self.mensaje("snapshot_registro", f"Snapshot no coincide con archivos: {nombre}")
        reproduccion = m.get("reproduccion")
        self.requerido(isinstance(reproduccion, dict) and texto_no_vacio(reproduccion.get("comando"))
                       and isinstance(reproduccion.get("dependencias"), list) and bool(reproduccion["dependencias"])
                       and all(texto_no_vacio(x) for x in reproduccion["dependencias"]),
                       "reproduccion", "Falta comando de reproducción y lista de dependencias no vacíos")
        auditoria = m.get("auditoria", {})
        if not isinstance(auditoria, dict):
            self.mensaje("tipo", "auditoria debe ser un objeto")
        for tipo in ("contenido", "visual", "correspondencia"):
            a = auditoria.get(tipo, {}) if isinstance(auditoria, dict) else {}
            self.requerido(isinstance(a, dict) and a.get("estado") == "aprobada"
                           and texto_no_vacio(a.get("evidencia")), "auditoria", f"Falta auditoría {tipo} aprobada con evidencia")
        verificada = auditoria.get("generacion_verificada") if isinstance(auditoria, dict) else None
        if verificada is not None and not isinstance(verificada, dict):
            self.mensaje("tipo", "auditoria.generacion_verificada debe ser un objeto o null")
        if self.estado == "revisado":
            self.requerido(isinstance(gen, dict) and isinstance(verificada, dict)
                           and json.dumps(verificada, sort_keys=True) == json.dumps(gen, sort_keys=True),
                           "auditoria_generacion", "La auditoría aprobada debe identificar exactamente "
                           "la generación actual mediante auditoria.generacion_verificada; "
                           "revisar de nuevo si cambiaron sus insumos, salidas o entorno.")
        pendientes = self.lista(m.get("pendientes", []), "pendientes")
        sustantivos = [p for p in pendientes if not isinstance(p, dict) or p.get("sustantivo") is not False]
        for p in pendientes:
            if isinstance(p, dict) and (not texto_no_vacio(p.get("descripcion")) or type(p.get("sustantivo")) is not bool):
                self.mensaje("tipo", "Pendiente requiere descripción y sustantivo booleano")
            elif isinstance(p, dict) and p["sustantivo"] is False:
                self.mensaje("pendiente_no_sustantivo", p["descripcion"], True)
            elif not isinstance(p, dict) and not texto_no_vacio(p):
                self.mensaje("tipo", "Pendiente debe ser texto u objeto")
        self.requerido(not sustantivos, "pendientes", "Existen pendientes sustantivos")
        return self.resultado()

    def validar_mapa(self, mapa, fuentes, texto, manifest):
        fs = self.objetos_id(fuentes, "fuentes")
        campos = {"titulo", "autor_institucion", "tipo", "fecha_edicion", "url_o_identificador",
                  "consulta", "alcance_leido", "localizadores", "afirmaciones_respaldadas", "estado", "limites"}
        for id_, fuente in fs.items():
            self.requerido(campos <= fuente.keys(), "fuente_campos", f"{id_}: faltan campos de evidencia")
            if fuente.get("estado") not in ("consultada", "pendiente", "historica_no_reverificada"):
                self.mensaje("fuente_estado", f"{id_}: estado no válido")
            for campo in ("localizadores", "afirmaciones_respaldadas"):
                if fuente.get(campo) is not None:
                    for valor in self.lista(fuente[campo], f"{id_}.{campo}"):
                        if not texto_no_vacio(valor):
                            self.mensaje("tipo", f"{id_}.{campo}: se requiere texto no vacío")
        if not isinstance(mapa, dict):
            self.mensaje("mapa", "mapa.json debe ser un objeto")
            return {}
        self.requerido(bool(mapa), "mapa", "Falta mapa")
        if not mapa:
            return {}
        if mapa.get("schema_version") != "1.0":
            self.mensaje("schema_mapa", "mapa.json requiere schema_version 1.0")
        if mapa.get("tema_id") != manifest.get("id") or mapa.get("version") != manifest.get("version"):
            self.mensaje("version", "ID/versión de mapa no coinciden con el manifiesto")
        conceptos = self.objetos_id(mapa.get("conceptos", []), "conceptos")
        self.requerido(bool(conceptos), "conceptos", "Faltan conceptos")
        encabezados = set(re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", texto, re.M))
        for id_, concepto in conceptos.items():
            if (not texto_no_vacio(concepto.get("titulo")) or not isinstance(concepto.get("apartado"), str)
                    or concepto["apartado"] not in encabezados):
                self.mensaje("apartado", f"{id_}: título vacío o apartado Markdown inexistente")
        marcadores = re.findall(r"\[([^\]\n]+)\]", texto)
        usadas = {id_ for marca in marcadores for id_ in re.findall(r"\bF\d+\b", marca)}
        usadas.update(id_ for id_ in fs if any(re.search(r"(?<![\w-])" + re.escape(id_) + r"(?![\w-])", marca) for marca in marcadores))
        for r in self.lista(mapa.get("relaciones", []), "relaciones"):
            if not isinstance(r, dict):
                self.mensaje("relacion", "Cada relación debe ser un objeto")
                continue
            if any(not isinstance(r.get(k), str) or r[k] not in conceptos for k in ("desde", "hacia")):
                self.mensaje("referencia", "Relación con concepto inexistente")
            if not texto_no_vacio(r.get("relacion")) or not texto_no_vacio(r.get("justificacion")):
                self.mensaje("relacion", "Relación sin significado o justificación")
            for f in self.lista(r.get("fuentes", []), "relacion.fuentes"):
                if not isinstance(f, str):
                    self.mensaje("referencia", "ID de fuente no textual")
                else:
                    usadas.add(f)
        vistos = set()
        for r in self.lista(mapa.get("remisiones", []), "remisiones"):
            if not isinstance(r, dict):
                self.mensaje("remision", "Cada remisión debe ser un objeto")
                continue
            id_ = r.get("concepto_id")
            if not isinstance(id_, str) or id_ not in conceptos:
                self.mensaje("referencia", "Remisión a concepto inexistente")
            elif id_ in vistos:
                self.mensaje("id_repetido", f"Remisión duplicada: {id_}")
            else:
                vistos.add(id_)
            paginas = self.lista(r.get("paginas_cuaderno", []), "paginas_cuaderno")
            if any(type(p) is not int or p < 1 for p in paginas):
                self.mensaje("pagina", "Las páginas deben ser enteros positivos; bool no es una página")
            self.requerido(bool(paginas) and texto_no_vacio(r.get("zona_pizarra")), "remision", f"Remisión incompleta: {id_}")
        self.requerido(set(conceptos) <= vistos, "remision", "Hay conceptos sin remisiones")
        for id_ in usadas:
            if id_ not in fs:
                self.mensaje("referencia", f"Fuente inexistente: {id_}")
            else:
                self.requerido(fs[id_].get("estado") == "consultada", "fuente_pendiente", f"Fuente usada no consultada: {id_}")
                for campo in ("titulo", "autor_institucion", "tipo", "url_o_identificador", "consulta", "alcance_leido"):
                    self.requerido(texto_no_vacio(fs[id_].get(campo)), "fuente_evidencia", f"{id_}: falta {campo}")
                for campo in ("localizadores", "afirmaciones_respaldadas"):
                    datos = fs[id_].get(campo)
                    self.requerido(isinstance(datos, list) and bool(datos) and all(texto_no_vacio(x) for x in datos),
                                   "fuente_evidencia", f"{id_}: falta lista {campo} no vacía")
        return conceptos

    def validar_cobertura(self, cobertura, entradas, conceptos):
        entradas = self.objetos_id(entradas, "entradas")
        cubiertas = set()
        for punto in self.lista(cobertura, "cobertura"):
            if not isinstance(punto, dict):
                self.mensaje("cobertura", "Cada punto de cobertura debe ser un objeto")
                continue
            id_, estado = punto.get("entrada_id"), punto.get("estado")
            if not isinstance(id_, str) or id_ not in entradas:
                self.mensaje("cobertura_entrada", "Punto vinculado a entrada inexistente")
            else:
                cubiertas.add(id_)
            if not texto_no_vacio(punto.get("punto")) or estado not in ("incluido", "corregido", "pendiente", "fuera_de_alcance"):
                self.mensaje("cobertura", "Punto de cobertura sin descripción o estado válido")
            ids = self.lista(punto.get("conceptos", []), "cobertura.conceptos")
            if any(not isinstance(c, str) or c not in conceptos for c in ids):
                self.mensaje("referencia", "Cobertura remite a concepto inexistente")
            if estado in ("incluido", "corregido") and not ids:
                self.mensaje("cobertura", "Punto incluido/corregido sin concepto de destino")
            if estado in ("corregido", "fuera_de_alcance") and not texto_no_vacio(punto.get("motivo")):
                self.mensaje("cobertura", "Corrección/exclusión sin motivo")
            self.requerido(estado != "pendiente", "cobertura_pendiente", "Punto de cobertura pendiente")
        for id_, entrada in entradas.items():
            if entrada.get("relevante") is False and not texto_no_vacio(entrada.get("sin_contenido")):
                self.mensaje("cobertura", f"Entrada no relevante sin motivo: {id_}")
            self.requerido(id_ in cubiertas or texto_no_vacio(entrada.get("sin_contenido")),
                           "cobertura_ausente", f"Entrada sin cobertura ni justificación: {id_}")

    def resultado(self):
        return {"ok": not self.errores, "validacion": "estructural", "estado": self.estado,
                "paquete_doble_validado": not self.errores and self.estado == "revisado",
                "errores": self.errores, "avisos": self.avisos,
                "limites": "No acredita veracidad, lectura de fuentes, legibilidad, contenido real de PDF, ni publicación o importación."}


def texto_no_vacio(valor):
    return isinstance(valor, str) and bool(valor.strip())


def validar(carpeta):
    validador = Validador(carpeta)
    try:
        return validador.validar()
    except (TypeError, ValueError, OSError, RuntimeError, RecursionError) as exc:
        validador.mensaje("estructura_invalida", f"No se pudo interpretar la estructura: {exc}")
        return validador.resultado()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carpeta", help="Carpeta que contiene manifest.json")
    args = parser.parse_args()
    resultado = validar(args.carpeta)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
