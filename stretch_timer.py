#!/usr/bin/env python3
"""
Stretch Reminder Timer - Cross-Platform GUI Application.

A desktop application that reminds users to get up and stretch at configurable
intervals. Features include:
- Standing body stretches with step-by-step instructions
- Eye exercises and breathing exercises (alternating)
- Configurable reminder intervals and quiet hours
- Light/dark theme support
- Desktop notifications via plyer
- Persistent settings via JSON

Dependencies:
    - tkinter (standard library)
    - plyer (optional, for desktop notifications)

Usage:
    python stretch_timer.py

Author: Created with assistance from Claude
License: MIT
"""

import tkinter as tk
from tkinter import ttk
import time
import random
from datetime import datetime
import threading
import json
import os
import sys
import subprocess

# Platform-specific audio support
if sys.platform == "win32":
    try:
        import winsound
        HAS_WINSOUND = True
    except ImportError:
        HAS_WINSOUND = False
else:
    HAS_WINSOUND = False

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


def play_notification_sound(root=None):
    """
    Play a notification sound in a cross-platform manner.

    Uses platform-specific implementations with graceful degradation:
    - Windows: winsound.PlaySound() with system sounds
    - Linux: subprocess calls to paplay, aplay, or canberra-gtk-play
    - Fallback: tkinter.bell()

    Args:
        root: tkinter root window (used for bell() fallback)

    Returns:
        bool: True if sound was played, False otherwise
    """
    # Windows: use winsound
    if sys.platform == "win32" and HAS_WINSOUND:
        try:
            winsound.PlaySound(
                "SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC
            )
            return True
        except Exception:
            pass

    # Linux: try various sound utilities
    elif sys.platform.startswith("linux"):
        sound_commands = [
            ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
            ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
            ["aplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
            ["canberra-gtk-play", "-i", "complete"],
            ["canberra-gtk-play", "-i", "bell"],
        ]
        for cmd in sound_commands:
            try:
                subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
            except (FileNotFoundError, OSError):
                continue

    # Fallback: tkinter bell
    if root:
        try:
            root.bell()
            return True
        except Exception:
            pass

    return False


# Settings file path - stored in same directory as script
SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "stretch_timer_settings.json"
)

# Breathing exercises - alternates with eye exercises
BREATHING_EXERCISES = [
    {
        "name": "Box Breathing",
        "duration": "1 min",
        "steps": [
            "Inhale slowly for 4 seconds",
            "Hold your breath for 4 seconds",
            "Exhale slowly for 4 seconds",
            "Hold empty for 4 seconds, repeat 3x",
        ]
    },
    {
        "name": "4-7-8 Relaxing Breath",
        "duration": "1 min",
        "steps": [
            "Inhale quietly through nose for 4 seconds",
            "Hold your breath for 7 seconds",
            "Exhale completely through mouth for 8 seconds",
            "Repeat 3 times",
        ]
    },
    {
        "name": "Deep Belly Breathing",
        "duration": "1 min",
        "steps": [
            "Place hand on belly, relax shoulders",
            "Inhale deeply, feel belly rise",
            "Exhale slowly, feel belly fall",
            "Repeat 5-6 slow breaths",
        ]
    },
    {
        "name": "Energizing Breath",
        "duration": "30 sec",
        "steps": [
            "Take a quick sniff-sniff-sniff through nose",
            "Exhale fully through mouth with a 'hah'",
            "This is one cycle",
            "Repeat 5 cycles, feel more alert",
        ]
    },
    {
        "name": "Calming Exhale Focus",
        "duration": "1 min",
        "steps": [
            "Inhale naturally for 4 seconds",
            "Exhale slowly for 6-8 seconds",
            "Focus only on the long exhale",
            "Repeat 5 times",
        ]
    },
    {
        "name": "Three-Part Breath",
        "duration": "1 min",
        "steps": [
            "Inhale: fill belly first, then ribs, then chest",
            "One smooth breath filling bottom to top",
            "Exhale: empty chest, ribs, then belly",
            "Repeat 4-5 times slowly",
        ]
    },
]

# Eye exercises - alternates with breathing exercises
EYE_EXERCISES = [
    {
        "name": "Eye Focus - Window Gaze",
        "duration": "20 sec",
        "steps": [
            "Look out a window at the farthest point",
            "Focus on that distant point for 20 seconds",
            "Let your eye muscles fully relax",
        ]
    },
    {
        "name": "Eye Focus - Near and Far",
        "duration": "30 sec",
        "steps": [
            "Focus on your thumb 10 inches away for 5 sec",
            "Look at something 20+ feet away for 5 sec",
            "Alternate back and forth 5 times",
        ]
    },
    {
        "name": "20-20-20 Rule",
        "duration": "20 sec",
        "steps": [
            "Find an object at least 20 feet away",
            "Focus on it for 20 seconds",
            "Blink naturally and breathe",
        ]
    },
    {
        "name": "Eye Relaxation - Palming",
        "duration": "20 sec",
        "steps": [
            "Rub palms together to warm them",
            "Cup warm palms over closed eyes",
            "Relax in the darkness for 20 seconds",
        ]
    },
    {
        "name": "Eye Circles",
        "duration": "30 sec",
        "steps": [
            "Keep head still, look up",
            "Slowly circle eyes clockwise",
            "Do 5 full circles",
            "Reverse: 5 circles counter-clockwise",
        ]
    },
    {
        "name": "Rapid Blinking",
        "duration": "20 sec",
        "steps": [
            "Blink rapidly for 10 seconds",
            "Close eyes and relax for 5 seconds",
            "Blink rapidly again for 5 seconds",
            "Helps refresh tear film",
        ]
    },
]

# Standing stretches with clear step-by-step instructions
STRETCHES = [
    # === NECK STRETCHES ===
    {
        "name": "Neck Half-Rolls",
        "duration": "1 minute",
        "steps": [
            "Stand straight, relax your shoulders",
            "Drop chin to chest gently",
            "Roll head to right ear, then back to chest",
            "Roll head to left ear, then back to chest",
            "Do 5 half-circles each direction (avoid rolling back)",
        ]
    },
    {
        "name": "Neck Side Stretch",
        "duration": "30 seconds",
        "steps": [
            "Stand tall with shoulders relaxed",
            "Tilt your right ear toward right shoulder",
            "Use right hand to gently press head further",
            "Hold for 15 seconds, feel the stretch",
            "Switch to the left side and repeat",
        ]
    },
    {
        "name": "Chin Tucks",
        "duration": "30 seconds",
        "steps": [
            "Stand with your back against a wall",
            "Pull your chin straight back (make a double chin)",
            "Keep your eyes level, don't tilt head",
            "Hold for 5 seconds",
            "Release and repeat 10 times",
        ]
    },
    {
        "name": "Neck Rotation",
        "duration": "30 seconds",
        "steps": [
            "Stand tall, face forward",
            "Slowly turn head to look over right shoulder",
            "Hold for 5 seconds",
            "Return to center, then look left",
            "Repeat 5 times each side",
        ]
    },
    {
        "name": "Forward Neck Stretch",
        "duration": "20 seconds",
        "steps": [
            "Stand with good posture",
            "Interlace fingers behind your head",
            "Gently pull chin toward chest",
            "Feel the stretch in the back of your neck",
            "Hold for 20 seconds, breathe slowly",
        ]
    },
    # === SHOULDER STRETCHES ===
    {
        "name": "Shoulder Rolls",
        "duration": "1 minute",
        "steps": [
            "Stand relaxed with arms at your sides",
            "Raise shoulders up toward your ears",
            "Roll them backward in large circles",
            "Do 10 backward rolls",
            "Then 10 forward rolls",
        ]
    },
    {
        "name": "Shoulder Shrugs",
        "duration": "30 seconds",
        "steps": [
            "Stand relaxed, arms at sides",
            "Raise shoulders up to your ears",
            "Hold for 5 seconds",
            "Release and let them drop",
            "Repeat 10 times",
        ]
    },
    {
        "name": "Cross-Body Arm Stretch",
        "duration": "30 seconds",
        "steps": [
            "Extend right arm across your chest",
            "Use left hand to press it closer",
            "Hold for 15 seconds",
            "Switch arms",
            "Hold left arm for 15 seconds",
        ]
    },
    {
        "name": "Chest Opener",
        "duration": "15 seconds",
        "steps": [
            "Stand tall with good posture",
            "Clasp hands behind your back",
            "Squeeze shoulder blades together",
            "Lift arms slightly while squeezing",
            "Hold 15 seconds, breathe deeply",
        ]
    },
    # === BODY STRETCHES ===
    {
        "name": "Reach for the Ceiling",
        "duration": "10 seconds",
        "steps": [
            "Stand tall with feet shoulder-width apart",
            "Raise both arms straight overhead",
            "Interlace your fingers, palms facing up",
            "Push upward and feel the stretch",
            "Hold for 10 seconds, breathe deeply",
        ]
    },
    {
        "name": "Standing Toe Touch",
        "duration": "15 seconds",
        "steps": [
            "Stand with feet hip-width apart",
            "Bend forward slowly from hips",
            "Reach toward shins or toes",
            "Keep knees soft, stop if back hurts",
            "Hold 15 seconds, breathe",
        ]
    },
    {
        "name": "Torso Twist",
        "duration": "30 seconds",
        "steps": [
            "Stand with feet shoulder-width apart",
            "Place hands on hips",
            "Twist upper body to the left",
            "Hold 3 seconds, return to center",
            "Twist right. Repeat 10 times each side",
        ]
    },
    {
        "name": "Side Bends",
        "duration": "30 seconds",
        "steps": [
            "Stand with feet shoulder-width apart",
            "Raise right arm overhead",
            "Lean slowly to the left",
            "Hold 10 seconds, feel the stretch",
            "Switch sides and repeat",
        ]
    },
    # === ARM/WRIST STRETCHES ===
    {
        "name": "Wrist Circles",
        "duration": "30 seconds",
        "steps": [
            "Extend both arms in front of you",
            "Make fists with both hands",
            "Rotate wrists in circles",
            "10 circles clockwise",
            "10 circles counter-clockwise",
        ]
    },
    {
        "name": "Arm Circles",
        "duration": "30 seconds",
        "steps": [
            "Stand with feet shoulder-width apart",
            "Extend arms straight out to sides",
            "Make small circles, gradually larger",
            "10 circles forward",
            "10 circles backward",
        ]
    },
    {
        "name": "Wrist Flexor Stretch",
        "duration": "30 seconds",
        "steps": [
            "Extend right arm, palm facing up",
            "Use left hand to pull fingers down",
            "Hold 15 seconds, feel forearm stretch",
            "Switch hands and repeat",
            "Great for typing strain relief",
        ]
    },
    # === LEG/BALANCE STRETCHES ===
    {
        "name": "One Leg Balance",
        "duration": "1 minute",
        "steps": [
            "Stand near a wall for support if needed",
            "Lift your right foot off the ground",
            "Balance on left leg for 30 seconds",
            "Switch legs",
            "Balance on right leg for 30 seconds",
        ]
    },
    {
        "name": "Calf Raises",
        "duration": "30 seconds",
        "steps": [
            "Stand with feet hip-width apart",
            "Rise up onto your toes",
            "Hold for 2 seconds at the top",
            "Lower heels back down slowly",
            "Repeat 15 times",
        ]
    },
    {
        "name": "March in Place",
        "duration": "1-2 minutes",
        "steps": [
            "Stand with feet together",
            "Lift right knee up high",
            "Lower it, lift left knee",
            "Swing arms naturally as you march",
            "Continue for 1-2 minutes",
        ]
    },
    {
        "name": "Standing Quad Stretch",
        "duration": "30 seconds",
        "steps": [
            "Stand near wall for balance",
            "Grab right ankle behind you",
            "Pull heel toward buttock",
            "Keep knees together, hold 15 sec",
            "Switch legs and repeat",
        ]
    },
    {
        "name": "Standing Hip Flexor Stretch",
        "duration": "30 seconds",
        "steps": [
            "Take a big step forward with right foot",
            "Lower into a shallow lunge",
            "Tuck tailbone, feel front of left hip stretch",
            "Hold 15 seconds",
            "Switch legs and repeat",
        ]
    },
]

THEMES = {
    "light": {
        "bg": "#f0f4f8",
        "fg": "#1a202c",
        "accent": "#4299e1",
        "accent_hover": "#3182ce",
        "card_bg": "#ffffff",
        "success": "#48bb78",
        "warning": "#ed8936",
        "step_bg": "#f7fafc",
        "step_num": "#4299e1",
    },
    "dark": {
        "bg": "#1a202c",
        "fg": "#e2e8f0",
        "accent": "#63b3ed",
        "accent_hover": "#4299e1",
        "card_bg": "#2d3748",
        "success": "#68d391",
        "warning": "#f6ad55",
        "step_bg": "#374151",
        "step_num": "#63b3ed",
    }
}


class StretchTimerApp:
    """
    Main application class for the Stretch Timer.

    This class manages the entire application lifecycle including:
    - Creating and managing the tkinter GUI
    - Running the countdown timer in a background thread
    - Displaying stretch reminders with popup windows
    - Managing user settings and theme preferences
    - Handling quiet hours functionality

    Attributes:
        root (tk.Tk): The main tkinter window.
        interval_minutes (tk.IntVar): Reminder interval in minutes.
        running (bool): Whether the timer is currently running.
        paused (bool): Whether the timer is paused.
        stretch_count (int): Number of stretches completed this session.
        theme (str): Current theme ('light' or 'dark').
        colors (dict): Current color palette from THEMES.
    """

    def __init__(self):
        """Initialize the application, create UI, and load settings."""
        self.root = tk.Tk()
        self.root.title("Stretch Reminder Timer")
        self.root.geometry("480x860")
        self.root.resizable(False, False)

        # Timer state
        self.interval_minutes = tk.IntVar(value=45)
        self.running = False
        self.paused = False
        self.stretch_count = 0
        self.start_time = None
        self.remaining_seconds = 0
        self.timer_thread = None
        self.theme = "light"
        self.colors = THEMES[self.theme]
        self.current_stretch = None
        self.current_secondary_exercise = None
        # Alternates between "eye" and "breathing" (start with breathing so first shown is eye)
        self.last_secondary_type = "breathing"

        # Quiet hours
        self.quiet_enabled = tk.BooleanVar(value=False)
        self.quiet_start = tk.StringVar(value="18:00")
        self.quiet_end = tk.StringVar(value="08:00")

        # Popup settings
        self.popup_timeout_seconds = tk.IntVar(value=180)
        self.popup_persistent = tk.BooleanVar(value=False)

        # Sound settings
        self.sound_enabled = tk.BooleanVar(value=True)

        # Custom message
        self.custom_message = tk.StringVar(value="Time to Stretch!")

        # Load saved settings
        self.load_settings()

        self.setup_ui()
        self.apply_theme()

        # Initialize persistent popup state (grey out timeout if needed)
        self.toggle_persistent_popup(save=False)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Click anywhere to clear focus from entry/spinbox widgets
        self.root.bind("<Button-1>", self.clear_focus)

    def clear_focus(self, event):
        """Clear focus from entry widgets when clicking elsewhere."""
        # Only clear focus if clicking on a non-entry widget
        widget = event.widget
        if not isinstance(widget, (tk.Entry, tk.Spinbox)):
            self.root.focus_set()

    def setup_ui(self):
        """Create the user interface."""
        # Main container
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header
        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 8))

        self.title_label = tk.Label(
            self.header_frame,
            text="Stretch Timer",
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        self.theme_btn = tk.Button(
            self.header_frame,
            text="Dark",
            font=("Segoe UI", 9),
            command=self.toggle_theme,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.theme_btn.pack(side=tk.RIGHT)

        # Timer display card
        self.timer_card = tk.Frame(self.main_frame, relief=tk.FLAT)
        self.timer_card.pack(fill=tk.X, pady=(0, 8))

        self.timer_label = tk.Label(
            self.timer_card,
            text="30:00",
            font=("Segoe UI", 36, "bold")
        )
        self.timer_label.pack(pady=6)

        self.status_label = tk.Label(
            self.timer_card,
            text="Ready to start",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(pady=(0, 6))

        # Control buttons
        self.btn_frame = tk.Frame(self.timer_card)
        self.btn_frame.pack(pady=(0, 8))

        self.start_btn = tk.Button(
            self.btn_frame,
            text="Start",
            font=("Segoe UI", 9, "bold"),
            width=8,
            command=self.toggle_timer,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=3)

        self.pause_btn = tk.Button(
            self.btn_frame,
            text="Pause",
            font=("Segoe UI", 9),
            width=8,
            command=self.toggle_pause,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.pause_btn.pack(side=tk.LEFT, padx=3)

        self.stretch_now_btn = tk.Button(
            self.btn_frame,
            text="Now",
            font=("Segoe UI", 9),
            width=6,
            command=self.trigger_stretch,
            cursor="hand2"
        )
        self.stretch_now_btn.pack(side=tk.LEFT, padx=3)

        # Settings section
        self.settings_frame = tk.LabelFrame(
            self.main_frame,
            text=" Settings ",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=6
        )
        self.settings_frame.pack(fill=tk.X, pady=(0, 6))

        # Interval setting
        interval_frame = tk.Frame(self.settings_frame)
        interval_frame.pack(fill=tk.X, pady=1)

        tk.Label(
            interval_frame,
            text="Interval (minutes):",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)

        self.interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=1,
            to=120,
            textvariable=self.interval_minutes,
            width=5,
            font=("Segoe UI", 9),
            command=self.update_interval,
            relief=tk.FLAT,
            buttonbackground="#e0e0e0"
        )
        self.interval_spinbox.pack(side=tk.RIGHT)
        self.interval_spinbox.bind("<Return>", lambda e: self.root.focus_set())
        self.interval_spinbox.bind("<FocusOut>", lambda e: self.update_interval())

        # Quiet hours
        quiet_frame = tk.Frame(self.settings_frame)
        quiet_frame.pack(fill=tk.X, pady=1)

        self.quiet_check = tk.Checkbutton(
            quiet_frame,
            text="Quiet hours:",
            variable=self.quiet_enabled,
            font=("Segoe UI", 9)
        )
        self.quiet_check.pack(side=tk.LEFT)

        quiet_times = tk.Frame(quiet_frame)
        quiet_times.pack(side=tk.RIGHT)

        self.quiet_start_entry = tk.Entry(
            quiet_times,
            textvariable=self.quiet_start,
            width=5,
            font=("Segoe UI", 9),
            justify=tk.CENTER
        )
        self.quiet_start_entry.pack(side=tk.LEFT)
        self.quiet_start_entry.bind("<Return>", lambda e: self.root.focus_set())
        self.quiet_start_entry.bind("<FocusOut>", lambda e: self.save_settings())

        tk.Label(quiet_times, text=" to ", font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.quiet_end_entry = tk.Entry(
            quiet_times,
            textvariable=self.quiet_end,
            width=5,
            font=("Segoe UI", 9),
            justify=tk.CENTER
        )
        self.quiet_end_entry.pack(side=tk.LEFT)
        self.quiet_end_entry.bind("<Return>", lambda e: self.root.focus_set())
        self.quiet_end_entry.bind("<FocusOut>", lambda e: self.save_settings())

        # Popup timeout setting
        popup_timeout_frame = tk.Frame(self.settings_frame)
        popup_timeout_frame.pack(fill=tk.X, pady=1)

        self.popup_timeout_label = tk.Label(
            popup_timeout_frame,
            text="Popup timeout (seconds):",
            font=("Segoe UI", 9)
        )
        self.popup_timeout_label.pack(side=tk.LEFT)

        self.popup_timeout_spinbox = tk.Spinbox(
            popup_timeout_frame,
            from_=10,
            to=300,
            textvariable=self.popup_timeout_seconds,
            width=5,
            font=("Segoe UI", 9),
            command=self.save_settings,
            relief=tk.FLAT,
            buttonbackground="#e0e0e0"
        )
        self.popup_timeout_spinbox.pack(side=tk.RIGHT)
        self.popup_timeout_spinbox.bind("<Return>", lambda e: self.root.focus_set())
        self.popup_timeout_spinbox.bind("<FocusOut>", lambda e: self.save_settings())

        # Persistent popup checkbox
        persistent_frame = tk.Frame(self.settings_frame)
        persistent_frame.pack(fill=tk.X, pady=1)

        self.persistent_check = tk.Checkbutton(
            persistent_frame,
            text="Persistent popup (no auto-close)",
            variable=self.popup_persistent,
            font=("Segoe UI", 9),
            command=self.toggle_persistent_popup
        )
        self.persistent_check.pack(side=tk.LEFT)

        # Sound notification toggle
        sound_frame = tk.Frame(self.settings_frame)
        sound_frame.pack(fill=tk.X, pady=1)

        self.sound_check = tk.Checkbutton(
            sound_frame,
            text="Play sound on reminder",
            variable=self.sound_enabled,
            font=("Segoe UI", 9),
            command=self.save_settings
        )
        self.sound_check.pack(side=tk.LEFT)

        # Stats section
        self.stats_frame = tk.LabelFrame(
            self.main_frame,
            text=" Stats ",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=6
        )
        self.stats_frame.pack(fill=tk.X, pady=(0, 6))

        stats_grid = tk.Frame(self.stats_frame)
        stats_grid.pack(fill=tk.X)

        # Stretch count
        count_frame = tk.Frame(stats_grid)
        count_frame.pack(side=tk.LEFT, expand=True)

        self.count_value = tk.Label(
            count_frame,
            text="0",
            font=("Segoe UI", 18, "bold")
        )
        self.count_value.pack()

        tk.Label(
            count_frame,
            text="Stretches",
            font=("Segoe UI", 9)
        ).pack()

        # Session duration
        duration_frame = tk.Frame(stats_grid)
        duration_frame.pack(side=tk.LEFT, expand=True)

        self.duration_value = tk.Label(
            duration_frame,
            text="0:00",
            font=("Segoe UI", 18, "bold")
        )
        self.duration_value.pack()

        tk.Label(
            duration_frame,
            text="Duration",
            font=("Segoe UI", 9)
        ).pack()

        # Current stretch section
        self.suggestion_frame = tk.LabelFrame(
            self.main_frame,
            text=" Current Stretch ",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=8
        )
        self.suggestion_frame.pack(fill=tk.BOTH, expand=True)

        # Stretch name and duration header
        self.stretch_header = tk.Frame(self.suggestion_frame)
        self.stretch_header.pack(fill=tk.X, pady=(0, 8))

        self.stretch_name_label = tk.Label(
            self.stretch_header,
            text="Ready!",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        self.stretch_name_label.pack(side=tk.LEFT)

        self.stretch_duration_label = tk.Label(
            self.stretch_header,
            text="",
            font=("Segoe UI", 9),
            anchor="e"
        )
        self.stretch_duration_label.pack(side=tk.RIGHT)

        # Steps container
        self.steps_frame = tk.Frame(self.suggestion_frame)
        self.steps_frame.pack(fill=tk.BOTH, expand=True)

        # Initial message
        self.initial_label = tk.Label(
            self.steps_frame,
            text="Click 'Start' to begin.\n\nStretch reminders will appear here\nwith step-by-step instructions.",
            font=("Segoe UI", 10),
            justify=tk.CENTER
        )
        self.initial_label.pack(expand=True)

        # Step labels (created dynamically)
        self.step_labels = []

    def create_step_labels(self, steps):
        """
        Create labels for each step of an exercise.

        Args:
            steps (list): List of step description strings.
        """
        # Clear existing labels
        for label in self.step_labels:
            label.destroy()
        self.step_labels = []

        # Hide initial message
        self.initial_label.pack_forget()

        c = self.colors

        for i, step in enumerate(steps, 1):
            step_frame = tk.Frame(self.steps_frame, bg=c["step_bg"], pady=4, padx=8)
            step_frame.pack(fill=tk.X, pady=2)

            # Step number
            num_label = tk.Label(
                step_frame,
                text=f"{i}.",
                font=("Segoe UI", 10, "bold"),
                fg=c["step_num"],
                bg=c["step_bg"],
                width=2,
                anchor="e"
            )
            num_label.pack(side=tk.LEFT, padx=(0, 8))

            # Step text
            text_label = tk.Label(
                step_frame,
                text=step,
                font=("Segoe UI", 10),
                fg=c["fg"],
                bg=c["step_bg"],
                anchor="w"
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.step_labels.append(step_frame)

    def apply_theme(self):
        """
        Apply the current color theme to all widgets.

        Updates colors for all frames, labels, buttons, and other widgets
        based on the current theme (light or dark).
        """
        c = self.colors

        self.root.configure(bg=c["bg"])
        self.main_frame.configure(bg=c["bg"])
        self.header_frame.configure(bg=c["bg"])
        self.title_label.configure(bg=c["bg"], fg=c["fg"])
        self.theme_btn.configure(
            bg=c["bg"],
            fg=c["fg"],
            activebackground=c["card_bg"],
            text="Light" if self.theme == "dark" else "Dark"
        )

        self.timer_card.configure(bg=c["card_bg"])
        self.timer_label.configure(bg=c["card_bg"], fg=c["accent"])
        self.status_label.configure(bg=c["card_bg"], fg=c["fg"])
        self.btn_frame.configure(bg=c["card_bg"])

        # Buttons
        for btn in [self.start_btn, self.pause_btn, self.stretch_now_btn]:
            btn.configure(
                bg=c["accent"],
                fg="white",
                activebackground=c["accent_hover"],
                activeforeground="white",
                relief=tk.FLAT
            )

        # Settings
        self.settings_frame.configure(bg=c["card_bg"], fg=c["fg"])
        for widget in self.settings_frame.winfo_children():
            self.style_widget_recursive(widget, c)

        # Stats
        self.stats_frame.configure(bg=c["card_bg"], fg=c["fg"])
        for widget in self.stats_frame.winfo_children():
            self.style_widget_recursive(widget, c)
        self.count_value.configure(fg=c["success"])
        self.duration_value.configure(fg=c["accent"])

        # Suggestion frame
        self.suggestion_frame.configure(bg=c["card_bg"], fg=c["fg"])
        self.stretch_header.configure(bg=c["card_bg"])
        self.stretch_name_label.configure(bg=c["card_bg"], fg=c["accent"])

        # Style Spinbox widgets for the current theme
        spinbox_bg = c["bg"]
        spinbox_fg = c["fg"]
        spinbox_btn_bg = c["card_bg"] if self.theme == "light" else "#4a5568"
        for spinbox in [self.interval_spinbox, self.popup_timeout_spinbox]:
            spinbox.configure(
                bg=spinbox_bg,
                fg=spinbox_fg,
                insertbackground=spinbox_fg,
                buttonbackground=spinbox_btn_bg
            )
        self.stretch_duration_label.configure(bg=c["card_bg"], fg=c["accent"])
        self.steps_frame.configure(bg=c["card_bg"])
        self.initial_label.configure(bg=c["card_bg"], fg=c["fg"])

        # Update step labels if they exist
        for step_frame in self.step_labels:
            step_frame.configure(bg=c["step_bg"])
            for child in step_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=c["step_bg"])
                    # Check if it's the number label (has width=2)
                    if child.cget("width") == 2:
                        child.configure(fg=c["step_num"])
                    else:
                        child.configure(fg=c["fg"])

        # Update popup timeout label based on persistent setting
        if self.popup_persistent.get():
            self.popup_timeout_label.configure(fg="gray")
        else:
            self.popup_timeout_label.configure(fg=c["fg"])

    def style_widget_recursive(self, widget, c):
        """
        Recursively apply theme colors to a widget and its children.

        Args:
            widget: The tkinter widget to style.
            c (dict): Color dictionary from THEMES.
        """
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=c["card_bg"])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=c["card_bg"], fg=c["fg"])
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(
                    bg=c["card_bg"],
                    fg=c["fg"],
                    activebackground=c["card_bg"],
                    selectcolor=c["bg"]
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=c["bg"], fg=c["fg"], insertbackground=c["fg"])
            elif isinstance(widget, tk.Spinbox):
                spinbox_btn_bg = c["card_bg"] if self.theme == "light" else "#4a5568"
                widget.configure(bg=c["bg"], fg=c["fg"], insertbackground=c["fg"], buttonbackground=spinbox_btn_bg)
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self.style_widget_recursive(child, c)

    def toggle_theme(self):
        """Switch between light and dark theme."""
        self.theme = "dark" if self.theme == "light" else "light"
        self.colors = THEMES[self.theme]
        self.apply_theme()
        self.save_settings()
        # Recreate step labels with new theme if a stretch is displayed
        if self.current_stretch and self.current_secondary_exercise:
            self.create_combined_step_labels(
                self.current_stretch,
                self.current_secondary_exercise,
                self.last_secondary_type
            )

    def toggle_timer(self):
        """Start or stop the timer."""
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        """Start the countdown timer."""
        self.running = True
        self.paused = False
        self.stretch_count = 0
        self.start_time = datetime.now()
        self.remaining_seconds = self.interval_minutes.get() * 60

        self.start_btn.configure(text="Stop")
        self.pause_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="Timer running...")

        self.update_stats()
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Stop the timer."""
        self.running = False
        self.paused = False

        self.start_btn.configure(text="Start")
        self.pause_btn.configure(state=tk.DISABLED, text="Pause")
        self.status_label.configure(text="Timer stopped")
        self.timer_label.configure(text=f"{self.interval_minutes.get():02d}:00")

    def toggle_pause(self):
        """Pause or resume the timer."""
        self.paused = not self.paused

        if self.paused:
            self.pause_btn.configure(text="Resume")
            self.status_label.configure(text="Paused")
        else:
            self.pause_btn.configure(text="Pause")
            self.status_label.configure(text="Timer running...")

    def timer_loop(self):
        """
        Main timer loop running in a background thread.

        Decrements the remaining time each second and triggers a stretch
        when the countdown reaches zero (unless in quiet hours).
        Uses root.after() for thread-safe UI updates.
        """
        while self.running:
            if not self.paused:
                if self.remaining_seconds <= 0:
                    if not self.is_quiet_hours():
                        self.root.after(0, self.trigger_stretch)
                    self.remaining_seconds = self.interval_minutes.get() * 60
                else:
                    self.remaining_seconds -= 1

                # Update display
                mins, secs = divmod(self.remaining_seconds, 60)
                self.root.after(0, lambda m=mins, s=secs: self.timer_label.configure(
                    text=f"{m:02d}:{s:02d}"
                ))

            # Update session duration
            self.root.after(0, self.update_stats)
            time.sleep(1)

    def is_quiet_hours(self):
        """
        Check if current time is within quiet hours.

        Returns:
            bool: True if notifications should be suppressed, False otherwise.

        Note:
            Handles overnight quiet hours (e.g., 22:00 to 06:00) correctly.
        """
        if not self.quiet_enabled.get():
            return False

        try:
            now = datetime.now().time()
            start = datetime.strptime(self.quiet_start.get(), "%H:%M").time()
            end = datetime.strptime(self.quiet_end.get(), "%H:%M").time()

            if start <= end:
                return start <= now <= end
            else:
                return now >= start or now <= end
        except ValueError:
            return False

    def trigger_stretch(self):
        """
        Trigger a stretch reminder.

        Selects a random stretch and alternates between eye/breathing exercises.
        Updates the UI, plays a sound, shows a desktop notification, and
        displays the popup window.
        """
        self.stretch_count += 1
        stretch = random.choice(STRETCHES)

        # Alternate between eye and breathing exercises
        if self.last_secondary_type == "breathing":
            secondary_exercise = random.choice(EYE_EXERCISES)
            secondary_type = "eye"
        else:
            secondary_exercise = random.choice(BREATHING_EXERCISES)
            secondary_type = "breathing"

        self.last_secondary_type = secondary_type
        self.current_stretch = stretch
        self.current_secondary_exercise = secondary_exercise

        # Update UI - show both exercises
        self.count_value.configure(text=str(self.stretch_count))
        self.stretch_name_label.configure(text=f"🧘 {stretch['name']}")
        self.stretch_duration_label.configure(text=stretch["duration"])

        # Create step labels for main stretch + secondary exercise
        self.create_combined_step_labels(stretch, secondary_exercise, secondary_type)

        # Play sound (if enabled)
        if self.sound_enabled.get():
            play_notification_sound(self.root)

        # Desktop notification
        if HAS_PLYER:
            try:
                if secondary_type == "eye":
                    secondary_label = "Eye Break"
                else:
                    secondary_label = "Breathing"
                title = f"{self.custom_message.get()} - {stretch['name']}"
                message = f"+ {secondary_label}: {secondary_exercise['name']}"
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Stretch Timer",
                    timeout=10
                )
            except Exception:
                pass

        # Show popup
        self.show_stretch_popup(stretch, secondary_exercise, secondary_type)

        # Reset timer
        self.remaining_seconds = self.interval_minutes.get() * 60

    def create_combined_step_labels(self, stretch, secondary_exercise,
                                       secondary_type="eye"):
        """
        Create labels for stretch steps combined with a secondary exercise.

        Displays the main stretch with blue bullets, followed by the secondary
        exercise (eye or breathing) with green bullets and header.

        Args:
            stretch (dict): The main stretch with 'name', 'duration', 'steps'.
            secondary_exercise (dict): Eye or breathing exercise dict.
            secondary_type (str): Either 'eye' or 'breathing'.
        """
        # Clear existing labels
        for label in self.step_labels:
            label.destroy()
        self.step_labels = []

        # Hide initial message
        self.initial_label.pack_forget()

        c = self.colors

        # Determine header prefix - both eye and breathing use green
        if secondary_type == "eye":
            header_prefix = "👁 Eye Break"
        else:
            header_prefix = "🫁 Breathing"
        secondary_color = c["success"]  # Green for both eye and breathing

        # Main stretch steps (blue bullets)
        for step in stretch["steps"]:
            step_frame = tk.Frame(self.steps_frame, bg=c["step_bg"], pady=3, padx=8)
            step_frame.pack(fill=tk.X, pady=1)

            bullet_label = tk.Label(
                step_frame,
                text="•",
                font=("Segoe UI", 9, "bold"),
                fg=c["step_num"],
                bg=c["step_bg"],
                width=2,
                anchor="e"
            )
            bullet_label.pack(side=tk.LEFT, padx=(0, 6))

            text_label = tk.Label(
                step_frame,
                text=step,
                font=("Segoe UI", 9),
                fg=c["fg"],
                bg=c["step_bg"],
                anchor="w"
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.step_labels.append(step_frame)

        # Separator and secondary exercise header
        secondary_header = tk.Frame(self.steps_frame, bg=c["card_bg"], pady=4)
        secondary_header.pack(fill=tk.X, pady=(6, 2))

        tk.Label(
            secondary_header,
            text=f"{header_prefix}: {secondary_exercise['name']}",
            font=("Segoe UI", 9, "bold"),
            fg=secondary_color,
            bg=c["card_bg"],
            anchor="w"
        ).pack(side=tk.LEFT)

        tk.Label(
            secondary_header,
            text=secondary_exercise["duration"],
            font=("Segoe UI", 8),
            fg=secondary_color,
            bg=c["card_bg"],
            anchor="e"
        ).pack(side=tk.RIGHT)

        self.step_labels.append(secondary_header)

        # Secondary exercise steps (green bullets)
        for step in secondary_exercise["steps"]:
            step_frame = tk.Frame(self.steps_frame, bg=c["step_bg"], pady=2, padx=8)
            step_frame.pack(fill=tk.X, pady=1)

            bullet_label = tk.Label(
                step_frame,
                text="•",
                font=("Segoe UI", 9),
                fg=secondary_color,
                bg=c["step_bg"],
                width=2,
                anchor="e"
            )
            bullet_label.pack(side=tk.LEFT, padx=(0, 6))

            text_label = tk.Label(
                step_frame,
                text=step,
                font=("Segoe UI", 9),
                fg=c["fg"],
                bg=c["step_bg"],
                anchor="w"
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.step_labels.append(step_frame)

    def show_stretch_popup(self, stretch, secondary_exercise,
                            secondary_type="eye"):
        """
        Show a popup window with the stretch and secondary exercise.

        Creates a topmost window displaying the stretch instructions and
        secondary exercise. Auto-closes after timeout unless persistent
        mode is enabled.

        Args:
            stretch (dict): The main stretch with 'name', 'duration', 'steps'.
            secondary_exercise (dict): Eye or breathing exercise dict.
            secondary_type (str): Either 'eye' or 'breathing'.
        """
        popup = tk.Toplevel(self.root)
        popup.title("Time to Stretch!")
        popup.geometry("450x600")
        popup.configure(bg=self.colors["card_bg"])
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        # Center on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - 450) // 2
        y = (popup.winfo_screenheight() - 600) // 2
        popup.geometry(f"+{x}+{y}")

        c = self.colors

        # Determine header prefix - both eye and breathing use green
        if secondary_type == "eye":
            header_prefix = "👁 Eye Break"
        else:
            header_prefix = "🫁 Breathing"
        secondary_color = c["success"]  # Green for both eye and breathing

        # Title
        tk.Label(
            popup,
            text=self.custom_message.get(),
            font=("Segoe UI", 14, "bold"),
            bg=c["card_bg"],
            fg=c["accent"]
        ).pack(pady=(12, 5))

        # Main content frame
        content_frame = tk.Frame(popup, bg=c["card_bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        # === MAIN STRETCH (blue heading with yoga icon) ===
        stretch_header = tk.Frame(content_frame, bg=c["card_bg"])
        stretch_header.pack(fill=tk.X, pady=(5, 8))

        tk.Label(
            stretch_header,
            text=f"🧘 {stretch['name']}",
            font=("Segoe UI", 13, "bold"),
            bg=c["card_bg"],
            fg=c["accent"]
        ).pack(side=tk.LEFT)

        tk.Label(
            stretch_header,
            text=stretch["duration"],
            font=("Segoe UI", 9),
            bg=c["card_bg"],
            fg=c["accent"]
        ).pack(side=tk.RIGHT)

        # Stretch steps (blue bullets)
        for step in stretch["steps"]:
            step_frame = tk.Frame(content_frame, bg=c["step_bg"], pady=4, padx=8)
            step_frame.pack(fill=tk.X, pady=2)

            tk.Label(
                step_frame,
                text="•",
                font=("Segoe UI", 10, "bold"),
                fg=c["step_num"],
                bg=c["step_bg"],
                width=2,
                anchor="e"
            ).pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(
                step_frame,
                text=step,
                font=("Segoe UI", 10),
                fg=c["fg"],
                bg=c["step_bg"],
                anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # === SECONDARY EXERCISE (Eye or Breathing) ===
        secondary_header = tk.Frame(content_frame, bg=c["card_bg"])
        secondary_header.pack(fill=tk.X, pady=(12, 6))

        tk.Label(
            secondary_header,
            text=f"{header_prefix}: {secondary_exercise['name']}",
            font=("Segoe UI", 11, "bold"),
            bg=c["card_bg"],
            fg=secondary_color
        ).pack(side=tk.LEFT)

        tk.Label(
            secondary_header,
            text=secondary_exercise["duration"],
            font=("Segoe UI", 9),
            bg=c["card_bg"],
            fg=secondary_color
        ).pack(side=tk.RIGHT)

        # Secondary exercise steps (green bullets)
        for step in secondary_exercise["steps"]:
            step_frame = tk.Frame(content_frame, bg=c["step_bg"], pady=4, padx=8)
            step_frame.pack(fill=tk.X, pady=2)

            tk.Label(
                step_frame,
                text="•",
                font=("Segoe UI", 10),
                fg=secondary_color,
                bg=c["step_bg"],
                width=2,
                anchor="e"
            ).pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(
                step_frame,
                text=step,
                font=("Segoe UI", 10),
                fg=c["fg"],
                bg=c["step_bg"],
                anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Stretch count
        tk.Label(
            popup,
            text=f"Stretch #{self.stretch_count}",
            font=("Segoe UI", 9),
            bg=c["card_bg"],
            fg=c["fg"]
        ).pack(pady=(8, 5))

        # Done button
        tk.Button(
            popup,
            text="Done!",
            font=("Segoe UI", 11, "bold"),
            bg=c["success"],
            fg="white",
            relief=tk.FLAT,
            width=12,
            command=popup.destroy,
            cursor="hand2"
        ).pack(pady=(5, 12))

        # Auto-close after timeout (unless persistent mode is enabled)
        if not self.popup_persistent.get():
            timeout_ms = self.popup_timeout_seconds.get() * 1000
            popup.after(timeout_ms, lambda: popup.destroy() if popup.winfo_exists() else None)

    def update_stats(self):
        """Update session statistics display."""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                duration_text = f"{hours}:{minutes:02d}"
            else:
                duration_text = f"{minutes}:{seconds:02d}"

            self.duration_value.configure(text=duration_text)

    def update_interval(self):
        """Update the timer display when interval changes."""
        if not self.running:
            self.timer_label.configure(text=f"{self.interval_minutes.get():02d}:00")
        self.save_settings()

    def toggle_persistent_popup(self, save=True):
        """
        Toggle persistent popup mode and update UI accordingly.

        When persistent mode is enabled, the timeout spinbox is disabled
        and greyed out since the popup won't auto-close.

        Args:
            save (bool): Whether to save settings after toggling.
        """
        if self.popup_persistent.get():
            # Disable timeout spinbox when persistent is checked
            self.popup_timeout_spinbox.configure(state=tk.DISABLED)
            self.popup_timeout_label.configure(fg="gray")
        else:
            # Enable timeout spinbox when persistent is unchecked
            self.popup_timeout_spinbox.configure(state=tk.NORMAL)
            c = self.colors
            self.popup_timeout_label.configure(fg=c["fg"])
        if save:
            self.save_settings()

    def on_close(self):
        """Handle window close."""
        self.running = False
        self.save_settings()
        self.root.destroy()

    def load_settings(self):
        """
        Load settings from JSON file.

        Reads settings from SETTINGS_FILE and applies them to the
        application state. Uses default values if file doesn't exist
        or is corrupted.
        """
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)

                # Apply loaded settings
                if "interval_minutes" in settings:
                    self.interval_minutes.set(settings["interval_minutes"])
                if "quiet_enabled" in settings:
                    self.quiet_enabled.set(settings["quiet_enabled"])
                if "quiet_start" in settings:
                    self.quiet_start.set(settings["quiet_start"])
                if "quiet_end" in settings:
                    self.quiet_end.set(settings["quiet_end"])
                if "theme" in settings:
                    self.theme = settings["theme"]
                    self.colors = THEMES[self.theme]
                if "custom_message" in settings:
                    self.custom_message.set(settings["custom_message"])
                if "popup_timeout_seconds" in settings:
                    self.popup_timeout_seconds.set(settings["popup_timeout_seconds"])
                if "popup_persistent" in settings:
                    self.popup_persistent.set(settings["popup_persistent"])
                if "sound_enabled" in settings:
                    self.sound_enabled.set(settings["sound_enabled"])
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, use defaults
            pass

    def save_settings(self):
        """
        Save current settings to JSON file.

        Writes all user preferences to SETTINGS_FILE for persistence
        across sessions. Silently fails if unable to write.
        """
        settings = {
            "interval_minutes": self.interval_minutes.get(),
            "quiet_enabled": self.quiet_enabled.get(),
            "quiet_start": self.quiet_start.get(),
            "quiet_end": self.quiet_end.get(),
            "theme": self.theme,
            "custom_message": self.custom_message.get(),
            "popup_timeout_seconds": self.popup_timeout_seconds.get(),
            "popup_persistent": self.popup_persistent.get(),
            "sound_enabled": self.sound_enabled.get(),
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)
        except IOError:
            pass  # Silently fail if unable to save

    def run(self):
        """Start the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = StretchTimerApp()
    app.run()
