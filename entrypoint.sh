#!/bin/bash
# Script that runs at container startup to ensure proper setup

# Ensure log directory exists with proper permissions
mkdir -p logs
touch logs/ebird-rba.log
touch logs/ebird_fetcher.log
touch logs/monitor.log

# Create an empty previous_alerts.json file if it doesn't exist
if [ ! -f logs/previous_alerts.json ]; then
    echo "{}" > logs/previous_alerts.json
fi

# If running in Docker, use the Docker-specific config file
if [ -f config/config_docker.py ]; then
    cp config/config_docker.py config/config.py
fi

# Run the application
exec python src/monitor.py
