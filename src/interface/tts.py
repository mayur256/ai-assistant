"""Text-to-speech module using Piper."""

import subprocess
from pathlib import Path


def synthesize(text: str, piper_bin: Path, voice_model: Path, output_file: Path) -> None:
    """
    Synthesize speech from text using Piper.
    
    Args:
        text: Text to synthesize
        piper_bin: Path to piper binary
        voice_model: Path to voice model file
        output_file: Path to output WAV file
        
    Raises:
        RuntimeError: If synthesis fails
    """
    print("→ Synthesizing speech...")
    
    cmd = [
        str(piper_bin),
        "-m", str(voice_model),
        "-f", str(output_file)
    ]
    
    try:
        subprocess.run(
            cmd,
            input=text,
            text=True,
            check=True,
            timeout=10,
            capture_output=True
        )
        print("✓ Synthesis complete")
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Synthesis timeout")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Synthesis failed: {e.stderr}")


def play_audio(audio_file: Path) -> None:
    """
    Play audio file using aplay.
    
    Args:
        audio_file: Path to WAV file
        
    Raises:
        RuntimeError: If playback fails
    """
    cmd = ["aplay", "-q", str(audio_file)]
    
    try:
        subprocess.run(cmd, check=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Playback timeout")
    except subprocess.CalledProcessError:
        raise RuntimeError("Playback failed")
