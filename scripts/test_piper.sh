#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "Piper TTS Synthesis Test"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIPER_BIN="$PROJECT_ROOT/models/piper/piper"
VOICE_MODEL="$PROJECT_ROOT/models/piper/voices/en_US-lessac-medium.onnx"
TEST_AUDIO="$PROJECT_ROOT/test_tts.wav"

# Check if Piper is installed
if [ ! -f "$PIPER_BIN" ]; then
    echo "✗ Piper not installed. Run scripts/install_piper.sh first"
    exit 1
fi

# Check if voice model exists
if [ ! -f "$VOICE_MODEL" ]; then
    echo "✗ Voice model not found. Run scripts/install_piper.sh first"
    exit 1
fi

# Synthesize test phrase
echo "→ Synthesizing: 'JARVIS system online.'"
START_TIME=$(date +%s%3N)

echo "JARVIS system online." | "$PIPER_BIN" -m "$VOICE_MODEL" -f "$TEST_AUDIO"

END_TIME=$(date +%s%3N)
LATENCY=$((END_TIME - START_TIME))

echo "✓ Synthesis complete"
echo "  Latency: ${LATENCY}ms"

# Play audio
echo ""
echo "→ Playing audio..."
aplay -q "$TEST_AUDIO" 2>/dev/null

echo ""
echo "=========================================="
echo "✓ TTS Test Complete"
echo "  Synthesis time: ${LATENCY}ms"
echo "=========================================="

# Cleanup
rm -f "$TEST_AUDIO"
