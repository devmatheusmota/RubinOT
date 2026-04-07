# RubinOT Bot

Automation bot for [RubinOT](https://rubinot.com) (Open Tibia Server). Automates click sequences and reads on-screen text via OCR.

**Windows only.** Requires Python 3.8+.

## Setup

1. Install Python from [python.org](https://www.python.org/downloads/) (check "Add to PATH" during install)

2. Install dependencies:
```
pip install pyautogui pywin32 easyocr opencv-python numpy dxcam bettercam windows-capture pymem
```

## Scripts

### `mouse_monitor.py` — Find Coordinates

Real-time monitor that shows your mouse position and pixel color. Use this to find the screen coordinates you need for the bot.

```
python mouse_monitor.py
```

Move your mouse over the game elements you want to click and note the X/Y values. Press `CTRL+C` to stop.

### `bot.py` — Automated Clicks

Sends a sequence of clicks to the RubinOT window. Edit the coordinates at the top of the file to match your setup:

```python
RIGHT_CLICK_1 = (851, 388)   # First right click
RIGHT_CLICK_2 = (1884, 355)  # Second right click
LEFT_CLICK_3 = (1320, 820)   # Left click
```

To run:
```
python bot.py
```

The bot will automatically find the RubinOT window by its title. No need to alt-tab — just make sure the game is open.

### `test_vision.py` — Screen Capture + OCR

Captures a screenshot of the RubinOT window and reads all text on screen using OCR. Useful for identifying items, NPCs, or any text the bot needs to react to.

```
python test_vision.py
```

- The screenshot is saved as `bot_vision.png`
- Items listed in `itens.txt` are highlighted with `[MATCH]` in the output
- If the screenshot comes back black, change the game's Graphics Engine to **DirectX 9** and run as **Administrator**

### `itens.txt` — Target Items

Add one item name per line. The OCR script will flag these when found on screen:

```
dragon shield
magic plate armor
```

## Screen Capture Bypass Tests

RubinOT has anti-screenshot protection that activates ~15 seconds after the game starts (likely `SetWindowDisplayAffinity`). The test scripts below try different approaches to bypass it.

**Run `test1.py` first** to identify which protection the game uses, then try the others.

| Script | Approach | Chance | Extra Setup |
|--------|----------|--------|-------------|
| `test1.py` | Affinity detection (diagnostic) | N/A | None |
| `test2.py` | PrintWindow + PW_RENDERFULLCONTENT | Low-Medium | None |
| `test3.py` | Windows.Graphics.Capture API | Low | Windows 10 1903+ |
| `test4.py` | BetterCam (DXGI Duplication) | Low | None |
| `test5.py` | **OBS Virtual Camera** | **Very High** | OBS Studio + Game Capture |
| `test6.py` | **Virtual Display Driver** | **Very High** | Virtual Display Driver install |
| `test7.py` | Pymem injection (remove protection) | Medium | Run as Administrator |

### test5.py — OBS Virtual Camera (Recommended)

This is the most likely to work. OBS Game Capture hooks into the game's rendering pipeline, bypassing the protection entirely. This is the same approach used by [TibiaAuto12](https://github.com/MuriloChianfa/TibiaAuto12).

1. Install [OBS Studio](https://obsproject.com/download)
2. Create a new Scene, add a **Game Capture** source
3. Set Mode to **Capture specific window**, select `[RubinOT.exe]: RubinOT`
4. Click **Start Virtual Camera** (bottom right of OBS)
5. Run `python test5.py`

### test6.py — Virtual Display Driver

Architecturally guaranteed to work because `SetWindowDisplayAffinity` only blocks capture APIs, not display outputs. A virtual monitor receives the full GPU scanout.

1. Download [Virtual Display Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver/releases)
2. Install the driver via Device Manager (requires Admin)
3. Set display mode to **Duplicate** in Windows Display Settings
4. Run `python test6.py`

## Troubleshooting

| Problem | Solution |
|---|---|
| `Could not find window 'RubinOT'` | Make sure the game is open. If the window title is different, update `WINDOW_TITLE` in `bot.py` and `test_vision.py` |
| Screenshot is black | Change Graphics Engine to DirectX 9 in game settings, restart, and run as Administrator |
| Clicks hit the wrong spot | Use `mouse_monitor.py` to find the correct coordinates, then update them in `bot.py` |
| `ModuleNotFoundError` | Run `pip install pyautogui pywin32 easyocr opencv-python numpy` |
