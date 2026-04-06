import win32api
import win32con
import win32gui
import time
import pyautogui
import sys

# --- COORDINATE SETTINGS ---
RIGHT_CLICK_1 = (851, 388)   # Right Click
RIGHT_CLICK_2 = (1884, 355)  # Right Click
LEFT_CLICK_3 = (1320, 820)   # Left Click

WINDOW_TITLE = "RubinOT"

def make_lparam(x, y):
    """Encode (x, y) into lParam for PostMessage click events."""
    return (x & 0xFFFF) | ((y & 0xFFFF) << 16)

def find_game_window():
    """Find the RubinOT window by title."""
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        print("Make sure RubinOT is running.")
        sys.exit(1)
    print(f"Found window '{WINDOW_TITLE}' (handle: {hwnd})")
    return hwnd

def screen_to_client(hwnd, x, y):
    """Convert screen coordinates to client-relative coordinates."""
    return win32gui.ScreenToClient(hwnd, (x, y))

def right_click(x, y, hwnd):
    try:
        cx, cy = screen_to_client(hwnd, x, y)
        lParam = make_lparam(cx, cy)
        pyautogui.moveTo(x, y, duration=0.2)
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.1)
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
        print(f"-> Right click at ({x}, {y}) [client: ({cx}, {cy})]")
    except Exception as e:
        print(f"ERROR: Right click failed at ({x}, {y}): {e}")

def left_click(x, y, hwnd):
    try:
        cx, cy = screen_to_client(hwnd, x, y)
        lParam = make_lparam(cx, cy)
        pyautogui.moveTo(x, y, duration=0.2)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.1)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        print(f"-> Left click at ({x}, {y}) [client: ({cx}, {cy})]")
    except Exception as e:
        print(f"ERROR: Left click failed at ({x}, {y}): {e}")

def execute_sequence(hwnd):
    right_click(*RIGHT_CLICK_1, hwnd)
    time.sleep(1.0)

    right_click(*RIGHT_CLICK_2, hwnd)
    time.sleep(1.0)

    left_click(*LEFT_CLICK_3, hwnd)
    time.sleep(1.0)

def start():
    print("Click Bot started.")
    hwnd = find_game_window()

    print("Starting sequence in 3 seconds...")
    time.sleep(3)

    execute_sequence(hwnd)
    print("\nSequence finished.")

if __name__ == "__main__":
    start()
