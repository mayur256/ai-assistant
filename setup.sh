#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "JARVIS Environment Setup - Phase 0.1"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run with sudo"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo ~"$ACTUAL_USER")

echo "Installing system dependencies..."

# Package list
PACKAGES=(
    "python3"
    "python3-venv"
    "python3-pip"
    "build-essential"
    "cmake"
    "git"
    "ffmpeg"
    "xdotool"
    "wmctrl"
    "playerctl"
    "sqlite3"
    "portaudio19-dev"
    "libasound2-dev"
    "curl"
    "wget"
)

# Update package list (allow warnings from broken third-party repos)
apt-get update -qq || true

# Install each package
for pkg in "${PACKAGES[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
        echo "✓ $pkg already installed"
    else
        echo "→ Installing $pkg..."
        if apt-get install -y -qq "$pkg" 2>/dev/null; then
            echo "✓ $pkg installed successfully"
        else
            echo "⚠ $pkg installation skipped (may be installed via other method)"
        fi
    fi
done

echo ""
echo "Creating project structure..."

# Project directories
PROJECT_ROOT="$ACTUAL_HOME/Documents/ai-assistant"
DIRS=(
    "src/interface"
    "src/intelligence"
    "src/execution"
    "src/core"
    "models"
    "logs"
    "data"
    "tests"
)

for dir in "${DIRS[@]}"; do
    DIR_PATH="$PROJECT_ROOT/$dir"
    if [ -d "$DIR_PATH" ]; then
        echo "✓ $dir exists"
    else
        mkdir -p "$DIR_PATH"
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$DIR_PATH"
        echo "✓ Created $dir"
    fi
done

echo ""
echo "Setting up Python virtual environment..."

VENV_PATH="$PROJECT_ROOT/venv"

if [ -d "$VENV_PATH" ]; then
    echo "✓ Virtual environment already exists"
else
    sudo -u "$ACTUAL_USER" python3 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created"
fi

# Upgrade pip
sudo -u "$ACTUAL_USER" "$VENV_PATH/bin/pip" install --upgrade pip -q
echo "✓ pip upgraded"

echo ""
echo "=========================================="
echo "✓ JARVIS Environment Setup Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Install Python dependencies: pip install -r requirements.txt"
echo "  3. Download models (whisper.cpp, Piper)"
echo ""
