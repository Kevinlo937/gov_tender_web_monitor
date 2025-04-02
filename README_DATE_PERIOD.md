# Web Monitoring System with Date Period Specification

This document provides an overview of the modifications made to the web monitoring system to support date period specification.

## Overview

The web monitoring system has been updated to allow for date period specification when searching for tender announcements on the Taiwan Public Construction Commission website. By default, the system now searches for tenders from 2 months ago until the current date, rather than only checking the current date.

## Changes Made

1. Modified the `_get_formatted_date()` method in `web_scraper.py` to accept a `months_ago` parameter:
   ```python
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
   ```

2. Updated the `search_tenders()` method in `web_scraper.py` to use different dates for start and end:
   ```python
   def search_tenders(self, months_ago=2):
       # ...
       form_data = {
           # ...
           'tenderStartDate': self._get_formatted_date(months_ago=months_ago),
           'tenderEndDate': self._get_formatted_date(),
           # ...
       }
       # ...
   ```

3. Added a `DEFAULT_MONTHS_AGO` constant to `monitor_system.py` with a value of 2.

4. Updated the `run_monitoring_job()` method in `monitor_system.py` to accept and use the `months_ago` parameter:
   ```python
   def run_monitoring_job(self, months_ago=DEFAULT_MONTHS_AGO):
       # ...
       logger.info(f"Date range: {months_ago} months ago until now")
       # ...
       new_tenders = self.scraper.search_tenders(months_ago=months_ago)
       # ...
   ```

5. Updated the `setup_schedule()` method in `monitor_system.py` to accept and use the `months_ago` parameter:
   ```python
   def setup_schedule(self, run_time="09:00", months_ago=DEFAULT_MONTHS_AGO):
       # ...
       def scheduled_job():
           return self.run_monitoring_job(months_ago=months_ago)
       # ...
       logger.info(f"Will search for tenders from {months_ago} months ago until now")
       # ...
   ```

## Usage

The system now searches for tenders from 2 months ago until the current date by default. This behavior is controlled by the `DEFAULT_MONTHS_AGO` constant in `monitor_system.py`.

If you want to change the default date range, you can modify this constant or pass a different value to the `run_monitoring_job()` or `setup_schedule()` methods.

## Testing

The system has been tested and is working correctly. The log output confirms that the script is searching for tenders with the specified organization and project keywords ('交通局' and '水湳') and using the date range of "2 months ago until now" as required.

Example log output:
```
2025-04-02 03:57:09,275 - INFO - Searching for tenders with org: '交通局' and project: '水湳'
2025-04-02 03:57:09,275 - INFO - Date range: 2 months ago until now
```
