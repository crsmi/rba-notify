# eBird Rare Bird Alert Monitor

This program monitors the eBird Rare Bird Alert system for specified counties and sends notifications when new rare bird sightings are reported. Currently configured for Portage County, Wisconsin, but easily extensible to monitor additional counties.

## Project Development

This project was developed through "vibe coding" using GitHub Copilot in agent mode. The design, implementation, and documentation were created collaboratively with GitHub's AI assistant.

## Deployment Options

You can run this application:
1. Directly using Python (see Setup section below)
2. Using Docker (see [Docker Setup](DOCKER.md) for container deployment)
3. On Ubuntu Server (see [Ubuntu Server Setup](UBUNTU.md) for specific instructions)
4. Using Portainer (see [Portainer Setup](PORTAINER.md) for deployment through Portainer)
5. For troubleshooting and verification, see the [Verification Guide](VERIFICATION.md)

### Deployment Status

The application has been successfully deployed on a mini PC running Ubuntu Server using Portainer. See the deployment guides for details on how to replicate this setup.

## Features

- Automatically checks for new rare bird alerts at regular intervals
- Sends notifications through text messages (via Twilio) and/or Discord
- Remembers previously seen alerts to avoid duplicate notifications
- Easily configurable to monitor multiple counties
- Detailed logging of all activities

## Setup

### Option 1: Using Conda (Recommended)

1. Clone this repository
2. Create and activate the conda environment:
   ```
   conda env create -f environment.yml
   conda activate ebird-rba
   ```
3. Create a `.env` file in the `config` directory (copy from `.env.template`):
   ```
   cp config/.env.template config/.env
   ```
4. Edit the `.env` file with your notification credentials:
   - For text notifications via Twilio, add your Twilio account SID, auth token, from number, and recipient numbers
   - For Discord notifications, add your Discord webhook URL

### Option 2: Using pip

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `config` directory (copy from `.env.template`):
   ```
   cp config/.env.template config/.env
   ```
4. Edit the `.env` file with your notification credentials:
   - For text notifications via Twilio, add your Twilio account SID, auth token, from number, and recipient numbers
   - For Discord notifications, add your Discord webhook URL

- **Windows users**: You can run `setup.bat` instead of manual commands to create the conda environment, copy the .env template, and create the logs folder.

## Configuration

Edit `config/config.py` to customize the application behavior:

- `COUNTIES`: List of counties to monitor (each with name, state, alert_id, and URL)
- `CHECK_INTERVAL`: How often to check for updates (in minutes)
- `ENABLE_TEXT_NOTIFICATIONS`: Set to `True` or `False` to enable/disable text notifications
- `ENABLE_DISCORD_NOTIFICATIONS`: Set to `True` or `False` to enable/disable Discord notifications
- `NOTIFY_ON_STARTUP`: When set to `False`, existing alerts found during the first run will be recorded but won't trigger notifications. Only new alerts that appear after the application starts will send notifications. Set to `True` to receive notifications for all alerts, including existing ones at startup.

### Adding More Counties

To monitor additional counties:

1. Find the county's eBird alert URL (format: `https://ebird.org/alert/summary?sid=SN[ID]&sortBy=obsDt&o=desc`)
2. Extract the alert ID from the URL (the `SN[ID]` part)
3. Add a new entry to the `COUNTIES` list in `config/config.py`:
   ```python
   {
       "name": "County Name",
       "state": "State Name",
       "alert_id": "SN12345",  # Replace with actual alert ID
       "url": "https://ebird.org/alert/summary?sid=SN12345&sortBy=obsDt&o=desc"
   }
   ```

## Running the Application

- If using the Conda environment (recommended):
  ```
  conda activate ebird-rba
  python run.py
  ```
- On Windows, you can also use the setup script:
  ```
  setup.bat
  conda activate ebird-rba
  python run.py
  ```

This will:
1. When run from an interactive terminal:
   - Show a summary of any new alerts found at startup
   - Allow you to choose whether to send notifications for these alerts:
     - `(y)es`: Send notifications for all alerts
     - `(n)o`: Skip these alerts entirely
     - `(s)ilent record`: Record the alerts without sending notifications
2. When run non-interactively or as a service:
   - Uses the `NOTIFY_ON_STARTUP` configuration option to determine startup notification behavior
3. Schedule regular checks based on the configured interval
4. Log all activity to the `logs` directory

## Logs

- Application logs are split by component and stored in the `logs/` folder:
  - `logs/monitor.log`: Main monitoring loop and scheduling
  - `logs/ebird_fetcher.log`: HTML fetch & parse operations
  - `logs/notifier.log`: Notification delivery operations
- The root-level `logs/ebird-rba.log` created by `run.py` remains empty because component modules configure their own loggers. You can safely ignore this file or remove it.
- Previous alert IDs are saved in `logs/previous_alerts.json` to prevent duplicate notifications.

## Testing

- A helper script `test_detection.py` allows you to verify the new‐observation detection logic against simulated data.
- Test data lives in `test_data/test_observations.json`.

## Requirements

- Python 3.6+ (Python 3.10 recommended)
- Conda environment (recommended) or pip installation
- Required packages are listed in `environment.yml` and `requirements.txt`
- For text notifications: Twilio account
- For Discord notifications: Discord webhook URL

## Future Enhancements

- **Observer Comments/Details**: Add ability to fetch and include observation details/comments that observers submit with their sightings. These details are currently available on eBird by clicking the dropdown arrow for each observation but would require additional HTTP requests to retrieve.
  - **Implementation Option 1**: Use the eBird API endpoint that serves these comments (e.g., `/alert/comments?obsId=OBS3092797574`) by extracting the observation ID from the main alert and making a second request for each observation.
  - **Implementation Option 2**: Fetch the full checklist page (e.g., `https://ebird.org/checklist/S229217027`) and parse the comments section (usually found in elements with class `.ChecklistComments` or `.CommentPanel`).
  - Both approaches would require extending `EBirdFetcher.fetch_alerts()` to optionally make these extra requests and including the results in the returned observation dictionary.
- Additional notification methods (email, push notifications, etc.)
- User interface for configuration

## Verifying Deployment

To confirm your deployment is working correctly:

1. **Check Container Logs**:
   - In Portainer: Navigate to Containers > ebird-rba > Logs
   - Via Docker CLI: `docker logs ebird-rba`
   - Look for messages like "Checking for new alerts..." which indicates the application is actively running

2. **Verify Notifications**:
   - If `NOTIFY_ON_STARTUP` is set to `true`, you should receive a notification on startup with any existing alerts
   - Otherwise, wait for the next rare bird alert or create a test entry in eBird (if you have permissions)

3. **Test Data Persistence**:
   - After receiving a notification, restart the container
   - Verify you don't receive duplicate notifications for the same alerts

See the [Verification and Troubleshooting Guide](VERIFICATION.md) for detailed instructions on verifying your deployment and troubleshooting common issues.