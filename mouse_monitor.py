import pyautogui
import time

def monitor_mouse():
    print("=" * 40)
    print("   MOUSE COORDINATE MONITOR")
    print("=" * 40)
    print("Press CTRL + C in the terminal to stop.")
    print("-" * 40)

    try:
        while True:
            x, y = pyautogui.position()

            try:
                color = pyautogui.pixel(x, y)
                color_str = str(color)
            except Exception:
                color_str = "N/A"

            print(f"X: {x:<5} Y: {y:<5} | Color (RGB): {color_str}", end="\r")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nMonitoring finished.")

if __name__ == "__main__":
    monitor_mouse()
