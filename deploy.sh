#!/bin/bash
# ============================================
# Stretch Timer - Linux Deployment Script
# Creates StretchTimer-Linux.tar.gz for distribution
# ============================================

set -e  # Exit on error

echo ""
echo "========================================"
echo "  Stretch Timer Linux Deployment"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
DIST_FOLDER="dist-linux"
ARCHIVE_FILE="StretchTimer-Linux.tar.gz"
SOURCE_FILE="stretch_timer.py"

# ==========================================
# Step 1: Check prerequisites
# ==========================================
echo "[1/5] Checking prerequisites..."

if [[ ! -f "$SOURCE_FILE" ]]; then
    echo "ERROR: $SOURCE_FILE not found in $SCRIPT_DIR"
    exit 1
fi
echo "       OK - $SOURCE_FILE found"

# ==========================================
# Step 2: Clean and create distribution folder
# ==========================================
echo ""
echo "[2/5] Preparing distribution folder..."

rm -rf "$DIST_FOLDER"
mkdir -p "$DIST_FOLDER"
echo "       OK - Created $DIST_FOLDER/"

# ==========================================
# Step 3: Copy source file
# ==========================================
echo ""
echo "[3/5] Copying application files..."

cp "$SOURCE_FILE" "$DIST_FOLDER/"
echo "       OK - $SOURCE_FILE copied"

# ==========================================
# Step 4: Create launcher and readme
# ==========================================
echo ""
echo "[4/5] Creating launcher and documentation..."

# Create the launcher shell script
cat > "$DIST_FOLDER/StretchTimer.sh" << 'LAUNCHER_EOF'
#!/bin/bash
# ============================================
# Stretch Timer Launcher
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || { echo "ERROR: Cannot access script directory."; exit 1; }

if [[ ! -f "stretch_timer.py" ]]; then
    echo "ERROR: stretch_timer.py not found."
    exit 1
fi

# Check for Python
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo ""
    echo "Python not found. Please install Python 3.10+:"
    echo ""
    echo "  Ubuntu/Debian: sudo apt install python3 python3-tk python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-tkinter python3-pip"
    echo "  Arch:          sudo pacman -S python python-tkinter python-pip"
    echo ""
    exit 1
fi

echo "Found Python: $PYTHON_CMD"
echo "Checking dependencies..."

# Install plyer (optional, for notifications)
$PYTHON_CMD -m pip install plyer --quiet --user 2>/dev/null || true

echo "Starting Stretch Timer..."
$PYTHON_CMD "$SCRIPT_DIR/stretch_timer.py" &
LAUNCHER_EOF

chmod +x "$DIST_FOLDER/StretchTimer.sh"
echo "       OK - StretchTimer.sh created"

# Create README
cat > "$DIST_FOLDER/README.txt" << 'README_EOF'
STRETCH TIMER (Linux)
=====================

A desktop app that reminds you to stretch at regular intervals.

REQUIREMENTS
------------
Python 3.10+ with tkinter

Install on Ubuntu/Debian:
  sudo apt install python3 python3-tk python3-pip

Install on Fedora:
  sudo dnf install python3 python3-tkinter python3-pip

Install on Arch:
  sudo pacman -S python python-tkinter python-pip

HOW TO RUN
----------
1. Open a terminal in this folder
2. Run: ./StretchTimer.sh

Or run directly:
  python3 stretch_timer.py

FEATURES
--------
- Configurable reminder intervals
- Standing stretches with step-by-step instructions
- Eye exercises and breathing exercises
- Light/dark themes
- Quiet hours
- Desktop notifications
- Auto-saved settings

AUTO-START (GNOME/KDE)
----------------------
To have Stretch Timer start automatically when you log in:

GNOME (using Startup Applications):
1. Open "Startup Applications" (gnome-session-properties)
2. Click "Add"
3. Name: Stretch Timer
4. Command: /full/path/to/StretchTimer.sh
5. Click "Add"

KDE:
1. Open System Settings > Startup and Shutdown > Autostart
2. Click "Add Script"
3. Browse to StretchTimer.sh

Using .desktop file (works on most desktops):
1. Create ~/.config/autostart/stretchtimer.desktop with:

[Desktop Entry]
Type=Application
Name=Stretch Timer
Exec=/full/path/to/StretchTimer.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
README_EOF

echo "       OK - README.txt created"

# ==========================================
# Step 5: Create tar.gz archive
# ==========================================
echo ""
echo "[5/5] Creating tar.gz archive..."

rm -f "$ARCHIVE_FILE"
tar -czf "$ARCHIVE_FILE" -C "$DIST_FOLDER" .

ARCHIVE_SIZE=$(du -h "$ARCHIVE_FILE" | cut -f1)
echo "       OK - $ARCHIVE_FILE created ($ARCHIVE_SIZE)"

# ==========================================
# Success
# ==========================================
echo ""
echo "========================================"
echo "  SUCCESS! Deployment complete."
echo "========================================"
echo ""
echo "  Output: $SCRIPT_DIR/$ARCHIVE_FILE"
echo "  Size:   $ARCHIVE_SIZE"
echo ""
echo "  Distribution contents:"
echo "  - StretchTimer.sh   (launcher)"
echo "  - stretch_timer.py  (application)"
echo "  - README.txt        (instructions)"
echo ""
