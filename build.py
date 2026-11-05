#!/usr/bin/env python3
"""Empaqueta el plugin de Moodle en dist/ listo para instalar desde
Administración del sitio > Extensiones > Instalar extensiones.

Uso:
    python build.py                     # genera el ZIP con la versión actual
    python build.py --bump              # incrementa $plugin->version (YYYYMMDDXX)
    python build.py --release 1.0.2     # cambia $plugin->release
    python build.py --bump --release 1.0.2
"""
import argparse
import datetime
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "moodle_servicio"
DIST = ROOT / "dist"
VERSION_FILE = SRC / "version.php"
# version.php está en ISO-8859-1; se lee/escribe igual para no alterar bytes.
ENCODING = "latin-1"

EXCLUDE_NAMES = {".git", ".gitignore", ".DS_Store", "Thumbs.db", "__pycache__", "node_modules"}

RE_COMPONENT = re.compile(r"\$plugin->component\s*=\s*'([^']+)'")
RE_VERSION = re.compile(r"(\$plugin->version\s*=\s*)(\d{10})")
RE_RELEASE = re.compile(r"(\$plugin->release\s*=\s*')([^']*)(')")


def read_meta(text):
    comp = RE_COMPONENT.search(text)
    ver = RE_VERSION.search(text)
    rel = RE_RELEASE.search(text)
    if not (comp and ver):
        sys.exit("ERROR: version.php debe definir $plugin->component y $plugin->version")
    return comp.group(1), ver.group(2), rel.group(2) if rel else ""


def next_version(current):
    today = datetime.date.today().strftime("%Y%m%d")
    if current[:8] >= today:
        # Mismo día (o fecha futura): incrementa el contador XX.
        return str(int(current) + 1)
    return today + "00"


def update_version_file(bump, release):
    text = VERSION_FILE.read_text(encoding=ENCODING)
    _, version, _ = read_meta(text)
    if bump:
        new = next_version(version)
        text = RE_VERSION.sub(lambda m: m.group(1) + new, text, count=1)
        print(f"version: {version} -> {new}")
    if release:
        if not RE_RELEASE.search(text):
            sys.exit("ERROR: version.php no define $plugin->release")
        text = RE_RELEASE.sub(lambda m: m.group(1) + release + m.group(3), text, count=1)
        print(f"release: -> {release}")
    with open(VERSION_FILE, "w", encoding=ENCODING, newline="") as f:
        f.write(text)


def validate(component):
    plugintype, name = component.split("_", 1)
    required = [SRC / "version.php", SRC / "lang" / "en" / f"{component}.php"]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        sys.exit("ERROR: faltan archivos requeridos por Moodle: " + ", ".join(missing))
    return plugintype, name


def build():
    component, version, release = read_meta(VERSION_FILE.read_text(encoding=ENCODING))
    plugintype, name = validate(component)

    # Un ZIP por release (p.ej. 1.0.2) en dist/; los de otros releases se
    # conservan. Solo se reemplaza el ZIP del MISMO release.
    if not release:
        sys.exit("ERROR: version.php debe definir $plugin->release (p.ej. '1.0.1')")
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / f"{component}_{release}.zip"
    if zip_path.exists():
        print(f"Aviso: ya existia {zip_path.name}, se reemplaza (usa --release para crear uno nuevo).")
        zip_path.unlink()

    def excluded(path):
        rel = path.relative_to(SRC)
        return any(part in EXCLUDE_NAMES for part in rel.parts) or path.suffix == ".pyc"

    # Moodle exige que la carpeta raíz del ZIP sea el nombre del plugin.
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SRC.rglob("*")):
            if excluded(path):
                continue
            arcname = f"{name}/{path.relative_to(SRC).as_posix()}"
            if path.is_dir():
                zf.writestr(arcname + "/", "")
            else:
                zf.write(path, arcname)

    print(f"Plugin:  {component} (tipo '{plugintype}', carpeta '{name}')")
    print(f"Version: {version}  release: {release}")
    print(f"ZIP:     {zip_path.relative_to(ROOT)}  -> subir en Administracion > Extensiones > Instalar extensiones")


def main():
    ap = argparse.ArgumentParser(description="Empaqueta el plugin de Moodle en dist/")
    ap.add_argument("--bump", action="store_true", help="incrementa $plugin->version (YYYYMMDDXX)")
    ap.add_argument("--release", help="establece $plugin->release, p.ej. 1.0.2")
    args = ap.parse_args()
    if args.bump or args.release:
        update_version_file(args.bump, args.release)
    build()


if __name__ == "__main__":
    main()
