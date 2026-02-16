# Phase 0.2 - Whisper.cpp Installation

## Overview
Install and verify whisper.cpp for local speech-to-text processing.

## Prerequisites
- Phase 0.1 completed (system dependencies installed)
- Build tools: gcc, make, cmake
- Git installed

## Installation Steps

### 1. Run Installation Script
```bash
./scripts/install_whisper.sh
```

This script will:
- Clone whisper.cpp repository
- Build in CPU-only mode using make
- Download base.en model (~142MB)
- Verify build and model integrity
- Place model in `models/whisper/`

### 2. Verify Installation
```bash
./scripts/test_whisper.sh
```

This will:
- Record 5 seconds of audio from your microphone
- Transcribe using whisper.cpp
- Measure and display latency
- Target: <700ms (per JARVIS_VISION.md)

### 3. Manual Test (Optional)
```bash
# Record test audio
ffmpeg -f alsa -i default -t 5 -ar 16000 -ac 1 test.wav

# Transcribe
./models/whisper.cpp/main -m models/whisper/ggml-base.en.bin -f test.wav -t 4
```

## Expected Output
```
✓ whisper.cpp cloned
✓ whisper.cpp built successfully
✓ base.en model downloaded
✓ Model verified (142315251 bytes)
```

## Troubleshooting

**Build fails:**
- Ensure build-essential, cmake installed
- Check gcc version: `gcc --version` (need 7+)

**Model download fails:**
- Check internet connection
- Manually download from: https://huggingface.co/ggerganov/whisper.cpp

**Audio recording fails:**
- Check microphone: `arecord -l`
- Test with: `arecord -d 3 test.wav`

## Files Created
```
models/
├── whisper.cpp/          # whisper.cpp source + binary
│   └── main              # transcription executable
└── whisper/
    └── ggml-base.en.bin  # model file
```

## Next Phase
Phase 0.3 - Piper TTS installation
