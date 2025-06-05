"""
Main application for monitoring eBird Rare Bird Alerts and sending notifications
"""
import logging
import time
import schedule
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ebird_fetcher import EBirdFetcher
from src.notifier import Notifier
from config.config import COUNTIES, CHECK_INTERVAL, DATA_STORAGE_FILE, NOTIFY_ON_STARTUP
from config.config import ENABLE_TEXT_NOTIFICATIONS, ENABLE_DISCORD_NOTIFICATIONS

# Set up logging
logging.basicConfig(
    filename='logs/monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_for_alerts(is_startup_run=False):
    """
    Check for new alerts and send notifications
    
    Args:
        is_startup_run: Whether this is the first run at application startup
    """
    try:
        logger.info("Starting alert check")
        
        # Initialize the fetcher and notifier
        fetcher = EBirdFetcher(DATA_STORAGE_FILE)
        notifier = Notifier()
        
        # Check each configured county
        for county in COUNTIES:
            logger.info(f"Checking {county['name']} County, {county['state']}")
            
            # Get new alerts for this county
            new_alerts = fetcher.get_new_alerts(county)
            
            if new_alerts:
                logger.info(f"Found {len(new_alerts)} new alerts for {county['name']} County")
                
                # Process each new alert
                for alert in new_alerts:
                    # Log the alert
                    logger.info(f"New alert: {alert['species']} at {alert['location']}")
                    
                    # Send notifications based on configuration
                    # Skip notifications at startup if configured to do so
                    should_notify = True
                    if is_startup_run and not NOTIFY_ON_STARTUP:
                        logger.info(f"Skipping notification for {alert['species']} (startup notification disabled)")
                        should_notify = False
                    
                    if should_notify:
                        notifier.notify_new_bird(
                            alert=alert,
                            county=county,
                            use_text=ENABLE_TEXT_NOTIFICATIONS,
                            use_discord=ENABLE_DISCORD_NOTIFICATIONS
                        )
            else:
                logger.info(f"No new alerts for {county['name']} County")
                
        logger.info("Alert check completed")
    except Exception as e:
        logger.error(f"Error during alert check: {e}")

def check_interactive(interactive=False):
    """
    Check for alerts in interactive mode, allowing user to choose notification behavior
    
    Args:
        interactive: Whether to run in interactive mode with user prompts
    
    Returns:
        List of new alerts found across all counties
    """
    all_new_alerts = []
    
    try:
        logger.info("Starting interactive alert check")
        
        # Initialize the fetcher but don't save changes yet
        fetcher = EBirdFetcher(DATA_STORAGE_FILE)
        previous_alerts = fetcher.previous_alerts.copy()
        
        # Check each configured county and collect alerts without saving
        for county in COUNTIES:
            county_name = f"{county['name']} County, {county['state']}"
            logger.info(f"Checking {county_name}")
            
            # Get all alerts (not saving to previous_alerts yet)
            all_alerts = fetcher.fetch_alerts(county)
            
            # Filter for new alerts
            alert_id = county['alert_id']
            if alert_id not in previous_alerts:
                previous_alerts[alert_id] = []
                
            new_alerts = []
            for alert in all_alerts:
                if alert['id'] not in previous_alerts[alert_id]:
                    new_alerts.append(alert)
                    all_new_alerts.append((county, alert))
            
            if new_alerts:
                logger.info(f"Found {len(new_alerts)} new alerts for {county_name}")
            else:
                logger.info(f"No new alerts for {county_name}")
                
    except Exception as e:
        logger.error(f"Error during interactive alert check: {e}")
        
    return all_new_alerts

def main():
    """Main function to start the monitor"""
    try:
        # Ensure necessary directories exist
        os.makedirs('logs', exist_ok=True)
        
        logger.info("Starting eBird Rare Bird Alert Monitor")
        
        # Check if running in interactive terminal
        interactive = sys.stdout.isatty()
        
        if interactive:
            # Interactive mode - summarize and ask for confirmation
            all_new_alerts = check_interactive(interactive=True)
            
            if all_new_alerts:
                print(f"\nFound {len(all_new_alerts)} new rare bird alerts:")
                
                # Group by county for better readability
                by_county = {}
                for county, alert in all_new_alerts:
                    county_name = f"{county['name']} County, {county['state']}"
                    if county_name not in by_county:
                        by_county[county_name] = []
                    by_county[county_name].append(alert)
                
                # Print summary by county
                for county_name, alerts in by_county.items():
                    print(f"\n{county_name}:")
                    for alert in alerts:
                        print(f"  - {alert['species']} ({alert['count']}) at {alert['location']} by {alert['observer']}")
                
                # Ask user what to do
                notify_choice = None
                while notify_choice not in ['y', 'n', 's']:
                    notify_choice = input("\nSend notifications for these alerts? (y)es/(n)o/(s)ilent record: ").lower()
                
                # Run with appropriate parameters based on user choice
                if notify_choice == 'y':
                    print("Sending notifications for all alerts...")
                    check_for_alerts(is_startup_run=False)  # Full notifications
                elif notify_choice == 'n':
                    print("Skipping these alerts entirely...")
                    # Do nothing - alerts won't be saved to previous_alerts
                else:  # silent mode
                    print("Recording alerts without notifications...")
                    check_for_alerts(is_startup_run=True)  # No notifications if NOTIFY_ON_STARTUP is False
            else:
                print("No new rare bird alerts found.")
                # Still run check_for_alerts to ensure data structures are initialized
                check_for_alerts(is_startup_run=True)
        else:
            # Non-interactive mode - use configuration setting
            check_for_alerts(is_startup_run=True)
        
        # Schedule regular checks
        schedule.every(CHECK_INTERVAL).minutes.do(check_for_alerts)
        
        logger.info(f"Monitor scheduled to check every {CHECK_INTERVAL} minutes")
        
        # Run the scheduler in a loop
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()