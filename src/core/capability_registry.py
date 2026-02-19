"""Capability registry - defines all allowed actions.

Security Model:
    - All actions must be pre-declared in CAPABILITIES
    - No action can execute without being in this registry
    - Each capability defines:
        * Risk level
        * Allowed parameters (apps, processes, etc.)
        * Confirmation requirements
        * Execution constraints
    
    This is the security boundary - nothing executes outside this registry.
"""

from typing import Dict, List, Any
from intelligence.schemas import Intent
from core.risk import RiskLevel


# Allowed applications for OPEN_APP and CLOSE_APP
# Only these apps can be launched/closed
ALLOWED_APPS: Dict[str, str] = {
    "firefox": "firefox",
    "chrome": "google-chrome",
    "code": "code",
    "terminal": "gnome-terminal",
    "vscode": "code",
    "browser": "firefox",
}


# Allowed processes for system control
ALLOWED_PROCESSES: List[str] = [
    "firefox",
    "chrome",
    "code",
    "gnome-terminal",
]


# Capability registry - defines all allowed actions
# This is the ONLY source of truth for what can be executed
CAPABILITIES: Dict[Intent, Dict[str, Any]] = {
    Intent.OPEN_APP: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "allowed_apps": ALLOWED_APPS,
        "description": "Open an application",
        "executable": True,
    },
    
    Intent.CLOSE_APP: {
        "risk": RiskLevel.HIGH,
        "requires_confirmation": True,
        "allowed_processes": ALLOWED_PROCESSES,
        "description": "Close an application",
        "executable": True,
    },
    
    Intent.SEARCH_WEB: {
        "risk": RiskLevel.MEDIUM,
        "requires_confirmation": False,
        "description": "Search the web",
        "executable": True,
    },
    
    Intent.PLAY_MUSIC: {
        "risk": RiskLevel.MEDIUM,
        "requires_confirmation": False,
        "description": "Play music",
        "executable": True,
    },
    
    Intent.STOP_MUSIC: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Stop music playback",
        "executable": True,
    },
    
    Intent.GET_TIME: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Get current time",
        "executable": True,
    },
    
    Intent.GET_DATE: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Get current date",
        "executable": True,
    },
    
    Intent.SYSTEM_INFO: {
        "risk": RiskLevel.MEDIUM,
        "requires_confirmation": False,
        "description": "Show system information",
        "executable": True,
    },
    
    Intent.GREETING: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Respond to greeting",
        "executable": True,
    },
    
    Intent.EXIT: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Exit assistant",
        "executable": True,
    },
    
    Intent.UNKNOWN: {
        "risk": RiskLevel.LOW,
        "requires_confirmation": False,
        "description": "Unknown intent",
        "executable": False,
    },
}


def validate_capability(intent: Intent) -> bool:
    """
    Validate that intent is in capability registry and executable.
    
    Args:
        intent: Intent to validate
        
    Returns:
        True if intent can be executed
    """
    if intent not in CAPABILITIES:
        return False
    
    return CAPABILITIES[intent].get("executable", False)


def get_capability(intent: Intent) -> Dict[str, Any]:
    """
    Get capability definition for intent.
    
    Args:
        intent: Intent to look up
        
    Returns:
        Capability definition dict
        
    Raises:
        KeyError: If intent not in registry
    """
    return CAPABILITIES[intent]


def requires_confirmation(intent: Intent) -> bool:
    """
    Check if intent requires user confirmation.
    
    Args:
        intent: Intent to check
        
    Returns:
        True if confirmation required
    """
    capability = CAPABILITIES.get(intent, {})
    return capability.get("requires_confirmation", False)
