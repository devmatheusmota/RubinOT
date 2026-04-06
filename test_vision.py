import os
import time
import ssl
import sys
import easyocr
import cv2
import numpy as np
import ctypes
import win32gui
import traceback

# Ignore SSL errors
ssl._create_default_https_context = ssl._create_unverified_context

WINDOW_TITLE = "RubinOT"

def find_game_window():
    """Find the RubinOT window and return its handle and client rect."""
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        print("Make sure RubinOT is running.")
        sys.exit(1)

    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
    width = right - left
    height = bottom - top

    print(f"Found window '{WINDOW_TITLE}' at ({left}, {top}) size {width}x{height}")
    return hwnd, left, top, width, height

def capture_window(x, y, width, height):
    """Capture a screen region using GDI BitBlt."""
    hwnd_desktop = 0
    hwndDC = None
    mfcDC = None
    saveBitMap = None

    try:
        hwndDC = ctypes.windll.user32.GetDC(hwnd_desktop)
        mfcDC = ctypes.windll.gdi32.CreateCompatibleDC(hwndDC)
        saveBitMap = ctypes.windll.gdi32.CreateCompatibleBitmap(hwndDC, width, height)
        ctypes.windll.gdi32.SelectObject(mfcDC, saveBitMap)

        result = ctypes.windll.gdi32.BitBlt(
            mfcDC, 0, 0, width, height,
            hwndDC, x, y, 0x00CC0020  # SRCCOPY
        )
        if result == 0:
            print("ERROR: BitBlt failed.")
            return None

        bmpinfo = np.zeros(1, dtype=[
            ('biSize', 'i4'), ('biWidth', 'i4'), ('biHeight', 'i4'),
            ('biPlanes', 'i2'), ('biBitCount', 'i2'), ('biCompression', 'i4'),
            ('biSizeImage', 'i4'), ('biXPelsPerMeter', 'i4'), ('biYPelsPerMeter', 'i4'),
            ('biClrUsed', 'i4'), ('biClrImportant', 'i4')
        ])
        bmpinfo['biSize'] = 40
        bmpinfo['biWidth'] = width
        bmpinfo['biHeight'] = -height  # Negative = top-down
        bmpinfo['biPlanes'] = 1
        bmpinfo['biBitCount'] = 32

        buffer = np.zeros((height, width, 4), dtype=np.uint8)
        rows = ctypes.windll.gdi32.GetDIBits(
            mfcDC, saveBitMap, 0, height,
            buffer.ctypes.data, bmpinfo.ctypes.data, 0
        )
        if rows == 0:
            print("ERROR: GetDIBits failed.")
            return None

        return cv2.cvtColor(buffer, cv2.COLOR_BGRA2BGR)

    except Exception as e:
        print(f"ERROR in capture_window: {e}")
        traceback.print_exc()
        return None

    finally:
        if saveBitMap:
            ctypes.windll.gdi32.DeleteObject(saveBitMap)
        if mfcDC:
            ctypes.windll.gdi32.DeleteDC(mfcDC)
        if hwndDC:
            ctypes.windll.user32.ReleaseDC(hwnd_desktop, hwndDC)

def load_target_items():
    """Load target items from itens.txt."""
    items_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "itens.txt")
    if not os.path.exists(items_path):
        return []
    with open(items_path, "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

try:
    print("=" * 40)
    print("    SCREEN CAPTURE + OCR")
    print("=" * 40)

    hwnd, x, y, width, height = find_game_window()
    target_items = load_target_items()
    if target_items:
        print(f"Looking for items: {', '.join(target_items)}")

    reader = easyocr.Reader(['en'], gpu=False)

    print("\n[!] 4 SECONDS! Click on RubinOT and DON'T leave it!")
    for i in range(4, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\nCapturing game window...")
    image = capture_window(x, y, width, height)

    if image is not None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        screenshot_path = os.path.join(current_dir, "bot_vision.png")
        cv2.imwrite(screenshot_path, image)

        if np.std(image) < 2:
            print("\n" + "!" * 30)
            print("WARNING: THE IMAGE IS UNIFORM (likely black).")
            print("-" * 30)
            print("RubinOT has protection against video memory reading.")
            print("TRY THIS:")
            print("1. In the game, change 'Graphics Engine' to 'DirectX 9'.")
            print("2. RESTART your computer.")
            print("3. Run as ADMINISTRATOR.")
            print("-" * 30)
        else:
            print(f"SUCCESS! Screenshot saved at: {screenshot_path}")
            print("Analyzing text...")
            results = reader.readtext(image)
            for (bbox, text, confidence) in results:
                text_lower = text.lower()
                match = any(item in text_lower for item in target_items)
                prefix = "[MATCH]" if match else "       "
                print(f"{prefix} Read: '{text}' (confidence: {confidence:.2f})")
    else:
        print("ERROR: Failed to capture the screen.")

except Exception:
    traceback.print_exc()

finally:
    print("\nPROCESS FINISHED.")
    input("Press ENTER to exit...")
