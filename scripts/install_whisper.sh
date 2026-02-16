#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "JARVIS Phase 0.2 - Whisper.cpp Setup"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="$PROJECT_ROOT/models/whisper"
WHISPER_DIR="$PROJECT_ROOT/models/whisper.cpp"

echo "Project root: $PROJECT_ROOT"

# Clone whisper.cpp
if [ -d "$WHISPER_DIR" ]; then
    echo "✓ whisper.cpp already cloned"
else
    echo "→ Cloning whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
    echo "✓ whisper.cpp cloned"
fi

cd "$WHISPER_DIR"

# Build whisper.cpp (CPU-only)
if [ -f "build/bin/whisper-cli" ]; then
    echo "✓ whisper.cpp already built"
else
    echo "→ Building whisper.cpp (CPU-only)..."
    cmake -B build
    cmake --build build -j"$(nproc)"
    echo "✓ whisper.cpp built successfully"
fi

# Verify build
if [ ! -f "build/bin/whisper-cli" ]; then
    echo "✗ Build failed: whisper-cli executable not found"
    exit 1
fi

# Create models directory
mkdir -p "$MODELS_DIR"

# Download base.en model
MODEL_FILE="$MODELS_DIR/ggml-base.en.bin"
if [ -f "$MODEL_FILE" ]; then
    echo "✓ base.en model already downloaded"
else
    echo "→ Downloading base.en model..."
    bash models/download-ggml-model.sh base.en
    mv models/ggml-base.en.bin "$MODEL_FILE"
    echo "✓ Model downloaded"
fi

# Verify model integrity
if [ ! -f "$MODEL_FILE" ]; then
    echo "✗ Model file not found"
    exit 1
fi

MODEL_SIZE=$(stat -f%z "$MODEL_FILE" 2>/dev/null || stat -c%s "$MODEL_FILE" 2>/dev/null)
if [ "$MODEL_SIZE" -lt 100000000 ]; then
    echo "✗ Model file too small (corrupted?)"
    exit 1
fi
echo "✓ Model verified (${MODEL_SIZE} bytes)"

echo ""
echo "=========================================="
echo "✓ Whisper.cpp Setup Complete"
echo "=========================================="
echo ""
echo "Test transcription:"
echo "  1. Record a test audio: ffmpeg -f pulse -i default -t 5 -ar 16000 test.wav"
echo "  2. Transcribe: $WHISPER_DIR/build/bin/whisper-cli -m $MODEL_FILE -f test.wav"
echo ""
