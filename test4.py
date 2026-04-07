"""
test4.py - BetterCam (improved dxcam fork)

BetterCam is a maintained fork of dxcam with improvements.
Tests DXGI Output Duplication capture, including:
- Multiple output indices (useful if a virtual display is installed)
- Session recreation when frames go black

Note: Like dxcam, this will likely only work for ~15 seconds
before SetWindowDisplayAffinity blocks it. Useful for initial
calibration or if combined with a virtual display (test6.py).

Deps: pip install bettercam opencv-python numpy easyocr
"""

import os
import ssl
import sys
import time
import traceback
import numpy as np
import cv2
import easyocr

ssl._create_default_https_context = ssl._create_unverified_context

OUTPUT_FILE = "capture_test4.png"
WINDOW_TITLE = "RubinOT"


def find_game_window():
    """Find game window position for region capture."""
    import win32gui
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        sys.exit(1)

    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
    print(f"Found '{WINDOW_TITLE}' at ({left},{top}) to ({right},{bottom})")
    return left, top, right, bottom


def try_bettercam_capture(output_idx=0, region=None):
    """Try capturing with BetterCam on a specific output."""
    import bettercam

    print(f"\nTrying BetterCam on output {output_idx}...")

    try:
        camera = bettercam.create(output_idx=output_idx, output_color="BGR")
    except Exception as e:
        print(f"  Could not create camera on output {output_idx}: {e}")
        return None

    try:
        if region:
            frame = camera.grab(region=region)
        else:
            frame = camera.grab()

        if frame is None:
            print(f"  Output {output_idx}: grab() returned None.")
            return None

        if np.std(frame) < 2:
            print(f"  Output {output_idx}: Image is black (std={np.std(frame):.2f}).")
            return None

        print(f"  Output {output_idx}: Got valid frame! ({frame.shape})")
        return frame

    finally:
        del camera


def try_continuous_capture(region=None):
    """Start continuous capture before protection activates."""
    import bettercam

    print("\nStarting continuous capture (trying to keep session alive)...")
    camera = bettercam.create(output_idx=0, output_color="BGR")

    try:
        camera.start(target_fps=10)
        valid_frames = 0
        black_frames = 0

        for i in range(100):  # Try for ~10 seconds
            frame = camera.get_latest_frame()
            if frame is not None:
                if np.std(frame) > 2:
                    valid_frames += 1
                    if region:
                        left, top, right, bottom = region
                        frame = frame[top:bottom, left:right]
                    last_good = frame.copy()
                else:
                    black_frames += 1

                if black_frames > 5 and valid_frames > 0:
                    print(f"  Protection activated after {valid_frames} good frames.")
                    print(f"  Returning last valid frame.")
                    return last_good

            time.sleep(0.1)

        camera.stop()

        if valid_frames > 0:
            print(f"  Got {valid_frames} valid frames, {black_frames} black frames.")
            return last_good
        else:
            print(f"  All {black_frames} frames were black.")
            return None

    finally:
        try:
            camera.stop()
        except Exception:
            pass
        del camera


def main():
    print("=" * 50)
    print("  TEST 4 - BetterCam (DXGI Output Duplication)")
    print("=" * 50)

    left, top, right, bottom = find_game_window()
    region = (left, top, right, bottom)

    # Attempt 1: Direct grab on each available output
    for idx in range(4):  # Try up to 4 outputs
        frame = try_bettercam_capture(output_idx=idx, region=region if idx == 0 else None)
        if frame is not None:
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE
            )
            cv2.imwrite(output_path, frame)
            print(f"\nSUCCESS! Image captured from output {idx}: {output_path}")

            print("Running OCR...")
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(frame)

            print("\n" + "=" * 40)
            print("  TEXTS FOUND")
            print("=" * 40)
            for (bbox, text, confidence) in results:
                print(f"  '{text}' (confidence: {confidence:.2f})")
            print("=" * 40)

            input("\nPress ENTER to exit...")
            return

    # Attempt 2: Continuous capture (try to catch frames before protection)
    frame = try_continuous_capture(region=region)
    if frame is not None:
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE
        )
        cv2.imwrite(output_path, frame)
        print(f"\nPARTIAL SUCCESS: Captured last valid frame before protection.")
        print(f"Saved to: {output_path}")
    else:
        print("\nFAILED: All capture attempts returned black.")
        print("DXGI Duplication is blocked by SetWindowDisplayAffinity.")
        print("Try test5.py (OBS) or test6.py (Virtual Display).")

    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("\nPress ENTER to exit...")
