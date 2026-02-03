# Stretch Timer

A Windows desktop application that reminds you to get up and stretch at regular intervals. Perfect for desk workers who want to maintain good posture and eye health.

## Features

- **21 Standing Stretches** - Neck, shoulders, back, arms, wrists, and legs
- **6 Eye Exercises** - Combat screen fatigue with the 20-20-20 rule and more
- **6 Breathing Exercises** - Box breathing, 4-7-8, and relaxation techniques
- **Configurable Intervals** - Set reminders from 1 to 120 minutes
- **Quiet Hours** - Automatically pause reminders during specified times
- **Light/Dark Themes** - Easy on the eyes
- **Desktop Notifications** - Never miss a stretch break
- **Persistent Settings** - Your preferences are saved automatically

## Screenshot

The app displays step-by-step instructions for each stretch, paired with either an eye exercise or breathing exercise (alternating).

## Requirements

- Windows 10/11
- Python 3.10+ (free from [Microsoft Store](https://apps.microsoft.com/detail/9NCVDN91XZQP) or [python.org](https://python.org))

## Quick Start

### Option 1: Run directly
```bash
pip install plyer
python stretch_timer.py
```

### Option 2: Use the launcher
Double-click `StretchTimer.bat` in the `dist` folder. It will:
- Check if Python is installed (guides you to install if not)
- Install the `plyer` dependency automatically
- Launch the app

## Download

Download the latest `StretchTimer.zip` from the [Releases](../../releases) page. Then:
1. Extract the ZIP
2. Double-click `StretchTimer.bat`
3. Install Python if prompted

## Creating a Release (for maintainers)

Releases are automated via GitHub Actions. When you create a release, `StretchTimer.zip` is built and attached automatically.

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

For local testing, run `Deploy.bat` to create `StretchTimer.zip` locally.

## Auto-Start with Windows

To have Stretch Timer start automatically when you log in:

1. Press `Win+R` to open the Run dialog
2. Type `shell:startup` and press Enter
3. Right-click in the folder and select "New > Shortcut"
4. Browse to `StretchTimer.bat` and select it
5. Name the shortcut "Stretch Timer"

## Files

| File | Description |
|------|-------------|
| `stretch_timer.py` | Main application |
| `Deploy.bat` | Creates distributable ZIP package locally |
| `Run.bat` | Quick launcher for development |
| `.github/workflows/release.yml` | GitHub Actions workflow for automated releases |
| `CLAUDE.md` | Development notes for Claude Code |

## Dependencies

- **tkinter** - GUI framework (included with Python)
- **plyer** - Desktop notifications (optional, installed automatically)

## License

MIT License - feel free to use and modify.

---

*Created with assistance from Claude*
