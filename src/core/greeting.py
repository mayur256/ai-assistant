"""Greeting module for assistant lifecycle events.

Lifecycle Events:
    - Startup: Time-aware greeting with username
    - Shutdown: Graceful goodbye message
    - Manual interrupt: Acknowledgment of user termination
"""

import os
from datetime import datetime


def get_time_of_day_greeting() -> str:
    """
    Get time-appropriate greeting.
    
    Returns:
        Greeting string based on current time
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Hello"


def get_username() -> str:
    """
    Get current username safely.
    
    Returns:
        Username or generic fallback
    """
    try:
        return os.getlogin()
    except Exception:
        # Fallback if getlogin() fails
        return os.getenv("USER", "there")


def get_startup_greeting(assistant_name: str) -> str:
    """
    Generate startup greeting message.
    
    Args:
        assistant_name: Name of the assistant
        
    Returns:
        Personalized startup greeting
    """
    time_greeting = get_time_of_day_greeting()
    username = "Sir"
    
    return f"{time_greeting}, {username}. {assistant_name} is ready and systems are online."


def get_shutdown_message(assistant_name: str) -> str:
    """
    Generate graceful shutdown message.
    
    Args:
        assistant_name: Name of the assistant
        
    Returns:
        Shutdown message
    """
    return f"Goodbye. {assistant_name} shutting down."


def get_interrupt_message() -> str:
    """
    Generate manual interrupt acknowledgment.
    
    Returns:
        Interrupt acknowledgment message
    """
    return "Interrupted. Shutting down."
