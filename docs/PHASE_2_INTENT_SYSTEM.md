# Phase 2 - Deterministic Intent System

## Overview
Rule-based intent classification with keyword matching and slot extraction.

## Architecture
```
main.py
  ↓
brain/
  ├── schemas.py      - Pydantic models (Intent, IntentResult)
  ├── intents.py      - Intent definitions and patterns
  └── classifier.py   - Rule-based classifier
```

## Supported Intents

| Intent | Keywords | Slots |
|--------|----------|-------|
| OPEN_APP | open, launch, start, run | app_name |
| CLOSE_APP | close, quit, exit, kill | app_name |
| SEARCH_WEB | search, google, look up, find | query |
| PLAY_MUSIC | play, music, song, audio | - |
| STOP_MUSIC | stop, pause, halt | - |
| GET_TIME | time, what time, current time | - |
| GET_DATE | date, what date, today | - |
| UNKNOWN | (no match) | - |

## Classification Algorithm

1. **Normalize**: Lowercase and strip input
2. **Score**: Match keywords for each intent
3. **Rank**: Select intent with highest score
4. **Extract**: Pull slot values based on intent
5. **Return**: IntentResult with confidence 0.0-1.0

## Example Usage

### Test Classifier
```python
from src.brain import classifier

result = classifier.classify("open firefox")
print(result.model_dump_json(indent=2))
```

**Output:**
```json
{
  "intent": "OPEN_APP",
  "confidence": 0.75,
  "slots": {
    "app_name": "firefox"
  },
  "raw_text": "open firefox"
}
```

### Run Voice Loop
```bash
python main.py
```

**Flow:**
1. Records audio
2. Transcribes with whisper.cpp
3. Classifies intent
4. Prints JSON result
5. Speaks: "Intent detected: OPEN_APP"

## Testing

### Test Cases
```bash
# Open app
"open firefox"          → OPEN_APP (app_name: firefox)
"launch chrome"         → OPEN_APP (app_name: chrome)

# Search
"search python docs"    → SEARCH_WEB (query: python docs)
"google weather"        → SEARCH_WEB (query: weather)

# Time/Date
"what time is it"       → GET_TIME
"what's the date"       → GET_DATE

# Music
"play music"            → PLAY_MUSIC
"stop music"            → STOP_MUSIC

# Unknown
"hello there"           → UNKNOWN (confidence: 0.0)
```

## Confidence Scoring

- **1.0**: Exact word match for all keywords
- **0.5-0.9**: Partial or substring matches
- **0.0**: No keywords matched (UNKNOWN)

## Security Compliance

✅ No execution layer yet  
✅ No global state  
✅ No magic strings (Intent enum)  
✅ Type hints required  
✅ Pydantic validation  
✅ Deterministic output  

## Limitations

- Rule-based only (no ML)
- Simple keyword matching
- No context awareness
- No multi-intent support
- Limited slot extraction

## Next Phase
Phase 3 - Execution Layer (capability registry + safe controllers)
