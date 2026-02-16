# Phase 1 - Core Voice Loop

## Overview
Basic voice interaction loop: record → transcribe → respond → play.

## Architecture
```
main.py
  ↓
interface/
  ├── recorder.py  - Audio capture (sounddevice)
  ├── stt.py       - Whisper.cpp integration
  └── tts.py       - Piper integration
```

## Security Compliance
✅ No shell=True usage  
✅ No arbitrary command execution  
✅ All subprocess calls use list arguments  
✅ Timeouts on all external processes  
✅ No AI/LLM integration yet  

## Installation

### 1. Install Python Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Models Installed
```bash
# Check whisper.cpp
ls models/whisper.cpp/build/bin/whisper-cli

# Check Piper
ls models/piper/piper
```

## Usage

### Run Voice Loop
```bash
python main.py
```

**Flow:**
1. Records 3 seconds of audio
2. Transcribes using whisper.cpp
3. Prints transcript
4. Synthesizes "You said: <transcript>"
5. Plays response

## Testing Individual Modules

### Test Recorder
```python
from src.interface import recorder
from pathlib import Path

audio = recorder.record_audio(duration=3)
recorder.save_wav(audio, Path("test.wav"))
```

### Test STT
```python
from src.interface import stt
from pathlib import Path

transcript = stt.transcribe(
    Path("test.wav"),
    Path("models/whisper.cpp/build/bin/whisper-cli"),
    Path("models/whisper/ggml-base.en.bin")
)
print(transcript)
```

### Test TTS
```python
from src.interface import tts
from pathlib import Path

tts.synthesize(
    "Hello world",
    Path("models/piper/piper"),
    Path("models/piper/voices/en_US-lessac-medium.onnx"),
    Path("output.wav")
)
tts.play_audio(Path("output.wav"))
```

## Error Handling
- All subprocess calls have timeouts
- Exceptions propagate with clear error messages
- Temp files cleaned up in finally block
- Graceful keyboard interrupt handling

## Performance
- Recording: ~3s (user-defined)
- Transcription: <700ms (target)
- Synthesis: ~200-300ms
- Total: <4.5s

## Next Phase
Phase 2 - Intent System (rule-based + ML classification)
