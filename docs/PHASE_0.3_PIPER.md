# Phase 0.3 - Piper TTS Installation

## Overview
Install and verify Piper TTS for local text-to-speech synthesis.

## Prerequisites
- Phase 0.1 completed (system dependencies installed)
- wget installed
- aplay available (alsa-utils)

## Installation Steps

### 1. Run Installation Script
```bash
./scripts/install_piper.sh
```

This script will:
- Download Piper binary (CPU version, ~10MB)
- Create `models/piper/` directory
- Download en_US-lessac-medium voice model (~63MB)
- Verify binary and model integrity

### 2. Verify Installation
```bash
./scripts/test_piper.sh
```

This will:
- Synthesize "JARVIS system online."
- Measure synthesis latency
- Play audio through speakers
- Clean up test files

### 3. Manual Test (Optional)
```bash
# Synthesize text
echo "Hello, I am JARVIS." | ./models/piper/piper -m models/piper/voices/en_US-lessac-medium.onnx -f output.wav

# Play audio
aplay output.wav
```

## Expected Output
```
✓ Piper binary downloaded
✓ Voice model downloaded
✓ Voice model verified (63201277 bytes)
✓ Synthesis complete
  Latency: 245ms
```

## Troubleshooting

**Binary download fails:**
- Check internet connection
- Manually download from: https://github.com/rhasspy/piper/releases

**Audio playback fails:**
- Check speakers: `aplay -l`
- Test with: `speaker-test -t wav -c 2`

**Synthesis too slow:**
- en_US-lessac-medium is balanced quality/speed
- For faster: use en_US-lessac-low
- For better quality: use en_US-lessac-high

## Files Created
```
models/piper/
├── piper                              # TTS binary
├── piper_phonemize                    # Phonemization library
├── espeak-ng-data/                    # Phoneme data
└── voices/
    ├── en_US-lessac-medium.onnx       # Voice model
    └── en_US-lessac-medium.onnx.json  # Voice config
```

## Voice Model Details
- Model: en_US-lessac-medium
- Language: English (US)
- Quality: Medium (balanced)
- Size: ~63MB
- Speed: ~200-300ms for short phrases

## Next Phase
Phase 1 - Core Voice Loop (Python integration)
