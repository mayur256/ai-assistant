"""AI Assistant Phase 2 - Intent Classification."""

import sys
import os
import json
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interface import recorder, stt, tts
from intelligence import classifier


def main() -> None:
    """Main voice loop."""
    
    # Get assistant name from environment or default
    assistant_name = os.getenv("ASSISTANT_NAME", "Assistant")
    
    # Paths
    project_root = Path(__file__).parent
    whisper_bin = project_root / "models/whisper.cpp/build/bin/whisper-cli"
    whisper_model = project_root / "models/whisper/ggml-base.en.bin"
    piper_bin = project_root / "models/piper/piper"
    piper_voice = project_root / "models/piper/voices/en_US-lessac-medium.onnx"
    
    # Verify dependencies
    if not whisper_bin.exists():
        print("✗ whisper-cli not found. Run scripts/install_whisper.sh")
        sys.exit(1)
    
    if not whisper_model.exists():
        print("✗ Whisper model not found. Run scripts/install_whisper.sh")
        sys.exit(1)
    
    if not piper_bin.exists():
        print("✗ Piper not found. Run scripts/install_piper.sh")
        sys.exit(1)
    
    if not piper_voice.exists():
        print("✗ Piper voice model not found. Run scripts/install_piper.sh")
        sys.exit(1)
    
    print("=" * 50)
    print(f"{assistant_name} - Core Voice Loop")
    print("=" * 50)
    print()
    
    try:
        # Create temp files
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as input_wav:
            input_path = Path(input_wav.name)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_wav:
            output_path = Path(output_wav.name)
        
        # Record audio
        audio_data = recorder.record_audio(duration=3)
        recorder.save_wav(audio_data, input_path)
        
        # Transcribe
        transcript = stt.transcribe(input_path, whisper_bin, whisper_model)
        
        print()
        print(f"Transcript: {transcript}")
        print()
        
        # Classify intent
        intent_result = classifier.classify(transcript)
        
        print("Intent Classification:")
        print(json.dumps(intent_result.model_dump(), indent=2))
        print()
        
        # Synthesize response
        response_text = f"Intent detected: {intent_result.intent.value}"
        tts.synthesize(response_text, piper_bin, piper_voice, output_path)
        
        # Play response
        print("→ Playing response...")
        tts.play_audio(output_path)
        print("✓ Playback complete")
        
        print()
        print("=" * 50)
        print("✓ Voice loop complete")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup temp files
        if input_path.exists():
            input_path.unlink()
        if output_path.exists():
            output_path.unlink()


if __name__ == "__main__":
    main()
