"""
test1.py - Affinity Detection (Diagnostic)

Detects which anti-screenshot protection the game uses and monitors
exactly WHEN it activates. Run this FIRST to understand the protection.

Uses: GetWindowDisplayAffinity via ctypes
Deps: pip install pywin32
"""

import ctypes
import time
import sys
import win32gui

WINDOW_TITLE = "RubinOT"

WDA_FLAGS = {
    0x00000000: "WDA_NONE (no protection)",
    0x00000001: "WDA_MONITOR (legacy protection - PrintWindow may work)",
    0x00000011: "WDA_EXCLUDEFROMCAPTURE (full protection - blocks all capture APIs)",
}


def find_game_window():
    """Find the RubinOT window handle."""
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        print("Make sure RubinOT is running.")
        sys.exit(1)
    print(f"Found window '{WINDOW_TITLE}' (hwnd={hwnd:#x})")
    return hwnd


def get_display_affinity(hwnd):
    """Read the current display affinity flag for the window."""
    affinity = ctypes.c_uint32()
    result = ctypes.windll.user32.GetWindowDisplayAffinity(
        hwnd, ctypes.byref(affinity)
    )
    if result:
        return affinity.value
    return None


def main():
    print("=" * 50)
    print("  TEST 1 - Display Affinity Detection")
    print("=" * 50)

    hwnd = find_game_window()

    initial = get_display_affinity(hwnd)
    if initial is None:
        print("ERROR: GetWindowDisplayAffinity failed.")
        sys.exit(1)

    flag_name = WDA_FLAGS.get(initial, f"UNKNOWN ({initial:#x})")
    print(f"\nInitial affinity: {flag_name}")

    if initial != 0:
        print("\nProtection is ALREADY active!")
        print("The anti-cheat enabled it before we could check.")
        input("\nPress ENTER to exit...")
        return

    print("\nProtection is NOT active yet. Monitoring every second...")
    print("Keep the game running. Will detect when protection activates.\n")

    start_time = time.time()
    last_value = initial

    try:
        for i in range(120):  # Monitor for up to 2 minutes
            current = get_display_affinity(hwnd)
            elapsed = time.time() - start_time

            if current is None:
                print(f"[{elapsed:6.1f}s] WARNING: GetWindowDisplayAffinity failed "
                      "(window closed?)")
                break

            if current != last_value:
                flag_name = WDA_FLAGS.get(current, f"UNKNOWN ({current:#x})")
                print(f"\n{'!'*50}")
                print(f"  PROTECTION ACTIVATED at {elapsed:.1f} seconds!")
                print(f"  New affinity: {flag_name}")
                print(f"{'!'*50}\n")

                if current == 0x00000001:
                    print("GOOD NEWS: WDA_MONITOR detected.")
                    print("PrintWindow with PW_RENDERFULLCONTENT (test2.py) MAY work!")
                elif current == 0x00000011:
                    print("WDA_EXCLUDEFROMCAPTURE detected.")
                    print("Most capture APIs are blocked.")
                    print("Try: OBS Game Capture (test5.py) or Virtual Display (test6.py)")

                last_value = current

            status = WDA_FLAGS.get(current, f"UNKNOWN ({current:#x})")
            print(f"[{elapsed:6.1f}s] Affinity: {status}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

    print("\nDone.")
    input("Press ENTER to exit...")


if __name__ == "__main__":
    main()
