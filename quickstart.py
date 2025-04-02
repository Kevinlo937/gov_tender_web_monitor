#!/usr/bin/env python3
"""
Quick Start Script for Web Monitoring and LINE Notification System
This script provides a simple way to start the monitoring system.
"""

import os
import sys
import logging
from monitor_system import MonitoringSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quickstart.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# LINE Bot credentials
CHANNEL_ACCESS_TOKEN = "UZE4h+sLvPk/7ueINMMK+I/AoqyUIj9apJhk+clU0RHL2MzUu2YB9Whqt/zIvREQS8dJJxM0BEk6/T/zC6DQwfBT5xz+I2v6pmMm2996+d3r9uOj9T+4rw5RluMoSB9NqantoYxGXjfWY+oRexwTSQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "ce6db7dd2dd73306763452ca55b15a49"

# Search keywords
ORG_KEYWORD = "交通局"
PROJECT_KEYWORD = "水湳"

def main():
    """Main function to start the monitoring system"""
    print("=" * 60)
    print("Web Monitoring and LINE Notification System")
    print("=" * 60)
    print(f"Monitoring for tenders with:")
    print(f"  - Organization: '{ORG_KEYWORD}'")
    print(f"  - Project: '{PROJECT_KEYWORD}'")
    print("\nStarting monitoring system...")
    
    try:
        # Create and start the monitoring system
        system = MonitoringSystem(
            org_keyword=ORG_KEYWORD,
            project_keyword=PROJECT_KEYWORD,
            channel_access_token=CHANNEL_ACCESS_TOKEN,
            channel_secret=CHANNEL_SECRET
        )
        
        # Run once immediately
        print("\nRunning initial check...")
        system.run_monitoring_job()
        print("Initial check completed.")
        
        # Ask if user wants to start scheduled monitoring
        print("\nDo you want to start scheduled daily monitoring at 09:00?")
        print("Press Ctrl+C at any time to stop the system.")
        input("Press Enter to continue or Ctrl+C to exit...")
        
        # Set up the schedule and run
        system.setup_schedule()
        print(f"\nMonitoring scheduled to run daily at 09:00.")
        print("System is now running. Press Ctrl+C to stop.")
        system.run_forever()
        
    except KeyboardInterrupt:
        print("\nSystem stopped by user.")
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Check the logs for more information.")
    
    print("\nExiting...")

if __name__ == "__main__":
    main()
