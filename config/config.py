"""
Configuration for the eBird Rare Bird Alert monitor
"""

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

# Notification settings
ENABLE_TEXT_NOTIFICATIONS = False
ENABLE_DISCORD_NOTIFICATIONS = True

# How often to check for updates (in minutes)
CHECK_INTERVAL = 1

# File to store previous alerts to detect new ones
DATA_STORAGE_FILE = "logs/previous_alerts.json"