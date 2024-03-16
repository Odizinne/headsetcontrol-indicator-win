import os
import pystray
import subprocess
import time
import threading
import winreg
from PIL import Image

current_directory = os.path.dirname(os.path.abspath(__file__))
headsetcontrol_path = os.path.join(current_directory, "headsetcontrol.exe")

def execute_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e.stderr}")
        return ""

def extract_battery_level(output):
    battery_index = output.find("Battery:")
    charging_index = output.find("Charging")
    unavailable_index = output.find("Unavailable")
    
    if battery_index != -1:
        percentage_index = battery_index + len("Battery: ")
        percentage_end_index = output.find('%', percentage_index)
        percentage = output[percentage_index:percentage_end_index].strip()
        
        if charging_index != -1:
            return "Charging"
        elif unavailable_index != -1:
            return "Unavailable"
        else:
            return int(percentage)
    return 0

def update_battery_icon(tray_icon):
    battery_status_output = execute_command([headsetcontrol_path, "-b"])
    battery_level_index = battery_status_output.find("Battery:")
    charging_index = battery_status_output.find("Charging")
    unavailable_index = battery_status_output.find("Unavailable")
    dark_mode = is_dark_mode()

    if battery_level_index != -1:
        battery_level = extract_battery_level(battery_status_output)

        icon = None

        if charging_index != -1:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_charging.png" if not dark_mode else "battery_charging_light.png"))
        elif battery_level == "Unavailable":
            icon = Image.open(os.path.join(current_directory, "icons", "battery_nondetected.png" if not dark_mode else "battery_nondetected_light.png"))
        elif int(battery_level) > 100:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_100.png" if not dark_mode else "battery_100_light.png"))
        elif int(battery_level) > 75:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_75.png" if not dark_mode else "battery_75_light.png"))
        elif int(battery_level) > 50:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_50.png" if not dark_mode else "battery_50_light.png"))
        elif int(battery_level) > 25:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_25.png" if not dark_mode else "battery_25_light.png"))
        else:
            icon = Image.open(os.path.join(current_directory, "icons", "battery_nondetected.png" if not dark_mode else "battery_nondetected_light.png"))
        
        tray_icon.icon = icon

def is_dark_mode():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
        return value == 0
    except Exception as e:
        print(f"Error detecting Windows mode: {e}")
        return False

def exit_action(icon, item):
    icon.stop()

def tray_thread(tray_icon):
    while True:
        update_battery_icon(tray_icon)
        time.sleep(5)

def main():
    dark_mode = is_dark_mode()
    initial_icon = "battery_nondetected.png" if not dark_mode else "battery_nondetected_light.png"
    icon = Image.open(os.path.join(current_directory, "icons", initial_icon))

    tray_icon = pystray.Icon("battery_icon", icon, "Battery Status")
    menu = pystray.Menu(pystray.MenuItem("Exit", exit_action))
    tray_icon.menu = menu

    update_thread = threading.Thread(target=tray_thread, args=(tray_icon,))
    update_thread.daemon = True
    update_thread.start()

    tray_icon.run()

if __name__ == "__main__":
    main()
