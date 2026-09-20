import os
import subprocess
import sys
import urllib.error
import urllib.request

"""
Script de automatización para crear un mapeo para DMC 1, 2, 3 y 4 Special Edition.
Verifica e instala AutoHotkey v2 automáticamente si no está presente.
"""


def get_ahk_path():
    # Posibles rutas donde AutoHotkey v2 suele instalarse
    paths = [
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


# Usar la carpeta actual del script para guardar el archivo de configuración localmente
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "dmc_mapping.ahk")

# 1. Evaluar si AutoHotkey está instalado; si no, descargarlo e instalarlo
ahk_exe = get_ahk_path()
if not ahk_exe:
    print("[1/3] AutoHotkey no encontrado. Descargando e instalando v2...")
    ahk_url = "https://www.autohotkey.com/download/ahk-v2.exe"
    installer_path = os.path.join(os.environ["TEMP"], "ahk_install.exe")
    try:
        urllib.request.urlretrieve(ahk_url, installer_path)
        subprocess.run([installer_path, "/silent"], check=True)
        print("¡AutoHotkey instalado con éxito!")
        ahk_exe = get_ahk_path()  # Volver a buscar la ruta tras la instalación
    except (urllib.error.URLError, OSError, subprocess.CalledProcessError) as e:
        print(f"Error durante la instalación: {e}")
        sys.exit(1)
else:
    print("[1/3] AutoHotkey ya está instalado.")

# 2. Código AHK completo incluyendo DMC 4 y su auto-cierre
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

print("[2/3] Creando archivo de configuración local...")
with open(script_path, "w", encoding="utf-8") as f:
    f.write(ahk_code)

# 3. Ejecutar el archivo .ahk utilizando explícitamente el ejecutable de AHK
print("[3/3] Iniciando el emulador de teclas global...")
try:
    if ahk_exe and os.path.exists(ahk_exe):
        subprocess.Popen([ahk_exe, script_path])
    else:
        subprocess.Popen(["cmd", "/c", script_path], shell=True)

    print("\n--------------------------------------------------")
    print("¡LISTO!")
    print("- Mapeo configurado y ejecutándose.")
    print("- Se cerrará automáticamente al salir de los juegos.")
    print("--------------------------------------------------")
except (OSError, subprocess.SubprocessError) as e:
    print(f"No se pudo iniciar el archivo: {e}")
    sys.exit(1)
