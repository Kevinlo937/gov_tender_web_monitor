#!/usr/bin/env python3
"""
Scheduler for Web Monitoring Script
This script schedules the web monitoring to run daily.
"""

import schedule
import time
import logging
from web_scraper import PCCWebScraper
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_monitoring_job():
    """Run the web monitoring job"""
    logger.info("Starting scheduled monitoring job")
    
    try:
        # Initialize the scraper with the target keywords
        scraper = PCCWebScraper("交通局", "水湳")
        
        # Search for new tenders
        new_tenders = scraper.search_tenders()
        
        if new_tenders:
            logger.info(f"Found {len(new_tenders)} new tenders")
            # The notification will be implemented in the next step
            # For now, just log the findings
            for tender in new_tenders:
                logger.info(f"New tender found: {tender['id']} - {tender['title']}")
        else:
            logger.info("No new tenders found")
            
        logger.info("Monitoring job completed successfully")
        return new_tenders
    
    except Exception as e:
        logger.error(f"Error in monitoring job: {e}")
        return []

def setup_schedule():
    """Set up the daily schedule for the monitoring job"""
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(run_monitoring_job)
    logger.info("Scheduled monitoring job to run daily at 09:00")
    
    # Also run once immediately when starting
    logger.info("Running initial monitoring job")
    run_monitoring_job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for pending scheduled jobs

if __name__ == "__main__":
    logger.info("Starting web monitoring scheduler")
    setup_schedule()
