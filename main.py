import customtkinter as ctk
import pyautogui
import winsound
import time
import threading
import os
import sys
import json
import pystray
from PIL import Image
from threading import Thread
import requests
import tempfile
import shutil

# =========================
# App info
# =========================
APP_VERSION = "1.0"
UPDATE_URL = "https://raw.githubusercontent.com/<username>/CaptchaDetectorPro/main/latest_version.json"  # change <username>

# =========================
# Resource path
# =========================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CAPTCHA_IMAGE = resource_path("assets/captcha_template.png")
SUCCESS_IMAGE = resource_path("assets/success_template.png")
SETTINGS_FILE = resource_path("settings.json")
ICON_FILE = resource_path("assets/icon.ico")

# =========================
# Load / Save Settings
# =========================
def load_settings():
    default = {"confidence": "0.7", "cooldown": "120", "sound": True}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                default.update(data)
        except:
            pass
    return default

def save_settings():
    data = {"confidence": confidence.get(), "cooldown": cooldown.get(), "sound": sound.get()}
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

# =========================
# Globals
# =========================
running = False
captcha_active = False
cooldown_until = 0
beep_event = threading.Event()

# =========================
# Beep Thread
# =========================
def beep_loop():
    while True:
        beep_event.wait()
        while beep_event.is_set():
            try:
                winsound.Beep(1200, 200)
            except:
                pass
            time.sleep(0.2)

Thread(target=beep_loop, daemon=True).start()

# =========================
# Detection loop
# =========================
def detection_loop():
    global running, captcha_active, cooldown_until
    while running:
        now = time.time()

        if now < cooldown_until:
            beep_event.clear()
            set_status("Cooldown...", "orange")
            time.sleep(1)
            continue

        region = None
        try:
            location = pyautogui.locateOnScreen(CAPTCHA_IMAGE, confidence=float(confidence.get()), region=region)
        except:
            location = None

        try:
            success = pyautogui.locateOnScreen(SUCCESS_IMAGE, confidence=float(confidence.get()), region=region)
        except:
            success = None

        if location and not captcha_active:
            captcha_active = True
            log("Captcha detected")
            set_status("Captcha Detected", "red")
            if sound.get():
                beep_event.set()

        if success:
            captcha_active = False
            beep_event.clear()
            cooldown_until = time.time() + int(cooldown.get())
            set_status("Success", "green")
            log("Success detected")

        if not location and captcha_active:
            captcha_active = False
            beep_event.clear()
            cooldown_until = time.time() + int(cooldown.get())
            log("Captcha cleared")

        time.sleep(0.4)

# =========================
# Controls
# =========================
def start():
    global running
    if not running:
        running = True
        Thread(target=detection_loop, daemon=True).start()
        set_status("Running", "blue")

def stop():
    global running
    running = False
    beep_event.clear()
    set_status("Stopped", "gray")
    save_settings()

# =========================
# UI Helpers
# =========================
def log(msg):
    log_box.insert("end", msg + "\n")
    log_box.see("end")

def set_status(text, color):
    status_label.configure(text=text, text_color=color)

# =========================
# Update System
# =========================
def check_update():
    try:
        resp = requests.get(UPDATE_URL, timeout=5).json()
        latest_version = resp.get("version", APP_VERSION)
        download_url = resp.get("url", None)

        if latest_version != APP_VERSION and download_url:
            log(f"Update available: {latest_version}")
            update_button.configure(state="normal")
            return download_url
        else:
            log("App is up to date")
            update_button.configure(state="disabled")
            return None
    except Exception as e:
        log(f"Failed to check updates: {e}")
        update_button.configure(state="disabled")
        return None

def run_update():
    url = check_update()
    if not url:
        return

    log("Downloading update...")
    try:
        r = requests.get(url, stream=True)
        temp_file = os.path.join(tempfile.gettempdir(), "CaptchaDetectorPro_Setup.exe")
        with open(temp_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        log("Running installer...")
        os.startfile(temp_file)
        stop()
        app.quit()
    except Exception as e:
        log(f"Failed to update: {e}")

# =========================
# Main Window
# =========================
app = ctk.CTk()
app.geometry("600x520")
app.title("Captcha Detector PRO")

# Load settings after root is created
settings_data = load_settings()
confidence = ctk.StringVar(app, value=settings_data["confidence"])
cooldown = ctk.StringVar(app, value=settings_data["cooldown"])
sound = ctk.BooleanVar(app, value=settings_data["sound"])

# Header
header = ctk.CTkLabel(app, text="Captcha Detector PRO", font=("Segoe UI", 20, "bold"))
header.pack(pady=10)

# Status
status_label = ctk.CTkLabel(app, text="Stopped", font=("Segoe UI", 14))
status_label.pack(pady=5)

# Buttons
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="Start", command=start, width=120).grid(row=0, column=0, padx=10)
ctk.CTkButton(btn_frame, text="Stop", command=stop, width=120).grid(row=0, column=1, padx=10)
update_button = ctk.CTkButton(btn_frame, text="Update", command=run_update, width=120, state="disabled")
update_button.grid(row=0, column=2, padx=10)

# Settings
settings_frame = ctk.CTkFrame(app)
settings_frame.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(settings_frame, text="Confidence").grid(row=0, column=0, padx=10, pady=5)
ctk.CTkEntry(settings_frame, textvariable=confidence, width=60).grid(row=0, column=1)

ctk.CTkLabel(settings_frame, text="Cooldown").grid(row=1, column=0, padx=10, pady=5)
ctk.CTkEntry(settings_frame, textvariable=cooldown, width=60).grid(row=1, column=1)

ctk.CTkCheckBox(settings_frame, text="Sound Alerts", variable=sound).grid(row=2, column=0, columnspan=2, pady=5)

# Log box
log_box = ctk.CTkTextbox(app, height=200)
log_box.pack(fill="both", expand=True, padx=20, pady=10)

footer = ctk.CTkLabel(app, text="v1.0 | Built by HabboLens", font=("Segoe UI", 10))
footer.pack(pady=5)

# =========================
# System tray
# =========================
icon_image = Image.open(ICON_FILE) if os.path.exists(ICON_FILE) else Image.new('RGB', (64,64))

def quit_tray(icon, item):
    stop()
    icon.stop()
    app.quit()

def show_window(icon, item):
    app.after(0, app.deiconify)

def on_closing():
    app.withdraw()
    tray_icon = pystray.Icon("CaptchaDetector", icon_image, "Captcha Detector PRO", menu=pystray.Menu(
        pystray.MenuItem("Open App", show_window),
        pystray.MenuItem("Quit", quit_tray)
    ))
    Thread(target=tray_icon.run, daemon=True).start()
    save_settings()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Check update on startup
app.after(1000, check_update)

# Start GUI
app.mainloop()