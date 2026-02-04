# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A cross-platform desktop application (Windows + Linux) that reminds users to stretch at configurable intervals. Built with Python/tkinter for the GUI with plyer for desktop notifications.

## Running the Application

```bash
python stretch_timer.py
```

**Dependencies:** `pip install plyer` (optional, for desktop notifications)

## Architecture

### Main Application (`stretch_timer.py`)

- **GUI Framework:** tkinter with ttk widgets
- **Notifications:** plyer library (optional, gracefully degrades)
- **Audio:** Cross-platform - winsound on Windows, paplay/aplay on Linux, tkinter bell() fallback
- **Threading:** Background timer loop runs in separate thread, uses `root.after()` for thread-safe UI updates
- **Persistence:** JSON settings file (`stretch_timer_settings.json`) in the same directory

**Utility functions:**
- `format_duration(seconds)` - Formats duration for display
  - Input: int (seconds) or tuple (min, max) for ranges
  - Output: "30 sec", "1 min", or "1-2 min"

**Key data structures:**
- `STRETCHES` - List of 21 standing body stretches (5 steps each)
- `EYE_EXERCISES` - List of 6 eye exercises (3-4 steps each)
- `BREATHING_EXERCISES` - List of 6 breathing exercises (4 steps each)
- `THEMES` - Light/dark color dictionaries

**Exercise pairing:** Every stretch reminder shows a random body stretch AND alternates between eye exercises and breathing exercises.

## Cross-Platform Support

### Platform Detection

The application uses `sys.platform` to detect the operating system:
- `win32` - Windows
- Starts with `linux` - Linux distributions

### Audio

Audio notifications use platform-specific implementations with graceful degradation:

- **Windows:** `winsound.PlaySound()` with system sounds
- **Linux:** Subprocess calls to `paplay`, `aplay`, or `canberra-gtk-play` with freedesktop sounds
- **Fallback:** `tkinter.bell()` if platform-specific methods fail

The `sound_enabled` setting allows users to disable sound entirely via a checkbox in Settings.

### Notifications

Desktop notifications use plyer, which is cross-platform. The import uses graceful degradation:

```python
try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False
```

## Deployment

### Local Testing Scripts

| Platform | Script | Output |
|----------|--------|--------|
| Windows | `Deploy.bat` | `StretchTimer-Windows.zip` |
| Linux | `deploy.sh` | `stretch_timer-linux.tar.gz` |

### CI/CD (`.github/workflows/release.yml`)

GitHub Actions workflow that automates release builds:
- **Trigger:** When a GitHub Release is created
- **Jobs:** Two parallel jobs - `build-windows` and `build-linux`
- **Output:** `StretchTimer-Windows.zip` and `stretch_timer-linux.tar.gz` attached to the release

**IMPORTANT: Keep deployment scripts and release.yml in sync!**

The workflow replicates both `Deploy.bat` (PowerShell) and `deploy.sh` (bash) logic. When updating one, update the others:

| Change | Deploy.bat | deploy.sh | release.yml |
|--------|------------|-----------|-------------|
| Files in archive | `copy` commands | `cp` commands | `Copy-Item` / `cp` |
| Windows launcher | Heredoc Step 4 | N/A | PowerShell `@'...'@` block |
| Linux launcher | N/A | Heredoc | Bash `cat > ... << 'EOF'` |
| Windows README | Heredoc Step 4 | N/A | PowerShell `@'...'@` block |
| Linux README | N/A | Heredoc | Bash `cat > ... << 'EOF'` |

Test locally with `Deploy.bat` (Windows) or `./deploy.sh` (Linux) before pushing changes.

## Deploying to GitHub

### Creating a Release

1. **Test locally:**
   - Windows: Run `Deploy.bat`, extract ZIP, test `StretchTimer.bat`
   - Linux: Run `./deploy.sh`, extract tar.gz, test `./StretchTimer.sh`

2. **Commit and push** all changes to `master`:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin master
   ```

3. **Create a GitHub Release:**
   - Go to your repo on GitHub → Releases → "Create a new release"
   - Click "Choose a tag" → type a version (e.g., `v1.0.0`) → "Create new tag"
   - Release title: e.g., "v1.0.0 - Cross-Platform Release"
   - Description: List changes/features
   - Click "Publish release"

4. **CI/CD runs automatically:**
   - GitHub Actions builds both packages in parallel
   - `StretchTimer-Windows.zip` and `stretch_timer-linux.tar.gz` get attached to the release

5. **Verify:** Check the release page for both attached files

### Version Tags

Use semantic versioning: `vMAJOR.MINOR.PATCH`
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

### GitHub CLI

**Location:** `C:\Program Files\GitHub CLI\gh.exe`

Create releases via CLI:
```bash
"C:\Program Files\GitHub CLI\gh.exe" release create v1.0.0 --title "v1.0.0 - Release" --notes "Release notes here"
```

## Key Constraints

- All stretches must be performed **standing up**
- Secondary exercises (eye/breathing) alternate each reminder, never shown alone

## Window Sizing

The main window and popup must be tall enough to display both the body stretch (5 steps) and secondary exercise (header + 4 steps). When adjusting window sizes:

- **Main window:** `self.root.geometry("WIDTHxHEIGHT")` in `__init__` (currently 480x860)
- **Popup window:** `popup.geometry("WIDTHxHEIGHT")` in `show_stretch_popup()` (currently 450x600), also update the centering calculation below it

If adding more steps to exercises or increasing font sizes, increase the height accordingly. The popup auto-centers on screen using `winfo_screenwidth()`/`winfo_screenheight()`.
