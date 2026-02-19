"""Risk level definitions for capability classification.

Security Model:
    Every action is assigned a risk level that determines:
    - Whether confirmation is required
    - Logging verbosity
    - Execution constraints
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk levels for capabilities."""
    
    LOW = "low"           # Safe operations (open app, get time)
    MEDIUM = "medium"     # Moderate risk (search web, play media)
    HIGH = "high"         # Significant risk (close app, system info)
    CRITICAL = "critical" # Dangerous operations (system commands)
