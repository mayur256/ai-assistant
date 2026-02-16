"""Speech-to-text module using whisper.cpp."""

import subprocess
from pathlib import Path


def transcribe(audio_file: Path, whisper_bin: Path, model_file: Path) -> str:
    """
    Transcribe audio file using whisper.cpp.
    
    Args:
        audio_file: Path to input WAV file
        whisper_bin: Path to whisper-cli binary
        model_file: Path to whisper model file
        
    Returns:
        Transcribed text
        
    Raises:
        RuntimeError: If transcription fails
    """
    print("→ Transcribing...")
    
    cmd = [
        str(whisper_bin),
        "-m", str(model_file),
        "-f", str(audio_file),
        "-t", "4",
        "--no-timestamps"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Parse output - whisper.cpp outputs transcript to stdout
        transcript = result.stdout.strip()
        
        # Remove any whisper.cpp metadata lines
        lines = [line for line in transcript.split('\n') if line.strip() and not line.startswith('[')]
        transcript = ' '.join(lines).strip()
        
        print("✓ Transcription complete")
        return transcript
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Transcription timeout")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Transcription failed: {e.stderr}")
