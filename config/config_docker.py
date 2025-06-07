"""
Configuration for the eBird Rare Bird Alert monitor.
This file supports environment variable overrides for easy Docker deployment.
"""
import os
from typing import Dict, List, Any

# Counties to monitor - can be extended with more counties
# Each entry contains: county_name, state, alert_id
COUNTIES = [
    {
        "name": "Portage",
        "state": "Wisconsin",
        "alert_id": "SN37222",
        "url": "https://ebird.org/alert/summary?sid=SN37222&sortBy=obsDt&o=desc"
    },
    # {
    #     "name": "Dane",
    #     "state": "Wisconsin",
    #     "alert_id": "SN35559",
    #     "url": "https://ebird.org/alert/summary?sid=SN35559&sortBy=obsDt&o=desc"
    # },
    # {
    #     "name": "WI",
    #     "state": "Wisconsin",
    #     "alert_id": "SN35574",
    #     "url": "https://ebird.org/alert/summary?sid=SN35574&sortBy=obsDt&o=desc"
    # }
]

# Load environment variables or use defaults
def get_env_bool(name: str, default: bool) -> bool:
    """Get boolean environment variable"""
    val = os.environ.get(name, str(default).lower())
    return val.lower() in ('true', 't', 'yes', 'y', '1')

def get_env_int(name: str, default: int) -> int:
    """Get integer environment variable"""
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default

# Notification settings
ENABLE_TEXT_NOTIFICATIONS = get_env_bool("ENABLE_TEXT_NOTIFICATIONS", False)
ENABLE_DISCORD_NOTIFICATIONS = get_env_bool("ENABLE_DISCORD_NOTIFICATIONS", True)

# How often to check for updates (in minutes)
CHECK_INTERVAL = get_env_int("CHECK_INTERVAL", 1)

# Control whether existing alerts trigger notifications on startup
# When False, only new alerts after the program starts will trigger notifications
NOTIFY_ON_STARTUP = get_env_bool("NOTIFY_ON_STARTUP", False)

# File to store previous alerts to detect new ones
DATA_STORAGE_FILE = os.environ.get("DATA_STORAGE_FILE", "logs/previous_alerts.json")
