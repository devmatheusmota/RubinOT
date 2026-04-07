"""
test7.py - Pymem DLL Injection (remove protection from inside the process)

Injects into the RubinOT process and calls SetWindowDisplayAffinity(hwnd, WDA_NONE)
from INSIDE the game process. This is the most aggressive approach.

SetWindowDisplayAffinity can only be changed by the process that owns the window.
By injecting code into the game process, we can call it as if we were the game.

WARNING: This is the most likely to be detected by anti-cheat (EMAC).
         Use this as a last resort.

REQUIRES: Run as Administrator

Deps: pip install pymem pywin32 dxcam opencv-python numpy easyocr
"""

import os
import ssl
import sys
import time
import traceback
import ctypes
import numpy as np
import cv2
import win32gui
import easyocr

ssl._create_default_https_context = ssl._create_unverified_context

WINDOW_TITLE = "RubinOT"
PROCESS_NAME = "RubinOT.exe"
OUTPUT_FILE = "capture_test7.png"

WDA_NONE = 0x00000000


def check_admin():
    """Check if script is running as Administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_current_affinity(hwnd):
    """Read the current display affinity."""
    affinity = ctypes.c_uint32()
    result = ctypes.windll.user32.GetWindowDisplayAffinity(
        hwnd, ctypes.byref(affinity)
    )
    if result:
        return affinity.value
    return None


def remove_affinity_via_injection(hwnd):
    """Inject into the game process and remove display affinity."""
    import pymem
    import pymem.process

    print("Opening game process...")
    try:
        pm = pymem.Pymem(PROCESS_NAME)
    except pymem.exception.ProcessNotFound:
        print(f"ERROR: Process '{PROCESS_NAME}' not found.")
        print("Make sure RubinOT is running.")
        return False
    except pymem.exception.CouldNotOpenProcess:
        print("ERROR: Could not open process. Run as Administrator!")
        return False

    print(f"  Process ID: {pm.process_id}")
    print(f"  Window handle: {hwnd:#x}")

    # Get address of SetWindowDisplayAffinity in user32.dll
    user32_base = None
    for module in pymem.process.enum_process_module(pm.process_handle):
        if module.name and "user32.dll" in module.name.lower():
            user32_base = module.lpBaseOfDll
            break

    if user32_base is None:
        print("ERROR: Could not find user32.dll in game process.")
        pm.close_process()
        return False

    print(f"  user32.dll base: {user32_base:#x}")

    # Get the function address from our own process (same offset in all processes)
    local_user32 = ctypes.windll.user32._handle
    local_func = ctypes.windll.user32.SetWindowDisplayAffinity
    func_offset = ctypes.cast(local_func, ctypes.c_void_p).value - local_user32
    remote_func = user32_base + func_offset

    print(f"  SetWindowDisplayAffinity at: {remote_func:#x}")

    # Shellcode: call SetWindowDisplayAffinity(hwnd, WDA_NONE) and return
    # x64 shellcode:
    #   mov rcx, <hwnd>          ; first arg = hwnd
    #   xor edx, edx             ; second arg = WDA_NONE (0)
    #   mov rax, <func_addr>     ; address of SetWindowDisplayAffinity
    #   call rax
    #   ret
    hwnd_bytes = hwnd.to_bytes(8, 'little')
    func_bytes = remote_func.to_bytes(8, 'little')

    shellcode = (
        b"\x48\xB9" + hwnd_bytes +          # mov rcx, hwnd
        b"\x31\xD2" +                         # xor edx, edx (WDA_NONE = 0)
        b"\x48\xB8" + func_bytes +           # mov rax, SetWindowDisplayAffinity
        b"\xFF\xD0" +                         # call rax
        b"\xC3"                               # ret
    )

    print("Injecting shellcode to remove display affinity...")

    try:
        # Allocate memory in target process
        alloc = pm.allocate(len(shellcode))
        print(f"  Allocated memory at: {alloc:#x}")

        # Write shellcode
        pm.write_bytes(alloc, shellcode, len(shellcode))

        # Execute shellcode in remote thread
        thread_handle = pm.start_thread(alloc)
        print(f"  Thread started: {thread_handle:#x}")

        # Wait for it to complete
        ctypes.windll.kernel32.WaitForSingleObject(
            ctypes.c_void_p(thread_handle), 5000  # 5 second timeout
        )

        # Cleanup
        pm.free(alloc)
        pm.close_process()

        print("  Injection complete!")
        return True

    except Exception as e:
        print(f"  Injection failed: {e}")
        pm.close_process()
        return False


def capture_with_dxcam():
    """Try to capture with dxcam after removing protection."""
    import dxcam

    camera = dxcam.create(output_color="BGR")
    frame = camera.grab()
    del camera
    return frame


def main():
    print("=" * 50)
    print("  TEST 7 - Pymem Injection (Remove Protection)")
    print("=" * 50)

    if not check_admin():
        print("\nWARNING: Not running as Administrator!")
        print("This script REQUIRES admin privileges for process injection.")
        print("Right-click the terminal and select 'Run as administrator'.\n")

    # Find game window
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd == 0:
        print(f"ERROR: Could not find window '{WINDOW_TITLE}'.")
        sys.exit(1)
    print(f"Found '{WINDOW_TITLE}' (hwnd={hwnd:#x})")

    # Check current protection
    affinity = get_current_affinity(hwnd)
    if affinity is not None:
        flags = {0x0: "WDA_NONE", 0x1: "WDA_MONITOR", 0x11: "WDA_EXCLUDEFROMCAPTURE"}
        print(f"Current affinity: {flags.get(affinity, f'UNKNOWN ({affinity:#x})')}")

        if affinity == 0:
            print("No protection detected! Capturing directly...")
        else:
            print("\nProtection is active. Attempting injection to remove it...")
            success = remove_affinity_via_injection(hwnd)

            if success:
                time.sleep(1)
                new_affinity = get_current_affinity(hwnd)
                if new_affinity == 0:
                    print("Protection REMOVED successfully!")
                else:
                    flag_name = flags.get(new_affinity, f"UNKNOWN ({new_affinity:#x})")
                    print(f"Affinity still set to {flag_name}.")
                    print("The anti-cheat may have re-applied it.")
    else:
        print("Could not read display affinity.")

    # Try capture
    print("\nCapturing with dxcam...")
    frame = capture_with_dxcam()

    if frame is None or np.std(frame) < 2:
        std = np.std(frame) if frame is not None else 0
        print(f"\nFAILED: Image is black (std={std:.2f}).")
        print("The injection may not have worked, or anti-cheat re-applied protection.")
        print("Try test5.py (OBS) instead.")
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
