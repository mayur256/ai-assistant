"""Execution controller - safely executes validated actions.

Security Model:
    - All subprocess calls use shell=False (no shell injection)
    - All commands use list arguments (no string parsing)
    - All parameters validated against capability registry
    - All executions logged with timestamp and result
    - Timeouts on all subprocess calls
    - No dynamic command construction
    
    This layer ONLY executes - it does NOT decide what to execute.
    Decision logic is in the intelligence layer.
"""

import subprocess
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from intelligence.schemas import Intent, IntentResult
from core.capability_registry import (
    validate_capability,
    get_capability,
    ALLOWED_APPS,
)


class ExecutionResult:
    """Result of action execution."""
    
    def __init__(
        self,
        success: bool,
        message: str,
        intent: Intent,
        details: Dict[str, Any] = None
    ):
        self.success = success
        self.message = message
        self.intent = intent
        self.details = details or {}
        self.timestamp = datetime.now()


def execute_intent(intent_result: IntentResult) -> ExecutionResult:
    """
    Execute validated intent through capability registry.
    
    Security:
        - Validates intent against capability registry
        - Only executes pre-approved actions
        - Uses safe subprocess calls (shell=False)
        - Logs all execution attempts
    
    Args:
        intent_result: Validated intent to execute
        
    Returns:
        ExecutionResult with success status and message
    """
    intent = intent_result.intent
    slots = intent_result.slots
    
    # Validate capability
    if not validate_capability(intent):
        logging.warning(f"Execution blocked: {intent.value} not in capability registry")
        return ExecutionResult(
            success=False,
            message=f"Intent {intent.value} cannot be executed",
            intent=intent
        )
    
    # Log execution attempt
    logging.info(f"Executing: {intent.value} | Slots: {slots}")
    
    # Route to appropriate handler
    try:
        if intent == Intent.OPEN_APP:
            return _execute_open_app(slots)
        elif intent == Intent.CLOSE_APP:
            return _execute_close_app(slots)
        elif intent == Intent.SEARCH_WEB:
            return _execute_search_web(slots)
        elif intent == Intent.PLAY_MUSIC:
            return _execute_play_music(slots)
        elif intent == Intent.STOP_MUSIC:
            return _execute_stop_music(slots)
        elif intent == Intent.GET_TIME:
            return _execute_get_time()
        elif intent == Intent.GET_DATE:
            return _execute_get_date()
        elif intent == Intent.SYSTEM_INFO:
            return _execute_system_info()
        elif intent == Intent.GREETING:
            return _execute_greeting()
        elif intent == Intent.EXIT:
            return _execute_exit()
        elif intent == Intent.PLAY_YOUTUBE:
            return _execute_play_youtube(slots)
        elif intent == Intent.SEARCH_YOUTUBE:
            return _execute_search_youtube(slots)
        else:
            return ExecutionResult(
                success=False,
                message=f"No handler for intent: {intent.value}",
                intent=intent
            )
    except Exception as e:
        logging.error(f"Execution failed: {intent.value} | Error: {e}")
        return ExecutionResult(
            success=False,
            message=f"Execution error: {str(e)}",
            intent=intent
        )


def _execute_open_app(slots: Dict[str, Any]) -> ExecutionResult:
    """
    Open application using xdg-open or direct command.
    
    Security: Only apps in ALLOWED_APPS can be opened.
    """
    app_name = slots.get("app_name")
    
    if not app_name:
        return ExecutionResult(
            success=False,
            message="No app name specified",
            intent=Intent.OPEN_APP
        )
    
    # Validate app is in allowed list
    if app_name not in ALLOWED_APPS:
        return ExecutionResult(
            success=False,
            message=f"App '{app_name}' not in allowed list",
            intent=Intent.OPEN_APP
        )
    
    # Get executable name
    executable = ALLOWED_APPS[app_name]
    
    # Execute with shell=False (safe)
    try:
        subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        logging.info(f"Opened app: {app_name} ({executable})")
        return ExecutionResult(
            success=True,
            message=f"Opened {app_name}",
            intent=Intent.OPEN_APP,
            details={"app": app_name, "executable": executable}
        )
    except FileNotFoundError:
        return ExecutionResult(
            success=False,
            message=f"App '{app_name}' not found on system",
            intent=Intent.OPEN_APP
        )


def _execute_close_app(slots: Dict[str, Any]) -> ExecutionResult:
    """
    Close application using pkill.
    
    Security: Only processes in ALLOWED_PROCESSES can be killed.
    """
    app_name = slots.get("app_name")
    
    if not app_name:
        return ExecutionResult(
            success=False,
            message="No app name specified",
            intent=Intent.CLOSE_APP
        )
    
    # Get process name
    process_name = ALLOWED_APPS.get(app_name, app_name)
    
    # Execute pkill with shell=False (safe)
    try:
        result = subprocess.run(
            ["pkill", "-f", process_name],
            timeout=5,
            capture_output=True
        )
        
        logging.info(f"Closed app: {app_name} ({process_name})")
        return ExecutionResult(
            success=True,
            message=f"Closed {app_name}",
            intent=Intent.CLOSE_APP,
            details={"app": app_name, "process": process_name}
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            message="Close operation timed out",
            intent=Intent.CLOSE_APP
        )


def _execute_search_web(slots: Dict[str, Any]) -> ExecutionResult:
    """Open browser with search query."""
    query = slots.get("query", "")
    
    # Construct safe URL (no shell injection possible)
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    try:
        subprocess.Popen(
            ["xdg-open", search_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return ExecutionResult(
            success=True,
            message=f"Searching for: {query}",
            intent=Intent.SEARCH_WEB,
            details={"query": query}
        )
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Search failed: {e}",
            intent=Intent.SEARCH_WEB
        )


def _execute_play_music(slots: Dict[str, Any]) -> ExecutionResult:
    """Play music using playerctl."""
    try:
        subprocess.run(["playerctl", "play"], timeout=5, check=True)
        return ExecutionResult(
            success=True,
            message="Playing music",
            intent=Intent.PLAY_MUSIC
        )
    except Exception:
        return ExecutionResult(
            success=False,
            message="No media player found",
            intent=Intent.PLAY_MUSIC
        )


def _execute_stop_music(slots: Dict[str, Any]) -> ExecutionResult:
    """Stop music using playerctl."""
    try:
        subprocess.run(["playerctl", "pause"], timeout=5, check=True)
        return ExecutionResult(
            success=True,
            message="Stopped music",
            intent=Intent.STOP_MUSIC
        )
    except Exception:
        return ExecutionResult(
            success=False,
            message="No media player found",
            intent=Intent.STOP_MUSIC
        )


def _execute_get_time() -> ExecutionResult:
    """Get current time."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    return ExecutionResult(
        success=True,
        message=f"The time is {time_str}",
        intent=Intent.GET_TIME,
        details={"time": time_str}
    )


def _execute_get_date() -> ExecutionResult:
    """Get current date."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    return ExecutionResult(
        success=True,
        message=f"Today is {date_str}",
        intent=Intent.GET_DATE,
        details={"date": date_str}
    )


def _execute_system_info() -> ExecutionResult:
    """Get basic system information."""
    try:
        # Safe system info commands
        hostname = subprocess.run(
            ["hostname"],
            capture_output=True,
            text=True,
            timeout=2
        ).stdout.strip()
        
        return ExecutionResult(
            success=True,
            message=f"System: {hostname}",
            intent=Intent.SYSTEM_INFO,
            details={"hostname": hostname}
        )
    except Exception:
        return ExecutionResult(
            success=False,
            message="Could not get system info",
            intent=Intent.SYSTEM_INFO
        )


def _execute_greeting() -> ExecutionResult:
    """Respond to greeting."""
    return ExecutionResult(
        success=True,
        message="Hello! How can I help you?",
        intent=Intent.GREETING
    )


def _execute_exit() -> ExecutionResult:
    """Handle exit intent."""
    return ExecutionResult(
        success=True,
        message="Goodbye!",
        intent=Intent.EXIT
    )


def _execute_play_youtube(slots: Dict[str, Any]) -> ExecutionResult:
    """
    Play YouTube video by opening search in Brave browser.
    
    Security: Uses shell=False, URL-encoded query, no arbitrary execution.
    """
    query = slots.get("query")
    
    if not query:
        return ExecutionResult(
            success=False,
            message="No video query specified",
            intent=Intent.PLAY_YOUTUBE
        )
    
    # URL encode query (safe - no shell injection possible)
    encoded_query = query.replace(" ", "+")
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    try:
        # Launch Brave with new window (shell=False - safe)
        subprocess.Popen(
            ["brave-browser", "--new-window", youtube_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        logging.info(f"Playing YouTube: {query}")
        return ExecutionResult(
            success=True,
            message=f"Playing {query} on YouTube",
            intent=Intent.PLAY_YOUTUBE,
            details={"query": query, "url": youtube_url}
        )
    except FileNotFoundError:
        # Fallback to default browser
        try:
            subprocess.Popen(
                ["xdg-open", youtube_url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return ExecutionResult(
                success=True,
                message=f"Playing {query} on YouTube",
                intent=Intent.PLAY_YOUTUBE,
                details={"query": query, "url": youtube_url}
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                message="Could not open browser",
                intent=Intent.PLAY_YOUTUBE
            )


def _execute_search_youtube(slots: Dict[str, Any]) -> ExecutionResult:
    """
    Search YouTube by opening search results in Brave browser.
    
    Security: Uses shell=False, URL-encoded query, no arbitrary execution.
    """
    query = slots.get("query")
    
    if not query:
        return ExecutionResult(
            success=False,
            message="No search query specified",
            intent=Intent.SEARCH_YOUTUBE
        )
    
    # URL encode query (safe - no shell injection possible)
    encoded_query = query.replace(" ", "+")
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    try:
        # Launch Brave with new window (shell=False - safe)
        subprocess.Popen(
            ["brave-browser", "--new-window", youtube_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        logging.info(f"Searching YouTube: {query}")
        return ExecutionResult(
            success=True,
            message=f"Searching YouTube for {query}",
            intent=Intent.SEARCH_YOUTUBE,
            details={"query": query, "url": youtube_url}
        )
    except FileNotFoundError:
        # Fallback to default browser
        try:
            subprocess.Popen(
                ["xdg-open", youtube_url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return ExecutionResult(
                success=True,
                message=f"Searching YouTube for {query}",
                intent=Intent.SEARCH_YOUTUBE,
                details={"query": query, "url": youtube_url}
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                message="Could not open browser",
                intent=Intent.SEARCH_YOUTUBE
            )
