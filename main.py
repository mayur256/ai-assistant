"""AI Assistant Phase 4 - Execution Layer Integration."""

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
from core.execution_controller import execute_intent
from core.capability_registry import validate_capability


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
    
    # Setup logging
    log_dir = project_root / "logs"
    setup_logging(log_dir)
    
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
        
        # Classify intent using hybrid approach
        # Primary: Rule-based (fast, deterministic)
        # Fallback: Semantic (handles variations)
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
        # This layer enforces safety and confirmation gates
        # Policy returns whether we should proceed to execution
        response_text, should_execute = decide_action(intent_result)
        
        print(f"Policy Decision: {'EXECUTE' if should_execute else 'REJECT/CONFIRM'}")
        print(f"Response: {response_text}")
        print()
        
        # ============================================================
        # SECURITY BOUNDARY: Execution Layer
        # ============================================================
        # All actions beyond this point go through:
        #   1. Capability Registry (validates intent is allowed)
        #   2. Execution Controller (safe subprocess calls only)
        #   3. No shell=True, no arbitrary commands, no dynamic execution
        # ============================================================
        
        execution_message = response_text
        
        if should_execute:
            # Validate intent against capability registry
            # This is the security gate - only pre-approved actions pass
            if validate_capability(intent_result.intent):
                print("→ Executing action...")
                
                # Execute through safe controller
                # All subprocess calls use shell=False
                # All parameters validated against allowed lists
                exec_result = execute_intent(intent_result)
                
                # Log execution result with timestamp
                if exec_result.success:
                    logging.info(
                        f"Execution SUCCESS: {exec_result.intent.value} | "
                        f"Message: {exec_result.message} | "
                        f"Timestamp: {exec_result.timestamp}"
                    )
                    execution_message = exec_result.message
                    print(f"✓ Execution successful: {exec_result.message}")
                else:
                    logging.error(
                        f"Execution FAILED: {exec_result.intent.value} | "
                        f"Message: {exec_result.message} | "
                        f"Timestamp: {exec_result.timestamp}"
                    )
                    execution_message = "I could not complete that action."
                    print(f"✗ Execution failed: {exec_result.message}")
            else:
                # Intent not in capability registry - security block
                logging.warning(
                    f"Execution BLOCKED: {intent_result.intent.value} not in capability registry"
                )
                execution_message = "I cannot execute that action."
                print(f"✗ Action blocked: Not in capability registry")
        
        print()
        
        # Synthesize and play response
        tts.synthesize(execution_message, piper_bin, piper_voice, output_path)
        
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
