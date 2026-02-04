# Stretch Timer

A cross-platform desktop application (Windows & Linux) that reminds you to get up and stretch at regular intervals. Perfect for desk workers who want to maintain good posture and eye health.

## Features

- **21 Standing Stretches** - Neck, shoulders, back, arms, wrists, and legs
- **6 Eye Exercises** - Combat screen fatigue with the 20-20-20 rule and more
- **6 Breathing Exercises** - Box breathing, 4-7-8, and relaxation techniques
- **Configurable Intervals** - Set reminders from 1 to 120 minutes
- **Quiet Hours** - Automatically pause reminders during specified times
- **Light/Dark Themes** - Easy on the eyes
- **Desktop Notifications** - Never miss a stretch break
- **Audio Notifications** - Sound alerts with cross-platform support (can be disabled)
- **Persistent Settings** - Your preferences are saved automatically

## Screenshot

The app displays step-by-step instructions for each stretch, paired with either an eye exercise or breathing exercise (alternating).

## Requirements

### Windows
- Windows 10/11
- Python 3.10+ (from [Microsoft Store](https://apps.microsoft.com/detail/9NCVDN91XZQP) or [python.org](https://python.org))

### Linux
- Python 3.10+ with tkinter (`sudo apt install python3-tk` on Debian/Ubuntu)
- Optional: PulseAudio for sound notifications

## Quick Start

### Option 1: Run directly
```bash
pip install plyer
python stretch_timer.py  # or python3 on Linux
```

### Option 2: Use the launcher
- **Windows:** Double-click `StretchTimer.bat`
- **Linux:** Run `./StretchTimer.sh`

The launcher will check for Python, install dependencies, and launch the app.

## Download

Download from the [Releases](../../releases) page:

| Platform | File | Launcher |
|----------|------|----------|
| Windows | `StretchTimer-Windows.zip` | `StretchTimer.bat` |
| Linux | `stretch_timer-linux.tar.gz` | `StretchTimer.sh` |

1. Extract the archive
2. Run the launcher for your platform
3. Install Python if prompted

## Creating a Release (for maintainers)

Releases are automated via GitHub Actions. When you create a release, both `StretchTimer-Windows.zip` and `stretch_timer-linux.tar.gz` are built and attached automatically.

**Via GitHub web UI (easiest):**
1. Go to Releases → "Draft a new release"
2. Create a new tag (e.g., `v1.0.0`)
3. Add release notes
4. Click "Publish release"

**Via command line:**
```bash
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes here"
```

**For local testing:**
- **Windows:** Run `Deploy.bat` to create `StretchTimer-Windows.zip`
- **Linux:** Run `./deploy.sh` to create `stretch_timer-linux.tar.gz`

## Auto-Start on Login

### Windows
1. Press `Win+R`, type `shell:startup`, press Enter
2. Create a shortcut to `StretchTimer.bat`

### Linux
Create `~/.config/autostart/stretch-timer.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=Stretch Timer
Exec=/path/to/stretch_timer/StretchTimer.sh
```

## Files

| File | Description |
|------|-------------|
| `stretch_timer.py` | Main application |
| `Deploy.bat` | Creates distributable ZIP package locally (Windows) |
| `deploy.sh` | Creates distributable tar.gz package locally (Linux) |
| `Run.bat` | Quick launcher for development (Windows) |
| `.github/workflows/release.yml` | GitHub Actions workflow for automated releases |
| `CLAUDE.md` | Development notes for Claude Code |

## Dependencies

- **tkinter** - GUI framework (included with Python)
- **plyer** - Desktop notifications (optional, installed automatically)

## License

MIT License - feel free to use and modify.

---

*Created with assistance from Claude*
