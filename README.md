# RubinOT Bot

Automation bot for [RubinOT](https://rubinot.com) (Open Tibia Server). Automates click sequences and reads on-screen text via OCR.

**Windows only.** Requires Python 3.8+.

## Setup

1. Install Python from [python.org](https://www.python.org/downloads/) (check "Add to PATH" during install)

2. Install dependencies:
```
pip install pyautogui pywin32 easyocr opencv-python numpy
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

## Troubleshooting

| Problem | Solution |
|---|---|
| `Could not find window 'RubinOT'` | Make sure the game is open. If the window title is different, update `WINDOW_TITLE` in `bot.py` and `test_vision.py` |
| Screenshot is black | Change Graphics Engine to DirectX 9 in game settings, restart, and run as Administrator |
| Clicks hit the wrong spot | Use `mouse_monitor.py` to find the correct coordinates, then update them in `bot.py` |
| `ModuleNotFoundError` | Run `pip install pyautogui pywin32 easyocr opencv-python numpy` |
