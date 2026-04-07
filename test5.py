"""
test5.py - OBS Virtual Camera via OpenCV

This is the MOST LIKELY approach to work. OBS Game Capture hooks
directly into the game's rendering pipeline (IDXGISwapChain::Present),
capturing frames BEFORE they reach the DWM compositor. This completely
bypasses SetWindowDisplayAffinity protection.

OBS is often WHITELISTED by anti-cheat systems. TibiaAuto12 (a popular
Tibia bot) uses this exact approach.

SETUP REQUIRED:
  1. Install OBS Studio: https://obsproject.com/download
  2. Open OBS and create a new Scene
  3. Add a "Game Capture" source:
     - Mode: "Capture specific window"
     - Window: select "[RubinOT.exe]: RubinOT"
     - Check "Allow transparency" if available
  4. Click "Start Virtual Camera" in OBS (bottom right)
  5. THEN run this script

Deps: pip install opencv-python numpy easyocr
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

OUTPUT_FILE = "capture_test5.png"


def find_virtual_camera():
    """Try to find the OBS Virtual Camera by testing camera indices."""
    print("Searching for OBS Virtual Camera...")

    for idx in range(10):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            continue

        # Read a test frame
        ret, frame = cap.read()
        backend = cap.getBackendName()
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cap.release()

        if ret and frame is not None:
            print(f"  Camera {idx}: {w}x{h} ({backend})")

    print("\nTrying each camera for non-black frames...")
    print("(Make sure OBS Virtual Camera is started)\n")

    for idx in range(10):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            continue

        # Read multiple frames (first frames can be black)
        valid = False
        for attempt in range(15):
            ret, frame = cap.read()
            if ret and frame is not None and np.std(frame) > 5:
                valid = True
                break
            time.sleep(0.1)

        if valid:
            print(f"  Camera {idx}: VALID frame detected!")
            cap.release()
            return idx

        cap.release()

    return None


def capture_from_camera(camera_idx):
    """Capture a frame from the virtual camera."""
    cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera {camera_idx}.")
        return None

    # Set resolution as high as possible
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Warm up - skip initial black frames
    print("Warming up camera (reading initial frames)...")
    for _ in range(30):
        cap.read()

    # Capture the actual frame
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("ERROR: Could not read frame from camera.")
        return None

    return frame


def main():
    print("=" * 50)
    print("  TEST 5 - OBS Virtual Camera Capture")
    print("=" * 50)

    print("""
PREREQUISITES:
  1. OBS Studio must be running
  2. A "Game Capture" source must be pointed at RubinOT
  3. "Start Virtual Camera" must be active in OBS

If you haven't set this up yet, press CTRL+C and follow
the setup instructions at the top of this script.
""")

    camera_idx = find_virtual_camera()

    if camera_idx is None:
        print("\nFAILED: No virtual camera with valid frames found.")
        print("\nPossible issues:")
        print("  - OBS is not running")
        print("  - Virtual Camera is not started (click 'Start Virtual Camera' in OBS)")
        print("  - Game Capture source is not configured correctly")
        print("  - Try selecting 'Capture specific window' in OBS Game Capture settings")
        input("\nPress ENTER to exit...")
        return

    print(f"\nUsing camera index: {camera_idx}")
    print("Capturing frame...")

    frame = capture_from_camera(camera_idx)

    if frame is None or np.std(frame) < 2:
        std = np.std(frame) if frame is not None else 0
        print(f"\nFAILED: Frame is black/uniform (std={std:.2f}).")
        print("Check OBS Game Capture settings.")
        input("\nPress ENTER to exit...")
        return

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    cv2.imwrite(output_path, frame)
    print(f"\nSUCCESS! Image captured: {output_path}")

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


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("\nPress ENTER to exit...")
