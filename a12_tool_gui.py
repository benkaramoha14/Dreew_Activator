import PySimpleGUI as sg
import subprocess
import sys
import os
import threading
import time

# ---------- Rutas ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SCRIPT = os.path.join(BASE_DIR, "client", "activator.py")
LOGO_PATH = os.path.join(BASE_DIR, "logo.jpg")
ICON_START = os.path.join(BASE_DIR, "icon_start.png")
ICON_EXIT = os.path.join(BASE_DIR, "icon_exit.png")

# ---------- Tema y fuentes ----------
sg.theme('DarkGrey5')
FONT_MAIN = ("Helvetica", 22, "bold")
FONT_LOG = ("Consolas", 11)

# ---------- Funciones ----------

def detect_iphone():
    """Detecta iPhone conectado usando ideviceinfo"""
    try:
        result = subprocess.run(
            ["ideviceinfo"], capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("ProductType:"):
                    model = line.split(":")[1].strip()
                    return f"📱 iPhone detectado: {model}"
        return None
    except Exception:
        return None

def colorize_log(line):
    """Colores según tipo de mensaje"""
    line = line.strip()
    if "error" in line.lower() or "fail" in line.lower():
        return f"\x1b[31m{line}\x1b[0m"
    elif "done" in line.lower() or "success" in line.lower():
        return f"\x1b[32m{line}\x1b[0m"
    elif "warn" in line.lower():
        return f"\x1b[33m{line}\x1b[0m"
    else:
        return line

def animate_logo_glow(window):
    """Efecto glow dinámico en logo"""
    brightness = 0
    direction = 1
    while True:
        color_value = 100 + int(155 * abs(brightness/255))
        window["Logo"].update(background_color=f"#{color_value:02x}{color_value:02x}{255:02x}")
        brightness += 10 * direction
        if brightness >= 255 or brightness <= 0:
            direction *= -1
        time.sleep(0.05)

def smooth_progress(window, key='Progress'):
    """Barra de progreso tipo loading real"""
    progress = 0
    while progress < 100:
        progress += 1
        window[key].update(progress, bar_color=(f"#00FFFF", "#1E1E1E"))
        time.sleep(0.02)

def start_unlock(window):
    """Ejecuta desbloqueo y actualiza barra/logs"""
    window["Start"].update(disabled=True)
    window["Status"].update("🚀 Iniciando DREW Activator...")
    window["Progress"].update(0)

    try:
        python_cmd = "python3" if sys.platform != "win32" else "python"
        process = subprocess.Popen([python_cmd, CLIENT_SCRIPT],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)

        stages = [
            "Conexión establecida",
            "Verificando dispositivo",
            "Preparando entorno",
            "Desbloqueo en curso",
            "Activación",
            "Finalizando proceso"
        ]
        stage_index = 0
        total_stages = len(stages)

        # Hilo barra de progreso tipo app
        threading.Thread(target=smooth_progress, args=(window,), daemon=True).start()

        for line in process.stdout:
            colored_line = colorize_log(line)
            window["Log"].print(colored_line)

            # Avanza las etapas
            if stage_index < total_stages and stages[stage_index].lower() in line.lower():
                stage_index += 1

        process.wait()
        window["Status"].update("✅ DREW Activator completado")
        sg.popup_notify("¡Proceso terminado!", title="DREW Activator", display_duration_in_ms=3000)

    except Exception as e:
        window["Status"].update(f"❌ Error: {e}")
    finally:
        window["Start"].update(disabled=False)
        window["Progress"].update(0)

# ---------- Layout PRO ----------
layout = [
    [sg.Image(LOGO_PATH, size=(250,250), key="Logo", pad=(0,10), justification="center")],
    [sg.Text("DREW Activator", font=FONT_MAIN, text_color="#00FFFF", justification="center")],
    [sg.Frame("Estado del dispositivo",
              [[sg.Text("Esperando iPhone...", key="Status", size=(45,1), text_color="#FFFFFF")]],
              relief=sg.RELIEF_SUNKEN, border_width=2, pad=(10,10))],
    [sg.Frame("Logs de proceso",
              [[sg.Output(size=(90, 15), key="Log", background_color="#1E1E1E", text_color="#FFFFFF", font=FONT_LOG)]],
              relief=sg.RELIEF_SUNKEN, border_width=2, pad=(10,10))],
    [sg.ProgressBar(100, orientation='h', size=(55, 20), key='Progress', bar_color=("#00FFFF","#1E1E1E"))],
    [sg.Button("Start Unlock", key="Start", image_filename=ICON_START, image_subsample=2,
               button_color=("white","#007ACC"), font=("Helvetica",12,"bold")),
     sg.Button("Exit", key="Exit", image_filename=ICON_EXIT, image_subsample=2,
               button_color=("white","#FF5555"), font=("Helvetica",12,"bold"))],
    [sg.Text("by Ibdi14", font=("Helvetica", 9, "italic"), text_color="#AAAAAA", justification="right", pad=(0,10))]
]

window = sg.Window("DREW Activator PRO", layout, finalize=True, resizable=True)

# ---------- Hilo para detección de iPhone ----------
def iphone_detector():
    while True:
        detected = detect_iphone()
        if detected:
            window["Status"].update(detected)
        time.sleep(2)

threading.Thread(target=iphone_detector, daemon=True).start()
threading.Thread(target=animate_logo_glow, args=(window,), daemon=True).start()

# ---------- Event loop ----------
while True:
    event, values = window.read(timeout=100)
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    if event == "Start":
        threading.Thread(target=start_unlock, args=(window,), daemon=True).start()

window.close()
