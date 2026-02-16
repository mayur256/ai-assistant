"""Audio recording module for JARVIS."""

import sounddevice as sd
import numpy as np
from pathlib import Path
import wave


def record_audio(duration: int = 3, sample_rate: int = 16000) -> np.ndarray:
    """
    Record audio from default microphone.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Audio sample rate in Hz
        
    Returns:
        Audio data as numpy array
    """
    print(f"→ Recording {duration} seconds of audio...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    print("✓ Recording complete")
    return audio


def save_wav(audio: np.ndarray, filepath: Path, sample_rate: int = 16000) -> None:
    """
    Save audio data to WAV file.
    
    Args:
        audio: Audio data as numpy array
        filepath: Output file path
        sample_rate: Audio sample rate in Hz
    """
    with wave.open(str(filepath), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
