# JARVIS — Local-First Hybrid AI Assistant

## 1. Product Vision

JARVIS is a hybrid, local-first desktop voice assistant for Linux.

**Primary objectives:**

- Fast (< 1.5 second response time)
- Deterministic execution layer
- Strict capability-based security model
- Local speech processing
- Hybrid reasoning (local + optional cloud)
- Modular, extensible architecture
- Built for learning AI/ML deeply

**JARVIS must never compromise user data.**

## 2. Core Philosophy

- Local-first by default
- Deterministic execution layer (no arbitrary shell execution)
- AI layer cannot directly execute OS commands
- All actions go through a capability registry
- High-risk actions require confirmation
- No background scanning of emails, files, or data
- Structured JSON contracts between AI and execution layers

## 3. System Architecture

**Three-layer architecture:**

### Interface Layer

- Microphone input
- Wake word detection
- Speech-to-text (whisper.cpp)
- Text-to-speech (Piper)

### Intelligence Layer (Python)

- Intent classification
- Slot extraction
- Confidence scoring
- Optional local LLM (Phase 2+)
- SQLite memory store
- Logging system

### Execution Layer

- OS automation (xdotool, wmctrl, xdg-open)
- Browser control
- File operations
- Media control (playerctl)
- No direct shell execution allowed

## 4. Security Model

### 4.1 Capability Registry

All actions must be declared in a registry.

**Example:**

```python
CAPABILITIES = {
    "OPEN_APP": {
        "risk": "low",
        "requires_confirmation": False,
        "allowed_apps": ["firefox", "code", "terminal"]
    }
}
```

No action may execute without being defined here.

### 4.2 Forbidden Behaviors

**Amazon Q must never generate:**

- Arbitrary shell command execution
- Code using shell=True
- Remote data exfiltration
- Background scanning of personal files
- Auto-sending emails
- Auto-executing downloaded scripts

### 4.3 Confirmation Gate

**High-risk actions must require:**

- Voice confirmation

**OR**

- Manual approval (keyboard)

## 5. Development Phases

### Phase 0 — Environment Setup

- Install dependencies
- Setup whisper.cpp
- Setup Piper
- Create project structure
- Setup SQLite

### Phase 1 — Core Voice Loop

- Record audio
- Transcribe
- Print transcript
- No wake word yet

### Phase 2 — Intent System

- Rule-based classifier
- ML classifier (TF-IDF + Logistic Regression)
- Confidence thresholding

### Phase 3 — Execution Layer

- Implement safe controllers
- Capability enforcement
- Logging

### Phase 4 — Local LLM Integration

- Structured JSON extraction
- Guardrails
- Fallback to deterministic intent system

### Phase 5 — Hybrid Cloud Intelligence

- Optional cloud reasoning
- Sanitized data only
- Explicit user approval for sensitive data

## 6. Performance Targets

- STT latency < 700ms
- Intent classification < 50ms
- Action execution < 300ms
- Total < 1.5s

## 7. Logging & Observability

**Every action must log:**

- Timestamp
- Intent
- Confidence
- Action taken
- Success/failure

Logs stored locally in SQLite.

## 8. Coding Standards

- Python 3.11+
- No global state
- Use dependency injection where possible
- Strict separation of AI vs execution
- Type hints required
- Pydantic models for structured data
- No magic strings for intents
- Every module testable independently

## 9. Long-Term Goals

- Plugin system
- RBAC modes (Work Mode, Personal Mode)
- Context memory
- Multi-agent architecture
- GUI using Tauri + React

## 10. Prime Directive

**JARVIS must never:**

- Execute commands outside the capability registry
- Send sensitive data externally without explicit consent
- Modify system state without deterministic routing
- Become dependent on cloud services for core functionality