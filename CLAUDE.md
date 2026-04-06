# RubinOT Bot

Bot for automating actions in RubinOT (Open Tibia Server). Windows-only.

## Project Structure

- `bot.py` — Executes a sequence of automated clicks (right/left) on the game window using Win32 API (`PostMessage`)
- `mouse_monitor.py` — Utility that monitors mouse position (X/Y) and pixel color in real-time, used to find coordinates for the bot
- `test_vision.py` — Screen capture + OCR (EasyOCR). Captures the RubinOT window via GDI/BitBlt and reads text from it
- `itens.txt` — List of target items (e.g. `dragon shield`)
- `bot_vision.png` — Latest screenshot captured by `test_vision.py`

## Tech Stack

- Python 3
- `pyautogui` — mouse movement
- `win32api` / `win32gui` / `win32con` — sending click events and finding the game window
- `easyocr` + `opencv-python` + `numpy` — screen capture and text recognition
- `ctypes` — low-level GDI calls for screen capture

## How It Works

- `bot.py` finds the RubinOT window by title using `FindWindow`, converts screen coordinates to client-relative, and sends clicks via `PostMessage` with properly encoded lParam coordinates.
- `test_vision.py` auto-detects the game window position/size, captures via GDI BitBlt, runs OCR, and highlights matches from `itens.txt`.

## Known Issues

- The game has anti-screenshot protection that blocks GDI screen capture (image comes back black). Workaround: switch Graphics Engine to DirectX 9 and run as Administrator.

## Conventions

- All code, comments, variable names, and prints must be in English.
