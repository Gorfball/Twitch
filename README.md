# Floating Counter for Streamers

A customizable floating counter for tracking successes and attempts (e.g., mount drops, shiny hunts, etc.) on your stream. Designed for OBS or any screen capture setup.

---

## 1. Prerequisites

- **Python 3.8 or newer**
  - Download from: https://www.python.org/downloads/
  - During installation, make sure to check the box that says **"Add Python to PATH"**.
- **pip** (Python package manager)
  - Usually included with Python. If not, see: https://pip.pypa.io/en/stable/installation/

---

## 2. Installation

1. **Download or clone this folder to your computer.**
2. Open a terminal (Command Prompt or PowerShell) in the folder containing the files (e.g., `C:\Users\YourName\Documents\Cursor\Twitch_Counter`).
3. Install the required packages by running:
   ```sh
   pip install -r requirements_floating_counter.txt
   ```

---

## 3. Running the Counter

1. In the same folder, run:
   ```sh
   python floating_counter_tkinter.py
   ```
2. A setup window will appear. Here you can:
   - Set the label (e.g., "Mounts Dropped:")
   - Choose font, size, and color
   - Choose whether to track attempts (denominator)
   - Choose whether to use global hotkeys
   - Choose whether to show on-screen buttons
   - Assign hotkeys for incrementing/decrementing (if enabled)
3. Click **Run** to launch the floating counter.

---

## 4. Features and Usage

- **Floating, borderless, always-on-top window**
- **Transparent background** (only the text and buttons are visible)
- **Draggable**: Click and drag the counter text to move it
- **Increment/Decrement**:
  - Use on-screen buttons (if enabled)
  - Or use global hotkeys (if enabled)
- **Success +**: Increases both numerator and denominator (e.g., a successful drop)
- **Success -**: Decreases only the numerator (undo a success)
- **Attempt + / -**: Only affect the denominator (if attempts are enabled)
- **F2**: Open settings to change label, font, color, hotkeys, and button visibility
- **Escape**: Close the counter

### For OBS/Streaming
- Add the counter window as a **Window Capture** source in OBS
- Enable "Capture layered windows" and "Allow transparency" for best results

---

## 5. Troubleshooting

- **Hotkeys not working?**
  - Make sure you have not disabled global hotkeys in the setup/settings.
  - Some keys may not work globally on all systems; try simple keys (like a, b, etc.) if you have issues.
  - If you get errors about missing permissions, try running your terminal as administrator.
- **Buttons not visible?**
  - Make sure "Show on-screen buttons" is checked in the setup/settings.
- **Window not transparent in OBS?**
  - In OBS, right-click your Window Capture source, go to Properties, and check "Allow transparency".
- **Font or button size issues?**
  - Try increasing the font size in the settings for better visibility.

---

## Need Help?
If you have any issues or suggestions, feel free to open an issue or contact the script author. 