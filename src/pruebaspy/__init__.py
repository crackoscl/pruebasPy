import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

"""
Script de automatización temporal para DMC 1, 2, 3 y 4 Special Edition.
Descarga y ejecuta AutoHotkey v2 de forma efímera en la carpeta TEMP y se limpia al salir.
"""


def url_open_safe(req: urllib.request.Request):
    context = ssl.create_default_context()
    try:
        return urllib.request.urlopen(req, context=context)
    except urllib.error.URLError, ssl.SSLError:
        unverified_context = ssl._create_unverified_context()  # type: ignore
        return urllib.request.urlopen(req, context=unverified_context)


def get_latest_github_release_info():
    """Consulta la API de GitHub y busca el hash específicamente vinculado al archivo .zip."""
    url = "https://api.github.com/repos/AutoHotkey/AutoHotkey/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Python-Hash-Fetcher",
            "Accept": "application/vnd.github.v3+json",
        },
    )

    try:
        with url_open_safe(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        body = data.get("body", "")
        assets = data.get("assets", [])

        target_filename = None
        download_url = None

        # 1. Buscamos el asset oficial que termine en .zip
        for asset in assets:
            name = asset.get("name", "")
            if name.endswith(".zip"):
                target_filename = name
                download_url = asset.get("browser_download_url")
                break

        if not target_filename or not download_url:
            return None, None, None

        expected_hash = None

        # 2. Búsqueda dirigida: Analizamos línea por línea para encontrar el hash exacto del .zip
        lines = body.splitlines()
        for i, line in enumerate(lines):
            if target_filename in line:
                line_hashes = re.findall(r"\b([a-fA-F0-9]{64})\b", line)
                if line_hashes:
                    expected_hash = line_hashes[0]
                    break

                for j in range(max(0, i - 2), min(len(lines), i + 3)):
                    nearby_hashes = re.findall(r"\b([a-fA-F0-9]{64})\b", lines[j])
                    if nearby_hashes:
                        expected_hash = nearby_hashes[0]
                        break
                if expected_hash:
                    break

        return target_filename, download_url, expected_hash

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Error al conectar con la API de GitHub: {e}")
        return None, None, None


temp_dir = tempfile.mkdtemp(prefix="dmc_ahk_")
ahk_exe = os.path.join(temp_dir, "AutoHotkey64.exe")
script_path = os.path.join(temp_dir, "dmc_mapping.ahk")

print(
    "[1/3] Consultando la última versión en GitHub y preparando entorno...", flush=True
)

real_filename, download_url, expected_hash = get_latest_github_release_info()

if not real_filename or not download_url:
    print(
        "ERROR: No se pudo obtener la información de descarga desde GitHub.", flush=True
    )
    input("Presiona Enter para salir...")
    sys.exit(1)

print(f"Archivo ZIP detectado en GitHub: {real_filename}", flush=True)
installer_path = os.path.join(temp_dir, real_filename)

try:
    req_ahk = urllib.request.Request(
        download_url,
        headers={
            "User-Agent": "Python-Downloader",
            "Accept": "application/octet-stream",
        },
    )

    # Uso de la función auxiliar centralizada para la descarga
    with url_open_safe(req_ahk) as response, open(installer_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    print("Archivo descargado correctamente desde GitHub.", flush=True)

    # Validación de Hash
    if expected_hash:
        print(f"Hash oficial del ZIP encontrado: {expected_hash}")
        sha256_hash = hashlib.sha256()
        with open(installer_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)  # type: ignore

        calculated_hash = sha256_hash.hexdigest().lower()

        if calculated_hash != expected_hash.lower():
            print("ERROR DE SEGURIDAD: El hash del archivo no coincide.", flush=True)
            print(f"Esperado: {expected_hash}", flush=True)
            print(f"Obtenido: {calculated_hash}", flush=True)
            input("Presiona Enter para salir...")
            sys.exit(1)
        print("¡Hash verificado correctamente!", flush=True)
    else:
        print(
            "AVISO: No se encontró el hash en la release de GitHub. Continuando extracción...",
            flush=True,
        )

    print("Extrayendo AutoHotkey de forma temporal...", flush=True)
    with zipfile.ZipFile(installer_path, "r") as zip_ref:
        zip_ref.extract("AutoHotkey64.exe", temp_dir)

except (urllib.error.URLError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as e:
    print(f"Error durante la preparación temporal: {e}", flush=True)
    input("Presiona Enter para salir...")
    sys.exit(1)
finally:
    if "installer_path" in locals() and os.path.exists(installer_path):
        try:
            os.remove(installer_path)
        except OSError:
            pass

ahk_code = """#Requires AutoHotkey v2.0
#SingleInstance Force

A_HotkeyInterval := 0
A_MaxHotkeysPerInterval := 99999

SetTimer(CheckGameClosed, 2000)

CheckGameClosed() {
    if !ProcessExist("dmc1.exe") && !ProcessExist("dmc2.exe") && !ProcessExist("dmc3.exe") && !ProcessExist("DevilMayCry4SpecialEdition.exe") {
        ExitApp()
    }
}

; -----------------------------------------------------------------
; Devil May Cry 1 HD
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe dmc1.exe")
LButton::I
RButton::J
MButton::L
Space::K
XButton1::Q
XButton2::E
LShift::Space
T::RShift
Esc::M
Pause::Suspend
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 2 HD
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe dmc2.exe")
LButton::I
RButton::J
MButton::L
Space::K
XButton1::Q
XButton2::E
LShift::Space
T::RShift
Esc::M
Pause::Suspend
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 3 Special Edition HD
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe dmc3.exe")
LButton::I
RButton::J
MButton::L
Space::K
XButton1::Q
XButton2::E
LShift::Space
T::RShift
Esc::M
z::Left
x::Right
Pause::Suspend
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 4 Special Edition
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe DevilMayCry4SpecialEdition.exe")
LButton::I
RButton::J
MButton::L
Space::K
XButton1::Q
XButton2::E
LShift::Space
C::O
F::P
Pause::Suspend
#HotIf
"""

print("[2/3] Creando script de mapeo temporal...", flush=True)
try:
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ahk_code)
except OSError as e:
    print(f"ERROR CRITICO: No se pudo escribir el archivo temporal: {e}", flush=True)
    input("Presiona Enter para salir...")
    sys.exit(1)

print("[3/3] Iniciando el mapeador y esperando a que cierres los juegos...", flush=True)
try:
    if os.path.exists(ahk_exe):
        process = subprocess.Popen([ahk_exe, script_path])
        process.wait()
    else:
        raise FileNotFoundError("No se pudo extraer el ejecutable de AutoHotkey.")

    print("\n--------------------------------------------------", flush=True)
    print("¡Juegos cerrados! El mapeador ha finalizado.", flush=True)
    print("--------------------------------------------------", flush=True)

except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
    print(f"Ocurrió un error durante la ejecución: {e}", flush=True)

finally:
    print("Limpiando archivos temporales...", flush=True)
    shutil.rmtree(temp_dir, ignore_errors=True)

print("¡Listo! Todo limpio y cerrado.", flush=True)
time.sleep(2)
sys.exit(0)
