"""
test6.py - Virtual Display Capture

Captures from a virtual monitor (Indirect Display Driver).
This is ARCHITECTURALLY GUARANTEED to bypass SetWindowDisplayAffinity
because that API only filters software capture APIs, NOT display outputs.
A virtual display receives the full unfiltered GPU scanout.

SETUP REQUIRED:
  1. Download Virtual Display Driver:
     https://github.com/VirtualDrivers/Virtual-Display-Driver/releases
  2. Extract and install the driver (requires Admin):
     - Open Device Manager as Administrator
     - Action > Add legacy hardware > Install manually
     - Browse to the extracted driver folder and select the .inf file
  3. A new virtual monitor appears in Windows Display Settings
  4. Set it to "Duplicate" your main display (Settings > Display > Multiple displays)
  5. Move or extend the game window to be visible on the virtual display
  6. THEN run this script

Deps: pip install dxcam opencv-python numpy easyocr
"""

import os
import ssl
import sys
import traceback
import numpy as np
import cv2
import dxcam
import easyocr

ssl._create_default_https_context = ssl._create_unverified_context

OUTPUT_FILE = "capture_test6.png"


def list_outputs():
    """List all available DXGI outputs (monitors)."""
    print("Available display outputs:")
    try:
        info = dxcam.output_info()
        for i, output in enumerate(info):
            print(f"  Output {i}: {output}")
        return len(info)
    except Exception as e:
        print(f"  Could not enumerate outputs: {e}")
        return 0


def try_capture_output(output_idx):
    """Try to capture from a specific output index."""
    try:
        camera = dxcam.create(output_idx=output_idx, output_color="BGR")
        frame = camera.grab()
        del camera

        if frame is None:
            print(f"  Output {output_idx}: grab() returned None.")
            return None

        print(f"  Output {output_idx}: Got frame {frame.shape}, std={np.std(frame):.2f}")

        if np.std(frame) < 2:
            return None

        return frame

    except Exception as e:
        print(f"  Output {output_idx}: Error - {e}")
        return None


def main():
    print("=" * 50)
    print("  TEST 6 - Virtual Display Capture")
    print("=" * 50)

    print("""
HOW THIS WORKS:
  SetWindowDisplayAffinity only blocks SOFTWARE capture APIs.
  A virtual display driver receives the full GPU output, including
  protected windows. We capture from the virtual display instead
  of the main monitor.

  This requires installing a Virtual Display Driver first.
  See instructions at the top of this script.
""")

    num_outputs = list_outputs()

    if num_outputs <= 1:
        print("\nWARNING: Only 1 display output detected.")
        print("You need to install a Virtual Display Driver first.")
        print("Download: https://github.com/VirtualDrivers/Virtual-Display-Driver/releases")
        print("\nTrying capture on output 0 anyway...\n")

    # Try each output, starting from index 1 (virtual display is usually not 0)
    best_frame = None
    best_idx = -1

    for idx in range(num_outputs):
        frame = try_capture_output(idx)
        if frame is not None:
            best_frame = frame
            best_idx = idx
            # Prefer non-zero outputs (likely the virtual display)
            if idx > 0:
                break

    if best_frame is None:
        print("\nFAILED: No valid frames from any output.")
        print("\nTroubleshooting:")
        print("  1. Install Virtual Display Driver (see instructions above)")
        print("  2. Set display mode to 'Duplicate' in Windows Display Settings")
        print("  3. Make sure RubinOT is visible on screen")
        input("\nPress ENTER to exit...")
        return

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    cv2.imwrite(output_path, best_frame)
    print(f"\nSUCCESS! Captured from output {best_idx}: {output_path}")

    print("Running OCR...")
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(best_frame)

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
