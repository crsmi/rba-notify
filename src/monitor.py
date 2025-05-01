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
from config.config import COUNTIES, CHECK_INTERVAL, DATA_STORAGE_FILE
from config.config import ENABLE_TEXT_NOTIFICATIONS, ENABLE_DISCORD_NOTIFICATIONS

# Set up logging
logging.basicConfig(
    filename='logs/monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_for_alerts():
    """Check for new alerts and send notifications"""
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
                    
                    # Send notifications
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

def main():
    """Main function to start the monitor"""
    try:
        # Ensure necessary directories exist
        os.makedirs('logs', exist_ok=True)
        
        logger.info("Starting eBird Rare Bird Alert Monitor")
        
        # Run once immediately at startup
        check_for_alerts()
        
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