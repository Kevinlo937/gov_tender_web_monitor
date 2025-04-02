#!/usr/bin/env python3
"""
Web Monitoring Script for Taiwan Public Construction Commission Website
This script monitors the website for new tender announcements containing specific keywords.
"""

import requests
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PCCWebScraper:
    """Scraper for Taiwan Public Construction Commission Website"""
    
    def __init__(self, org_keyword, project_keyword):
        """
        Initialize the scraper with search keywords
        
        Args:
            org_keyword (str): Organization keyword to search for
            project_keyword (str): Project keyword to search for
        """
        self.base_url = "https://web.pcc.gov.tw/pis/"
        self.search_url = "https://web.pcc.gov.tw/tps/pss/tender.do"
        self.org_keyword = org_keyword
        self.project_keyword = project_keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.history_file = os.path.join(self.data_dir, "tender_history.json")
        self.tender_history = self._load_history()
        
    def _load_history(self):
        """Load previously found tenders from history file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error decoding history file. Starting with empty history.")
                return {}
        return {}
    
    def _save_history(self):
        """Save tender history to file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.tender_history, f, ensure_ascii=False, indent=2)
    
    def search_tenders(self):
        """
        Search for tenders matching the specified keywords
        
        Returns:
            list: List of new tender announcements
        """
        logger.info(f"Searching for tenders with org: '{self.org_keyword}' and project: '{self.project_keyword}'")
        
        # Form data for the search request
        form_data = {
            'method': 'search',
            'searchMode': 'true',
            'searchType': 'basic',
            'tenderStatus': '4,5,21,29',  # Tender status codes
            'isSpdt': 'Y',
            'pageIndex': '1',
            'tenderWay': '1,2,3,4,5,6,7,8,9,10',
            'tenderDateRadio': 'on',
            'tenderStartDate': self._get_formatted_date(),
            'tenderEndDate': self._get_formatted_date(),
            'orgName': self.org_keyword,
            'tenderName': self.project_keyword,
            'isReset': 'Y',
            'btnQuery': '查詢'
        }
        
        try:
            # Send POST request to search for tenders
            response = requests.post(self.search_url, headers=self.headers, data=form_data)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all tender rows in the search results
            tender_rows = soup.select('div.tenderCase')
            
            if not tender_rows:
                logger.info("No tender rows found in the search results")
                return []
            
            new_tenders = []
            for row in tender_rows:
                tender = self._parse_tender_row(row)
                if tender:
                    # Check if this is a new tender
                    if tender['id'] not in self.tender_history:
                        new_tenders.append(tender)
                        self.tender_history[tender['id']] = tender
            
            # Save updated history
            self._save_history()
            
            logger.info(f"Found {len(new_tenders)} new tenders")
            return new_tenders
            
        except requests.RequestException as e:
            logger.error(f"Error searching for tenders: {e}")
            return []
    
    def _parse_tender_row(self, row):
        """
        Parse a tender row from the search results
        
        Args:
            row: BeautifulSoup element representing a tender row
            
        Returns:
            dict: Tender information or None if parsing failed
        """
        try:
            # Extract tender ID
            tender_id_elem = row.select_one('div.tenderCase_id')
            if not tender_id_elem:
                return None
            tender_id = tender_id_elem.text.strip()
            
            # Extract tender title
            title_elem = row.select_one('div.tenderCase_title')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract organization
            org_elem = row.select_one('div.tenderCase_org')
            organization = org_elem.text.strip() if org_elem else "Unknown Organization"
            
            # Extract dates
            date_elem = row.select_one('div.tenderCase_date')
            date_str = date_elem.text.strip() if date_elem else ""
            
            # Extract link to tender details
            link_elem = row.select_one('a')
            link = ""
            if link_elem and 'href' in link_elem.attrs:
                link = self.base_url + link_elem['href']
            
            return {
                'id': tender_id,
                'title': title,
                'organization': organization,
                'date': date_str,
                'link': link,
                'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing tender row: {e}")
            return None
    
    def _get_formatted_date(self):
        """Get today's date formatted for the search form (ROC calendar)"""
        today = datetime.now()
        # Convert to ROC calendar (Taiwan calendar)
        roc_year = today.year - 1911
        return f"{roc_year}/{today.month:02d}/{today.day:02d}"

# For testing
if __name__ == "__main__":
    scraper = PCCWebScraper("交通局", "水湳")
    new_tenders = scraper.search_tenders()
    
    if new_tenders:
        print(f"Found {len(new_tenders)} new tenders:")
        for tender in new_tenders:
            print(f"ID: {tender['id']}")
            print(f"Title: {tender['title']}")
            print(f"Organization: {tender['organization']}")
            print(f"Date: {tender['date']}")
            print(f"Link: {tender['link']}")
            print("-" * 50)
    else:
        print("No new tenders found.")
