# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Windows desktop application that reminds users to stretch at configurable intervals. Built with Python/tkinter for the GUI with plyer for desktop notifications.

## Running the Application

```bash
python stretch_timer.py
```

**Dependencies:** `pip install plyer` (optional, for desktop notifications)

## Architecture

### Main Application (`stretch_timer.py`)

- **GUI Framework:** tkinter with ttk widgets
- **Notifications:** plyer library (optional, gracefully degrades)
- **Audio:** Windows-native winsound
- **Threading:** Background timer loop runs in separate thread, uses `root.after()` for thread-safe UI updates
- **Persistence:** JSON settings file (`stretch_timer_settings.json`) in the same directory

**Key data structures:**
- `STRETCHES` - List of 21 standing body stretches (5 steps each)
- `EYE_EXERCISES` - List of 6 eye exercises (3-4 steps each)
- `BREATHING_EXERCISES` - List of 6 breathing exercises (4 steps each)
- `THEMES` - Light/dark color dictionaries

**Exercise pairing:** Every stretch reminder shows a random body stretch AND alternates between eye exercises and breathing exercises.

### Deployment (`Deploy.bat`)

Creates a distributable ZIP package locally for testing. Users need Python installed (guided to Microsoft Store if missing).

### CI/CD (`.github/workflows/release.yml`)

GitHub Actions workflow that automates release builds:
- **Trigger:** When a GitHub Release is created
- **Runs on:** `windows-latest`
- **Output:** Builds `StretchTimer.zip` and attaches it to the release

**IMPORTANT: Keep Deploy.bat and release.yml in sync!**

The workflow replicates `Deploy.bat` logic in PowerShell. These cannot share code (batch vs PowerShell), so when updating one, update the other:

| Change | Update in Deploy.bat | Update in release.yml |
|--------|---------------------|----------------------|
| Files included in ZIP | `copy` commands in Step 3 | `Copy-Item` in PowerShell |
| Launcher script content | Heredoc in Step 4 | `@'...'@` block for StretchTimer.bat |
| README.txt content | Heredoc in Step 4 | `@'...'@` block for README.txt |
| ZIP structure | `DIST_FOLDER` variable | `dist` folder creation |

Test locally with `Deploy.bat` before pushing changes that affect the release workflow.

## Key Constraints

- All stretches must be performed **standing up**
- Secondary exercises (eye/breathing) alternate each reminder, never shown alone

## Window Sizing

The main window and popup must be tall enough to display both the body stretch (5 steps) and secondary exercise (header + 4 steps). When adjusting window sizes:

- **Main window:** `self.root.geometry("WIDTHxHEIGHT")` in `__init__` (currently 480x820)
- **Popup window:** `popup.geometry("WIDTHxHEIGHT")` in `show_stretch_popup()` (currently 450x560), also update the centering calculation below it

If adding more steps to exercises or increasing font sizes, increase the height accordingly. The popup auto-centers on screen using `winfo_screenwidth()`/`winfo_screenheight()`.
