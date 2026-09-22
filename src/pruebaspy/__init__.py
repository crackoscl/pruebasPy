import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

"""
Script de automatización temporal para DMC 1, 2, 3 y 4 Special Edition.
Descarga y ejecuta AutoHotkey v2 de forma efímera en la carpeta TEMP y se limpia al salir.
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


temp_dir = tempfile.mkdtemp(prefix="dmc_ahk_")
ahk_exe = os.path.join(temp_dir, "AutoHotkey64.exe")
script_path = os.path.join(temp_dir, "dmc_mapping.ahk")

print("[1/3] Preparando entorno temporal y descargando AutoHotkey v2...", flush=True)

ahk_url = "https://www.autohotkey.com/download/ahk-v2.zip"
installer_path = os.path.join(temp_dir, "ahk-v2.zip")

try:
    urllib.request.urlretrieve(ahk_url, installer_path)
    expected_hash = get_github_release_hash(os.path.basename(installer_path))

    if expected_hash:
        sha256_hash = hashlib.sha256()
        with open(installer_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)  # type: ignore

        calculated_hash = sha256_hash.hexdigest().lower()

        if calculated_hash != expected_hash:
            print("ERROR DE SEGURIDAD: El hash del archivo no coincide.", flush=True)
            print(f"Esperado: {expected_hash}", flush=True)
            print(f"Obtenido: {calculated_hash}", flush=True)
            input("Presiona Enter para salir...")
            sys.exit(1)
        print("¡Hash verificado correctamente!", flush=True)

    print("Extrayendo AutoHotkey de forma temporal...", flush=True)
    with zipfile.ZipFile(installer_path, "r") as zip_ref:
        zip_ref.extract("AutoHotkey64.exe", temp_dir)

except (urllib.error.URLError, OSError, subprocess.CalledProcessError) as e:
    print(f"Error durante la preparación temporal: {e}", flush=True)
    input("Presiona Enter para salir...")
    sys.exit(1)
finally:
    if os.path.exists(installer_path):
        try:
            os.remove(installer_path)
        except OSError:
            pass

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
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except OSError:
                pass
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except OSError:
                pass
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

print("¡Listo! Todo limpio y cerrado.", flush=True)
