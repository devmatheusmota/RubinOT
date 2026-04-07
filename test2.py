"""
test2.py - PrintWindow with PW_RENDERFULLCONTENT

Uses the PrintWindow API with the PW_RENDERFULLCONTENT flag (0x02).
This asks the window to render itself into a DC, which can sometimes
bypass protections that only block compositor-level capture.

Works if the game uses WDA_MONITOR. Blocked by WDA_EXCLUDEFROMCAPTURE.

Deps: pip install pywin32 opencv-python numpy easyocr
"""

import os
import ssl
import sys
import ctypes
from ctypes import windll
import numpy as np
import cv2
import easyocr
import win32gui
import traceback

ssl._create_default_https_context = ssl._create_unverified_context

WINDOW_TITLE = "RubinOT"
PW_RENDERFULLCONTENT = 0x00000002
OUTPUT_FILE = "capture_test2.png"


def find_game_window():
    """Find the RubinOT window handle and dimensions."""
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        sys.exit(1)

    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"Found '{WINDOW_TITLE}' at ({left},{top}) size {width}x{height}")
    return hwnd, width, height


def capture_printwindow(hwnd, width, height):
    """Capture window using PrintWindow + PW_RENDERFULLCONTENT."""
    hwndDC = None
    mfcDC = None
    saveBitMap = None

    try:
        hwndDC = windll.user32.GetWindowDC(hwnd)
        if not hwndDC:
            print("ERROR: GetWindowDC failed.")
            return None

        mfcDC = windll.gdi32.CreateCompatibleDC(hwndDC)
        saveBitMap = windll.gdi32.CreateCompatibleBitmap(hwndDC, width, height)
        windll.gdi32.SelectObject(mfcDC, saveBitMap)

        # The key call: PrintWindow with PW_RENDERFULLCONTENT
        result = windll.user32.PrintWindow(hwnd, mfcDC, PW_RENDERFULLCONTENT)
        if result == 0:
            print("WARNING: PrintWindow returned 0 (may have failed).")

        # Extract bitmap data
        bmpinfo = np.zeros(1, dtype=[
            ('biSize', 'i4'), ('biWidth', 'i4'), ('biHeight', 'i4'),
            ('biPlanes', 'i2'), ('biBitCount', 'i2'), ('biCompression', 'i4'),
            ('biSizeImage', 'i4'), ('biXPelsPerMeter', 'i4'),
            ('biYPelsPerMeter', 'i4'), ('biClrUsed', 'i4'),
            ('biClrImportant', 'i4')
        ])
        bmpinfo['biSize'] = 40
        bmpinfo['biWidth'] = width
        bmpinfo['biHeight'] = -height  # Top-down
        bmpinfo['biPlanes'] = 1
        bmpinfo['biBitCount'] = 32

        buffer = np.zeros((height, width, 4), dtype=np.uint8)
        windll.gdi32.GetDIBits(
            mfcDC, saveBitMap, 0, height,
            buffer.ctypes.data, bmpinfo.ctypes.data, 0
        )

        return cv2.cvtColor(buffer, cv2.COLOR_BGRA2BGR)

    finally:
        if saveBitMap:
            windll.gdi32.DeleteObject(saveBitMap)
        if mfcDC:
            windll.gdi32.DeleteDC(mfcDC)
        if hwndDC:
            windll.user32.ReleaseDC(hwnd, hwndDC)


def main():
    print("=" * 50)
    print("  TEST 2 - PrintWindow + PW_RENDERFULLCONTENT")
    print("=" * 50)

    hwnd, width, height = find_game_window()

    print("\nCapturing with PrintWindow (PW_RENDERFULLCONTENT)...")
    image = capture_printwindow(hwnd, width, height)

    if image is None:
        print("FAILED: Could not capture image.")
        input("\nPress ENTER to exit...")
        return

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    cv2.imwrite(output_path, image)

    if np.std(image) < 2:
        print(f"\nFAILED: Image is black/uniform (std={np.std(image):.2f}).")
        print("PrintWindow is blocked by the anti-screenshot protection.")
        print("Try test5.py (OBS) or test6.py (Virtual Display) instead.")
    else:
        print(f"\nSUCCESS! Image captured: {output_path}")
        print("Running OCR...")

        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(image)

        print("\n" + "=" * 40)
        print("  TEXTS FOUND")
        print("=" * 40)
        for (bbox, text, confidence) in results:
            print(f"  '{text}' (confidence: {confidence:.2f})")
        print("=" * 40)

    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("\nPress ENTER to exit...")
