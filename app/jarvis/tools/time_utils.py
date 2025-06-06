"""
Time utilities for Jarvis voice assistant.
"""

from datetime import datetime

def get_current_time() -> dict:
    """
    Get the current time and date
    """
    now = datetime.now()
    formatted_date = now.strftime("%m-%d-%Y")
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": formatted_date,
    } 