#!/usr/bin/env python3
"""
Web Monitoring Script for Taiwan Public Construction Commission Website
This script monitors the website for new tender announcements containing specific keywords.
Updated to use the correct URL structure based on manual search analysis.
"""

import requests
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime, timedelta
import os
import urllib.parse
import re

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
        # Updated search URL based on manual search analysis
        self.search_url = "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic"
        self.org_keyword = org_keyword
        self.project_keyword = project_keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://web.pcc.gov.tw/pis/'
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
    
    def search_tenders(self, months_ago=2, debug=False):
        """
        Search for tenders matching the specified keywords within a date range
        
        Args:
            months_ago (int): Number of months to look back for the start date. Default is 2.
            debug (bool): Whether to print debug information. Default is False.
        
        Returns:
            list: List of new tender announcements
        """
        logger.info(f"Searching for tenders with org: '{self.org_keyword}' and project: '{self.project_keyword}'")
        logger.info(f"Date range: {months_ago} months ago until now")
        
        # Calculate start and end dates
        start_date = self._get_formatted_date(months_ago=months_ago)
        end_date = self._get_formatted_date()
        
        # Convert dates to the format used in the URL (YYYY/MM/DD)
        # The URL uses Western calendar years (add 1911 to ROC year)
        start_date_parts = start_date.split('/')
        end_date_parts = end_date.split('/')
        
        start_date_url = f"{int(start_date_parts[0]) + 1911}/{start_date_parts[1]}/{start_date_parts[2]}"
        end_date_url = f"{int(end_date_parts[0]) + 1911}/{end_date_parts[1]}/{end_date_parts[2]}"
        
        # URL parameters based on manual search analysis
        params = {
            'firstSearch': 'true',
            'searchType': 'basic',
            'isBinding': 'N',
            'isLogIn': 'N',
            'orgName': self.org_keyword,
            'orgId': '',
            'tenderName': self.project_keyword,
            'tenderId': '',
            'tenderType': 'TENDER_DECLARATION',
            'tenderWay': 'TENDER_WAY_ALL_DECLARATION',
            'dateType': 'isDate',
            'tenderStartDate': start_date_url,
            'tenderEndDate': end_date_url,
            'radProctrgCate': '',
            'policyAdvocacy': ''
        }
        
        # Build the URL with parameters
        url = f"{self.search_url}?{urllib.parse.urlencode(params)}"
        
        if debug:
            logger.info(f"Search URL: {url}")
        
        try:
            # Send GET request to search for tenders
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save the response HTML for inspection if in debug mode
            if debug:
                debug_file = os.path.join(self.data_dir, "search_response.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info(f"Saved response HTML to {debug_file}")
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main results table
            # Based on the HTML structure observed in the manual search
            main_table = soup.select_one('table.tb_01')
            if not main_table:
                logger.info("No results table found in the search response")
                return []
            
            # Find all tender rows in the search results table
            tender_rows = main_table.select('tr')
            
            # Skip the first row (header) and any rows that don't contain actual tender data
            data_rows = []
            for row in tender_rows:
                # Check if this is a data row by looking for the item number in the first cell
                cells = row.select('td')
                if cells and len(cells) >= 9:  # Ensure we have enough cells
                    try:
                        # Try to convert the first cell to an integer (item number)
                        item_number = cells[0].text.strip()
                        if re.match(r'^\d+$', item_number):
                            data_rows.append(row)
                    except (ValueError, IndexError):
                        continue
            
            if not data_rows:
                logger.info("No tender data rows found in the search results")
                return []
            
            logger.info(f"Found {len(data_rows)} tender data rows in the search results")
            
            new_tenders = []
            for row in data_rows:
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
            # Extract data from table cells
            cells = row.select('td')
            if len(cells) < 9:  # Ensure we have enough cells
                logger.warning(f"Row has insufficient cells: {len(cells)}")
                return None
            
            # Extract item number (first cell)
            item_number = cells[0].text.strip()
            
            # Extract organization (second cell)
            organization = cells[1].text.strip()
            
            # Extract tender ID and title (third cell)
            tender_cell = cells[2]
            tender_text = tender_cell.get_text(separator='\n').strip()
            tender_parts = tender_text.split('\n', 1)
            
            tender_id = tender_parts[0].strip()
            title = tender_parts[1].strip() if len(tender_parts) > 1 else "Unknown Title"
            
            # Extract transmission number (fourth cell)
            transmission = cells[3].text.strip()
            
            # Extract tender method (fifth cell)
            tender_method = cells[4].text.strip()
            
            # Extract tender type (sixth cell)
            tender_type = cells[5].text.strip()
            
            # Extract announcement date (seventh cell)
            announcement_date = cells[6].text.strip()
            
            # Extract deadline (eighth cell)
            deadline = cells[7].text.strip()
            
            # Extract budget (ninth cell)
            budget = cells[8].text.strip()
            
            # Extract link to tender details
            link = ""
            link_elem = tender_cell.select_one('a')
            if link_elem and 'href' in link_elem.attrs:
                href = link_elem['href']
                if href.startswith('/'):
                    link = f"https://web.pcc.gov.tw{href}"
                else:
                    link = f"https://web.pcc.gov.tw/{href}"
            
            return {
                'id': tender_id,
                'title': title,
                'organization': organization,
                'transmission': transmission,
                'tender_method': tender_method,
                'tender_type': tender_type,
                'announcement_date': announcement_date,
                'deadline': deadline,
                'budget': budget,
                'link': link,
                'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing tender row: {e}")
            return None
    
    def _get_formatted_date(self, months_ago=0):
        """Get a date formatted for the search form (ROC calendar)
        
        Args:
            months_ago (int): Number of months to subtract from today's date.
        
        Returns:
            str: Formatted date in ROC calendar.
        """
        today = datetime.now()
        # Calculate the date `months_ago` months prior
        target_date = today - timedelta(days=months_ago * 30)  # Approximation for months
        # Convert to ROC calendar (Taiwan calendar)
        roc_year = target_date.year - 1911
        return f"{roc_year}/{target_date.month:02d}/{target_date.day:02d}"

# For testing
if __name__ == "__main__":
    # Test with the correct URL structure and parameters
    print("Testing with updated URL structure based on manual search...")
    
    # Test 1: Original keywords '交通局' and '水湳' with updated URL structure
    print("\nTest 1: Original keywords '交通局' and '水湳' with updated URL structure")
    scraper = PCCWebScraper("交通局", "水湳")
    new_tenders = scraper.search_tenders(months_ago=2, debug=True)
    
    if new_tenders:
        print(f"\nFound {len(new_tenders)} new tenders:")
        for tender in new_tenders:
            print(f"ID: {tender['id']}")
            print(f"Title: {tender['title']}")
            print(f"Organization: {tender['organization']}")
            print(f"Announcement Date: {tender['announcement_date']}")
            print(f"Deadline: {tender['deadline']}")
            print(f"Budget: {tender['budget']}")
            print(f"Link: {tender['link']}")
            print("-" * 50)
    else:
        print("\nNo new tenders found in the test.")
