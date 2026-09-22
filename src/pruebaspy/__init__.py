import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

"""
Script de automatización para crear un mapeo para DMC 1, 2, 3 y 4 Special Edition.
Diseñado para ejecutables de Nuitka mediante doble clic con manejo defensivo de errores y validación de hash.
"""


def get_github_release_hash(target_filename: str):
    url = "https://api.github.com/repos/AutoHotkey/AutoHotkey/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Python-Hash-Fetcher",
            "Accept": "application/vnd.github.v3+json",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            body = data.get("body", "")

            if target_filename:
                pattern = rf"(?:{re.escape(target_filename)}).*?([a-fA-F0-9]{{64}})"
                match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1)

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Error al conectar con la API de GitHub: {e}")
        return None


def get_ahk_path():
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    paths = [
        os.path.join(local_app_data, r"Programs\AutoHotkey\v2\AutoHotkey64.exe"),
        os.path.join(local_app_data, r"Programs\AutoHotkey\v2\AutoHotkey.exe"),
        os.path.join(local_app_data, r"Programs\AutoHotkey\AutoHotkey64.exe"),
        os.path.join(local_app_data, r"Programs\AutoHotkey\AutoHotkey.exe"),
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey64.exe",
        r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


if getattr(sys, "frozen", False):
    current_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

script_path = os.path.join(current_dir, "dmc_mapping.ahk")

print("[1/3] Verificando entorno y AutoHotkey v2...", flush=True)

ahk_exe = get_ahk_path()
if not ahk_exe:
    print(
        "[1/3] AutoHotkey no encontrado. Descargando e instalando v2.0.28...",
        flush=True,
    )
    ahk_url = "https://www.autohotkey.com/download/ahk-v2.exe"
    with urllib.request.urlopen(ahk_url) as response:
        final_url = response.geturl()
        content_disposition = response.headers.get("Content-Disposition")

        if content_disposition and "filename=" in content_disposition:
            file_name = content_disposition.split("filename=")[-1].strip("\"'")
        else:
            file_name = os.path.basename(final_url)

    installer_path = os.path.join(os.environ["TEMP"], file_name)
    expected_hash = get_github_release_hash(os.path.basename(installer_path))

    try:
        urllib.request.urlretrieve(ahk_url, installer_path)

        sha256_hash = hashlib.sha256()
        with open(installer_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)  # type: ignore

        calculated_hash = sha256_hash.hexdigest().lower()

        if calculated_hash != expected_hash:
            print("ERROR DE SEGURIDAD: El hash del instalador no coincide.", flush=True)
            print(f"Esperado: {expected_hash}", flush=True)
            print(f"Obtenido: {calculated_hash}", flush=True)
            input("Presiona Enter para salir...")
            sys.exit(1)

        print("¡Hash verificado correctamente! Instalando AutoHotkey...", flush=True)
        subprocess.run([installer_path, "/silent"], check=True)
        print("¡AutoHotkey instalado con éxito!", flush=True)
        ahk_exe = get_ahk_path()

    except (urllib.error.URLError, OSError, subprocess.CalledProcessError) as e:
        print(f"Error durante la instalación: {e}", flush=True)
        input("Presiona Enter para salir...")
        sys.exit(1)
    finally:
        if os.path.exists(installer_path):
            try:
                os.remove(installer_path)
            except OSError:
                pass
else:
    print(f"[1/3] AutoHotkey detectado correctamente en: {ahk_exe}", flush=True)


ahk_code = """#Requires AutoHotkey v2.0
#SingleInstance Force

A_HotkeyInterval := 0
A_MaxHotkeysPerInterval := 99999

; Revisa cada 2 segundos si alguno de los cuatro juegos sigue abierto
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
LButton::I      ;[LMB] Melee/Y
RButton::J      ;[RMB] Shoot/X
MButton::L      ;[MMB] Shoot/B
Space::K        ;[Space] Jump/A
XButton1::Q     ;[Mouse Button 4] Map/LT
XButton2::E     ;[Mouse Button 5] Taunt/RT
LShift::Space   ;[Left Shift] Lock-on/RB
T::RShift       ;[T] Pause Menu/Back
Esc::M          ;[Esc] Menu Screen/Start
Pause::Suspend  ;[Pause] Suspend Script
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 2 HD
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe dmc2.exe")
LButton::I      ;[LMB] Melee/Y
RButton::J      ;[RMB] Shoot/X
MButton::L      ;[MMB] Evade/B
Space::K        ;[Space] Jump/A
XButton1::Q     ;[Mouse Button 4] Change Guns/LT
XButton2::E     ;[Mouse Button 5] Disengage Lock-on/RT
LShift::Space   ;[Left Shift] Lock-on/RB
T::RShift       ;[T] Pause Menu/Back
Esc::M          ;[Esc] Menu Screen/Start
Pause::Suspend  ;[Pause] Suspend Script
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 3 Special Edition HD
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe dmc3.exe")
LButton::I      ;[LMB] Melee/Y
RButton::J      ;[RMB] Shoot/X
MButton::L      ;[MMB/Scroll Button] Style Action/B
Space::K        ;[Space] Jump/A
XButton1::Q     ;[Mouse Button 4] Change Guns/LT
XButton2::E     ;[Mouse Button 5] Change Devil Arms/RT
LShift::Space   ;[Left Shift] Lock-on/RB
T::RShift       ;[T] Taunt/Back
Esc::M          ;[Esc] Pause/Start
z::Left         ;[Z] Rotate Camera Left
x::Right        ;[X] Rotate Camera Right
Pause::Suspend  ;[Pause] Suspend Script
#HotIf

; -----------------------------------------------------------------
; Devil May Cry 4 Special Edition
; -----------------------------------------------------------------
#HotIf WinActive("ahk_exe DevilMayCry4SpecialEdition.exe")
LButton::I      ;[LMB] Melee/Y
RButton::J      ;[RMB] Shoot/X
MButton::L      ;[MMB] Style Action/B
Space::K        ;[Space] Jump/A
XButton1::Q     ;[Mouse Button 4] Change Guns/LT
XButton2::E     ;[Mouse Button 5] Change Devil Arms/RT
LShift::Space   ;[Left Shift] Lock-on/RB
C::O            ;[C] Change Target
F::P            ;[F] Reset Camera
Pause::Suspend  ;Suspend Script
#HotIf
"""

print("[2/3] Creando archivo de configuración local...", flush=True)
try:
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ahk_code)
    print(f"-> Archivo generado correctamente en: {script_path}", flush=True)
except OSError as e:
    print(
        f"ERROR CRITICO: No se pudo escribir el archivo. Revisa permisos de la"
        f" carpeta: {e}",
        flush=True,
    )
    input("Presiona Enter para salir...")
    sys.exit(1)

print("[3/3] Iniciando el emulador de teclas global...", flush=True)
try:
    if ahk_exe and os.path.exists(ahk_exe):
        subprocess.Popen([ahk_exe, script_path])
    else:
        raise FileNotFoundError(
            "No se encontró el ejecutable de AutoHotkey v2 en las rutas estándar."
        )

    print("\n--------------------------------------------------", flush=True)
    print("¡LISTO!", flush=True)
    print("- Mapeo configurado y ejecutándose.", flush=True)
    print("- Se cerrará automáticamente al salir de los juegos.", flush=True)
    print("--------------------------------------------------", flush=True)
except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
    print(f"No se pudo iniciar el archivo: {e}", flush=True)
    input("Presiona Enter para salir...")
    sys.exit(1)

print("\nPuedes cerrar esta ventana de consola cuando desees.", flush=True)
input("Presiona Enter para cerrar esta ventana...")
