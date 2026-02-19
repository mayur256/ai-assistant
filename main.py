"""AI Assistant Phase 5.1 - Lifecycle Management."""

import sys
import os
import json
import logging
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interface import recorder, stt, tts
from intelligence.hybrid_classifier import classify_hybrid
from intelligence.policy import setup_logging, decide_action
from intelligence.schemas import Intent
from core.execution_controller import execute_intent
from core.capability_registry import validate_capability
from core.greeting import get_startup_greeting, get_shutdown_message, get_interrupt_message


def main() -> None:
    """
    Main voice loop with lifecycle management.
    
    Lifecycle:
        - Startup: Greet user
        - Loop: Process voice commands until EXIT or interrupt
        - Shutdown: Graceful termination
    """
    
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
    print(f"{assistant_name} - Voice Assistant")
    print("=" * 50)
    print()
    
    # Setup logging
    log_dir = project_root / "logs"
    setup_logging(log_dir)
    
    # ============================================================
    # LIFECYCLE: Startup Greeting
    # ============================================================
    startup_greeting = get_startup_greeting(assistant_name)
    print(f"→ {startup_greeting}")
    
    # Speak startup greeting
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as greeting_wav:
        greeting_path = Path(greeting_wav.name)
    
    try:
        tts.synthesize(startup_greeting, piper_bin, piper_voice, greeting_path)
        tts.play_audio(greeting_path)
    finally:
        if greeting_path.exists():
            greeting_path.unlink()
    
    print()
    print("Listening for commands... (say 'exit' to quit)")
    print()
    
    # ============================================================
    # LIFECYCLE: Main Loop
    # ============================================================
    # This flag controls the assistant lifecycle
    # Set to False to trigger graceful shutdown
    assistant_running = True
    
    try:
        while assistant_running:
            # Create temp files for this iteration
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as input_wav:
                input_path = Path(input_wav.name)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_wav:
                output_path = Path(output_wav.name)
            
            try:
                # Record audio
                audio_data = recorder.record_audio(duration=10)
                recorder.save_wav(audio_data, input_path)
                
                # Transcribe
                transcript = stt.transcribe(input_path, whisper_bin, whisper_model)
                
                print()
                print(f"Transcript: {transcript}")
                print()
                
                # Classify intent using hybrid approach
                hybrid_result = classify_hybrid(transcript)
                intent_result = hybrid_result["intent_result"]
                
                print("Hybrid Classification:")
                print(f"  Rule: {hybrid_result['rule_intent']} (confidence: {hybrid_result['rule_confidence']:.2f})")
                if hybrid_result['semantic_intent']:
                    print(f"  Semantic: {hybrid_result['semantic_intent']} (similarity: {hybrid_result['semantic_similarity']:.2f})")
                print(f"  Decision Source: {hybrid_result['decision_source'].upper()}")
                print(f"  Final Intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
                print()
                
                # Policy layer: Decide action based on confidence
                response_text, should_execute = decide_action(intent_result)
                
                print(f"Policy Decision: {'EXECUTE' if should_execute else 'REJECT/CONFIRM'}")
                print(f"Response: {response_text}")
                print()
                
                # ============================================================
                # SECURITY BOUNDARY: Execution Layer
                # ============================================================
                
                execution_message = response_text
                
                if should_execute:
                    if validate_capability(intent_result.intent):
                        print("→ Executing action...")
                        exec_result = execute_intent(intent_result)
                        
                        if exec_result.success:
                            logging.info(
                                f"Execution SUCCESS: {exec_result.intent.value} | "
                                f"Message: {exec_result.message} | "
                                f"Timestamp: {exec_result.timestamp}"
                            )
                            execution_message = exec_result.message
                            print(f"✓ Execution successful: {exec_result.message}")
                            
                            # ============================================================
                            # LIFECYCLE: Check for EXIT intent
                            # ============================================================
                            if intent_result.intent == Intent.EXIT:
                                assistant_running = False
                                execution_message = get_shutdown_message(assistant_name)
                                print(f"\n→ {execution_message}")
                        else:
                            logging.error(
                                f"Execution FAILED: {exec_result.intent.value} | "
                                f"Message: {exec_result.message} | "
                                f"Timestamp: {exec_result.timestamp}"
                            )
                            execution_message = "I could not complete that action."
                            print(f"✗ Execution failed: {exec_result.message}")
                    else:
                        logging.warning(
                            f"Execution BLOCKED: {intent_result.intent.value} not in capability registry"
                        )
                        execution_message = "I cannot execute that action."
                        print(f"✗ Action blocked: Not in capability registry")
                
                print()
                
                # Synthesize and play response
                tts.synthesize(execution_message, piper_bin, piper_voice, output_path)
                print("→ Playing response...")
                tts.play_audio(output_path)
                print("✓ Playback complete")
                print()
                
                if assistant_running:
                    print("-" * 50)
                    print()
                
            finally:
                # Cleanup temp files for this iteration
                if input_path.exists():
                    input_path.unlink()
                if output_path.exists():
                    output_path.unlink()
    # ============================================================
    # LIFECYCLE: Shutdown Handling
    # ============================================================
    except KeyboardInterrupt:
        # Manual interrupt by user (Ctrl+C)
        print("\n")
        interrupt_msg = get_interrupt_message()
        print(f"→ {interrupt_msg}")
        
        # Speak interrupt message
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as interrupt_wav:
            interrupt_path = Path(interrupt_wav.name)
        
        try:
            tts.synthesize(interrupt_msg, piper_bin, piper_voice, interrupt_path)
            tts.play_audio(interrupt_path)
        except Exception:
            pass  # Fail silently on shutdown
        finally:
            if interrupt_path.exists():
                interrupt_path.unlink()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    
    # Clean exit
    print()
    print("=" * 50)
    print("✓ Assistant terminated")
    print("=" * 50)


if __name__ == "__main__":
    main()
