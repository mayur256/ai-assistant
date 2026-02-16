#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "Whisper.cpp Transcription Test"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHISPER_DIR="$PROJECT_ROOT/models/whisper.cpp"
MODEL_FILE="$PROJECT_ROOT/models/whisper/ggml-base.en.bin"
TEST_AUDIO="$PROJECT_ROOT/test_audio.wav"

# Check if whisper.cpp is built
if [ ! -f "$WHISPER_DIR/build/bin/whisper-cli" ]; then
    echo "✗ whisper.cpp not built. Run scripts/install_whisper.sh first"
    exit 1
fi

# Check if model exists
if [ ! -f "$MODEL_FILE" ]; then
    echo "✗ Model not found. Run scripts/install_whisper.sh first"
    exit 1
fi

# Record test audio
echo "→ Recording 30 seconds of audio..."
echo "  (Speak into your microphone)"
ffmpeg -f pulse -i default -t 30 -ar 16000 -ac 1 -y "$TEST_AUDIO" 2>&1 | grep -v "^\[" || true
echo "✓ Audio recorded"

# Transcribe with timing
echo ""
echo "→ Transcribing..."
START_TIME=$(date +%s%3N)

"$WHISPER_DIR/build/bin/whisper-cli" -m "$MODEL_FILE" -f "$TEST_AUDIO" -t 4 --no-timestamps

END_TIME=$(date +%s%3N)
LATENCY=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "✓ Transcription complete"
echo "  Latency: ${LATENCY}ms"
if [ "$LATENCY" -lt 700 ]; then
    echo "  Status: ✓ Within target (<700ms)"
else
    echo "  Status: ⚠ Above target (>700ms)"
fi
echo "=========================================="

# Cleanup
# rm -f "$TEST_AUDIO"
