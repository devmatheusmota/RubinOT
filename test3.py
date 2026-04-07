"""
test3.py - Windows.Graphics.Capture API

Uses the modern Windows 10/11 screen capture API via the
'windows-capture' Python library. Tests both window-specific
and monitor-wide capture modes.

Requires Windows 10 version 1903 or later.

Deps: pip install windows-capture opencv-python numpy easyocr
"""

import os
import ssl
import sys
import traceback

ssl._create_default_https_context = ssl._create_unverified_context

OUTPUT_FILE = "capture_test3.png"


def try_window_capture():
    """Try capturing the RubinOT window using Windows.Graphics.Capture."""
    from windows_capture import WindowsCapture, Frame, InternalCaptureControl

    captured_frame = [None]

    capture = WindowsCapture(
        cursor_capture=None,
        draw_border=None,
        monitor_index=None,
        window_name="RubinOT",
    )

    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE
        )
        frame.save_as_image(output_path)
        captured_frame[0] = output_path
        capture_control.stop()

    @capture.event
    def on_closed():
        pass

    print("Starting Windows.Graphics.Capture (window mode)...")
    capture.start()
    return captured_frame[0]


def try_monitor_capture():
    """Try capturing the primary monitor using Windows.Graphics.Capture."""
    from windows_capture import WindowsCapture, Frame, InternalCaptureControl

    captured_frame = [None]

    capture = WindowsCapture(
        cursor_capture=None,
        draw_border=None,
        monitor_index=0,
        window_name=None,
    )

    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "capture_test3_monitor.png"
        )
        frame.save_as_image(output_path)
        captured_frame[0] = output_path
        capture_control.stop()

    @capture.event
    def on_closed():
        pass

    print("Starting Windows.Graphics.Capture (monitor mode)...")
    capture.start()
    return captured_frame[0]


def validate_and_ocr(image_path):
    """Check if image is valid and run OCR."""
    import numpy as np
    import cv2
    import easyocr

    image = cv2.imread(image_path)
    if image is None:
        print("FAILED: Could not read saved image.")
        return False

    if np.std(image) < 2:
        print(f"FAILED: Image is black/uniform (std={np.std(image):.2f}).")
        return False

    print(f"SUCCESS! Image captured: {image_path}")
    print("Running OCR...")

    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(image)

    print("\n" + "=" * 40)
    print("  TEXTS FOUND")
    print("=" * 40)
    for (bbox, text, confidence) in results:
        print(f"  '{text}' (confidence: {confidence:.2f})")
    print("=" * 40)
    return True


def main():
    print("=" * 50)
    print("  TEST 3 - Windows.Graphics.Capture API")
    print("=" * 50)

    # Try window-specific capture first
    print("\n--- Attempt 1: Window capture ---")
    try:
        path = try_window_capture()
        if path:
            if validate_and_ocr(path):
                input("\nPress ENTER to exit...")
                return
            print("Window capture returned black image.")
    except Exception as e:
        print(f"Window capture failed: {e}")

    # Fallback to monitor capture
    print("\n--- Attempt 2: Monitor capture ---")
    try:
        path = try_monitor_capture()
        if path:
            if validate_and_ocr(path):
                input("\nPress ENTER to exit...")
                return
            print("Monitor capture returned black image.")
    except Exception as e:
        print(f"Monitor capture failed: {e}")

    print("\nFAILED: Both capture modes returned black or failed.")
    print("Windows.Graphics.Capture respects SetWindowDisplayAffinity.")
    print("Try test5.py (OBS) or test6.py (Virtual Display) instead.")
    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("\nPress ENTER to exit...")
