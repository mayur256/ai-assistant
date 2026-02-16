#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "JARVIS Phase 0.3 - Piper TTS Setup"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIPER_DIR="$PROJECT_ROOT/models/piper"
PIPER_BIN="$PIPER_DIR/piper"
VOICE_DIR="$PIPER_DIR/voices"
VOICE_MODEL="$VOICE_DIR/en_US-lessac-medium.onnx"
VOICE_CONFIG="$VOICE_DIR/en_US-lessac-medium.onnx.json"

echo "Project root: $PROJECT_ROOT"

# Create directories
mkdir -p "$PIPER_DIR"
mkdir -p "$VOICE_DIR"

# Download Piper binary
if [ -f "$PIPER_BIN" ]; then
    echo "✓ Piper binary already downloaded"
else
    echo "→ Downloading Piper binary..."
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
    wget -q -O /tmp/piper.tar.gz "$PIPER_URL"
    tar -xzf /tmp/piper.tar.gz -C "$PIPER_DIR" --strip-components=1
    rm /tmp/piper.tar.gz
    chmod +x "$PIPER_BIN"
    echo "✓ Piper binary downloaded"
fi

# Verify binary
if [ ! -f "$PIPER_BIN" ]; then
    echo "✗ Piper binary not found"
    exit 1
fi

# Download voice model
if [ -f "$VOICE_MODEL" ] && [ -f "$VOICE_CONFIG" ]; then
    # Check if files are not empty
    MODEL_SIZE=$(stat -c%s "$VOICE_MODEL" 2>/dev/null || echo "0")
    if [ "$MODEL_SIZE" -gt 1000000 ]; then
        echo "✓ Voice model already downloaded"
    else
        echo "→ Re-downloading voice model (previous download incomplete)..."
        rm -f "$VOICE_MODEL" "$VOICE_CONFIG"
        wget -O "$VOICE_MODEL" "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
        wget -O "$VOICE_CONFIG" "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
        echo "✓ Voice model downloaded"
    fi
else
    echo "→ Downloading en_US-lessac-medium voice..."
    wget -O "$VOICE_MODEL" "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    wget -O "$VOICE_CONFIG" "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    echo "✓ Voice model downloaded"
fi

# Verify model files
if [ ! -f "$VOICE_MODEL" ]; then
    echo "✗ Voice model file not found"
    exit 1
fi

if [ ! -f "$VOICE_CONFIG" ]; then
    echo "✗ Voice config file not found"
    exit 1
fi

MODEL_SIZE=$(stat -c%s "$VOICE_MODEL" 2>/dev/null)
if [ "$MODEL_SIZE" -lt 1000000 ]; then
    echo "✗ Voice model too small (corrupted?)"
    exit 1
fi
echo "✓ Voice model verified (${MODEL_SIZE} bytes)"

echo ""
echo "=========================================="
echo "✓ Piper TTS Setup Complete"
echo "=========================================="
echo ""
echo "Test synthesis:"
echo "  echo 'JARVIS system online.' | $PIPER_BIN -m $VOICE_MODEL -f test.wav"
echo "  aplay test.wav"
echo ""
