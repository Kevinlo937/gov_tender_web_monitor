#!/usr/bin/env python3
"""
Test script for the web monitoring and LINE notification system
This script tests the functionality of the integrated system with different test cases.
"""

import logging
import os
import json
from datetime import datetime
from web_scraper import PCCWebScraper
from line_notifier import LineNotifier
from monitor_system import MonitoringSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# LINE Bot credentials
CHANNEL_ACCESS_TOKEN = "YOUR TOKEN"
CHANNEL_SECRET = "YOUR SECRET"

def create_test_tenders():
    """Create test tender data for testing"""
    return [
        {
            'id': 'TEST-001',
            'title': '水湳智慧城市建設計畫',
            'organization': '交通局',
            'date': '113/04/02',
            'link': 'https://web.pcc.gov.tw/pis/test_link_1',
            'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'TEST-002',
            'title': '水湳經貿園區交通規劃',
            'organization': '交通局',
            'date': '113/04/02',
            'link': 'https://web.pcc.gov.tw/pis/test_link_2',
            'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

def test_web_scraper():
    """Test the web scraper component"""
    logger.info("Testing web scraper component...")
    
    try:
        # Initialize the scraper with test keywords
        scraper = PCCWebScraper("交通局", "水湳")
        
        # Test the search function
        logger.info("Testing search_tenders function...")
        tenders = scraper.search_tenders()
        
        logger.info(f"Search returned {len(tenders)} tenders")
        
        # Test history tracking
        logger.info("Testing history tracking...")
        history_file = os.path.join(scraper.data_dir, "tender_history.json")
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                logger.info(f"History file contains {len(history)} entries")
        else:
            logger.warning("History file does not exist")
        
        logger.info("Web scraper test completed")
        return True
    except Exception as e:
        logger.error(f"Error testing web scraper: {e}", exc_info=True)
        return False

def test_line_notifier():
    """Test the LINE notifier component"""
    logger.info("Testing LINE notifier component...")
    
    try:
        # Initialize the notifier
        notifier = LineNotifier(CHANNEL_ACCESS_TOKEN)
        
        # Create test tenders
        test_tenders = create_test_tenders()
        
        # Test formatting
        logger.info("Testing message formatting...")
        message = notifier.format_tender_notification(test_tenders[0])
        logger.info(f"Formatted message length: {len(message)}")
        
        # Test sending a notification (uncomment to actually send)
        logger.info("Testing notification sending...")
        # Uncomment the next line to actually send a test message
        # success = notifier.send_tender_notification(test_tenders[0])
        # logger.info(f"Notification sending {'succeeded' if success else 'failed'}")
        
        logger.info("LINE notifier test completed (sending disabled)")
        return True
    except Exception as e:
        logger.error(f"Error testing LINE notifier: {e}", exc_info=True)
        return False

def test_integrated_system():
    """Test the integrated monitoring system"""
    logger.info("Testing integrated monitoring system...")
    
    try:
        # Initialize the system
        system = MonitoringSystem(
            org_keyword="交通局",
            project_keyword="水湳",
            channel_access_token=CHANNEL_ACCESS_TOKEN,
            channel_secret=CHANNEL_SECRET
        )
        
        # Test running a monitoring job
        logger.info("Testing monitoring job...")
        system.run_monitoring_job()
        
        # Check if last run was updated
        last_run = system._get_last_run()
        logger.info(f"Last run timestamp: {last_run}")
        
        logger.info("Integrated system test completed")
        return True
    except Exception as e:
        logger.error(f"Error testing integrated system: {e}", exc_info=True)
        return False

def run_all_tests():
    """Run all test cases"""
    logger.info("Starting system tests...")
    
    # Test each component
    scraper_test = test_web_scraper()
    notifier_test = test_line_notifier()
    system_test = test_integrated_system()
    
    # Report results
    logger.info("Test results:")
    logger.info(f"Web Scraper: {'PASS' if scraper_test else 'FAIL'}")
    logger.info(f"LINE Notifier: {'PASS' if notifier_test else 'FAIL'}")
    logger.info(f"Integrated System: {'PASS' if system_test else 'FAIL'}")
    
    if scraper_test and notifier_test and system_test:
        logger.info("All tests PASSED")
        return True
    else:
        logger.warning("Some tests FAILED")
        return False

if __name__ == "__main__":
    run_all_tests()
