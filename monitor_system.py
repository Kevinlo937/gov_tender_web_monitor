#!/usr/bin/env python3
"""
Integrated Web Monitoring and LINE Notification System
This script integrates the web scraper and LINE notifier to create a complete monitoring system.
"""

import os
import logging
import schedule
import time
from datetime import datetime
from web_scraper import PCCWebScraper
from line_notifier import LineNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor_system.log"),
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

class MonitoringSystem:
    """Integrated monitoring system that combines web scraping and LINE notifications"""
    
    def __init__(self, org_keyword, project_keyword, channel_access_token, channel_secret):
        """
        Initialize the monitoring system
        
        Args:
            org_keyword (str): Organization keyword to search for
            project_keyword (str): Project keyword to search for
            channel_access_token (str): LINE Channel Access Token
            channel_secret (str): LINE Channel Secret
        """
        self.org_keyword = org_keyword
        self.project_keyword = project_keyword
        self.channel_access_token = channel_access_token
        self.channel_secret = channel_secret
        
        # Initialize components
        self.scraper = PCCWebScraper(org_keyword, project_keyword)
        self.notifier = LineNotifier(channel_access_token)
        
        # Create data directory if it doesn't exist
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File to track the last run time
        self.last_run_file = os.path.join(self.data_dir, "last_run.txt")
        
    def _update_last_run(self):
        """Update the last run timestamp"""
        with open(self.last_run_file, 'w') as f:
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def _get_last_run(self):
        """Get the last run timestamp"""
        if os.path.exists(self.last_run_file):
            with open(self.last_run_file, 'r') as f:
                return f.read().strip()
        return "Never"
    
    def run_monitoring_job(self):
        """Run the monitoring job: scrape website and send notifications if new tenders are found"""
        logger.info(f"Starting monitoring job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Last run: {self._get_last_run()}")
        logger.info(f"Searching for tenders with org: '{self.org_keyword}' and project: '{self.project_keyword}'")
        
        try:
            # Search for new tenders
            new_tenders = self.scraper.search_tenders()
            
            if new_tenders:
                logger.info(f"Found {len(new_tenders)} new tenders")
                
                # Send notifications for new tenders
                notification_success = self.notifier.send_multiple_tenders_notification(new_tenders)
                
                if notification_success:
                    logger.info("Successfully sent notifications to LINE")
                else:
                    logger.error("Failed to send notifications to LINE")
            else:
                logger.info("No new tenders found")
            
            # Update last run time
            self._update_last_run()
            logger.info("Monitoring job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in monitoring job: {e}", exc_info=True)
    
    def setup_schedule(self, run_time="09:00"):
        """
        Set up the daily schedule for the monitoring job
        
        Args:
            run_time (str): Time to run the job daily (24-hour format, e.g., "09:00")
        """
        # Schedule the job to run daily at the specified time
        schedule.every().day.at(run_time).do(self.run_monitoring_job)
        logger.info(f"Scheduled monitoring job to run daily at {run_time}")
        
        # Also run once immediately when starting
        logger.info("Running initial monitoring job")
        self.run_monitoring_job()
    
    def run_forever(self):
        """Run the scheduler indefinitely"""
        logger.info("Starting monitoring system scheduler")
        
        try:
            # Keep the script running
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for pending scheduled jobs
        except KeyboardInterrupt:
            logger.info("Monitoring system stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error in scheduler: {e}", exc_info=True)

def main():
    """Main function to run the monitoring system"""
    try:
        # Create and start the monitoring system
        system = MonitoringSystem(
            org_keyword=ORG_KEYWORD,
            project_keyword=PROJECT_KEYWORD,
            channel_access_token=CHANNEL_ACCESS_TOKEN,
            channel_secret=CHANNEL_SECRET
        )
        
        # Set up the schedule and run
        system.setup_schedule()
        system.run_forever()
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    main()
