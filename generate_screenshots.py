#!/usr/bin/env python3
"""
Screenshot generator for Stretch Timer
Automatically captures screenshots of the app in different states.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import time

# Add the current directory to path to import stretch_timer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app module
import stretch_timer

def capture_widget(widget, filename):
    """Capture a screenshot of a widget using PIL."""
    try:
        from PIL import ImageGrab

        # Update the widget to ensure it's rendered
        widget.update_idletasks()
        widget.update()
        time.sleep(0.3)  # Give time for rendering

        # Get widget position on screen
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()

        # Capture the region
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screenshot.save(filename)
        print(f"Saved: {filename}")
        return True
    except ImportError:
        print("PIL not installed. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error capturing {filename}: {e}")
        return False

def main():
    print("Stretch Timer Screenshot Generator")
    print("=" * 40)

    # Check for PIL
    try:
        from PIL import ImageGrab
    except ImportError:
        print("ERROR: Pillow is required. Install with: pip install Pillow")
        sys.exit(1)

    # Create the app
    print("Creating app instance...")
    app = stretch_timer.StretchTimerApp()

    # Set up a sample stretch to display (without sound/notification)
    print("Setting up display state...")
    # Disable sound temporarily
    original_sound = app.sound_enabled.get()
    app.sound_enabled.set(False)

    # Manually set up the display similar to trigger_stretch but without popup
    stretch = stretch_timer.STRETCHES[0]  # Use first stretch for consistency
    secondary_exercise = stretch_timer.EYE_EXERCISES[0]  # Use first eye exercise
    secondary_type = "eye"

    app.stretch_count = 3  # Show some activity
    app.current_stretch = stretch
    app.current_secondary_exercise = secondary_exercise

    # Update UI
    app.count_value.configure(text=str(app.stretch_count))
    app.stretch_name_label.configure(text=f"🧘 {stretch['name']}")
    app.stretch_duration_label.configure(text=stretch_timer.format_duration(stretch["duration"]))
    app.create_combined_step_labels(stretch, secondary_exercise, secondary_type)

    # Ensure window is visible and rendered
    app.root.deiconify()
    app.root.lift()
    app.root.update()
    time.sleep(0.5)

    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    os.makedirs(screenshots_dir, exist_ok=True)

    # Screenshot 1: Main window - Light theme
    print("\n1. Capturing main window (light theme)...")
    if app.theme != "light":
        app.toggle_theme()
        app.root.update()
        time.sleep(0.3)
    capture_widget(app.root, os.path.join(screenshots_dir, "screenshot-light.png"))

    # Screenshot 2: Main window - Dark theme
    print("\n2. Capturing main window (dark theme)...")
    app.toggle_theme()  # Switch to dark
    app.root.update()
    time.sleep(0.3)
    capture_widget(app.root, os.path.join(screenshots_dir, "screenshot-dark.png"))

    # Screenshot 3: Popup window (in dark theme)
    print("\n3. Capturing popup window...")
    # Create popup with proper parameters
    app.show_stretch_popup(stretch, secondary_exercise, secondary_type)
    app.root.update()
    time.sleep(0.5)

    # Find the popup window (it's a Toplevel)
    for widget in app.root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            capture_widget(widget, os.path.join(screenshots_dir, "screenshot-popup.png"))
            widget.destroy()
            break

    # Restore sound setting
    app.sound_enabled.set(original_sound)

    print("\n" + "=" * 40)
    print("Screenshots generated successfully!")
    print("Files created in images/:")
    print("  - images/screenshot-light.png (main window, light theme)")
    print("  - images/screenshot-dark.png (main window, dark theme)")
    print("  - images/screenshot-popup.png (stretch reminder popup)")

    # Clean exit
    app.root.quit()
    app.root.destroy()

if __name__ == "__main__":
    main()
