"""
Startup script for eBird Rare Bird Alert Monitor
"""
import logging
import sys
import os
from src.monitor import main

if __name__ == "__main__":
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Set up console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ebird-rba.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Start the monitor
        main()
    except Exception as e:
        print(f"Error starting monitor: {e}")
        logging.error(f"Error starting monitor: {e}")