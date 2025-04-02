# Web Monitoring and LINE Notification System Documentation

## Overview

This system automatically monitors the Taiwan Public Construction Commission website (https://web.pcc.gov.tw/pis/) for new tender announcements that match specific criteria. When matching announcements are found, notifications are sent to a LINE bot.

### Features

- Daily automatic monitoring of the Taiwan Public Construction Commission website
- Filtering for tender announcements containing specific keywords ('交通局' and '水湳')
- LINE notifications when matching announcements are found
- History tracking to avoid duplicate notifications
- Comprehensive logging for monitoring system activity
- Scheduled execution with configurable timing

## System Components

The system consists of three main components:

1. **Web Scraper** (`web_scraper.py`): Monitors the website for new tender announcements
2. **LINE Notifier** (`line_notifier.py`): Sends notifications to LINE when new announcements are found
3. **Monitoring System** (`monitor_system.py`): Integrates the web scraper and LINE notifier

## Installation

### Prerequisites

- Python 3.6 or higher
- Internet connection
- LINE Bot account with Channel Access Token and Channel Secret

### Required Python Packages

The following Python packages are required:

- requests
- beautifulsoup4
- schedule
- line-bot-sdk

You can install them using pip:

```bash
pip install requests beautifulsoup4 schedule line-bot-sdk
```

## Configuration

The system is configured with the following parameters in `monitor_system.py`:

- `ORG_KEYWORD`: Organization keyword to search for (default: '交通局')
- `PROJECT_KEYWORD`: Project keyword to search for (default: '水湳')
- `CHANNEL_ACCESS_TOKEN`: LINE Channel Access Token
- `CHANNEL_SECRET`: LINE Channel Secret

You can modify these parameters in the `monitor_system.py` file to change the search criteria or LINE bot credentials.

## Usage

### Running the System

To start the monitoring system, run:

```bash
python monitor_system.py
```

This will:
1. Start the monitoring system
2. Run an initial check immediately
3. Schedule daily checks at 9:00 AM

### Testing the System

To test the system without sending actual notifications, run:

```bash
python test_system.py
```

This will test each component of the system and report the results.

## File Structure

- `web_scraper.py`: Web scraping functionality
- `line_notifier.py`: LINE notification functionality
- `monitor_system.py`: Integrated monitoring system
- `test_system.py`: Test script for the system
- `data/`: Directory for storing system data
  - `tender_history.json`: History of found tenders
  - `last_run.txt`: Timestamp of the last monitoring run
- `*.log`: Log files for each component

## Customization

### Changing Search Criteria

To change the search criteria, modify the `ORG_KEYWORD` and `PROJECT_KEYWORD` variables in `monitor_system.py`.

### Changing Schedule

To change the schedule, modify the `run_time` parameter in the `setup_schedule` method call in `monitor_system.py`. The time should be in 24-hour format (e.g., "09:00").

### Modifying Notification Format

To change the notification format, modify the `format_tender_notification` method in the `LineNotifier` class in `line_notifier.py`.

## Troubleshooting

### Logs

The system generates the following log files:

- `web_monitor.log`: Web scraper logs
- `line_notification.log`: LINE notifier logs
- `monitor_system.log`: Integrated system logs
- `test_system.log`: Test logs

Check these logs for information about system activity and any errors that occur.

### Common Issues

1. **No tenders found**: Verify that the search criteria are correct and that there are actually tenders matching those criteria.

2. **LINE notifications not sending**: Verify that the LINE Channel Access Token and Channel Secret are correct and that the bot has the necessary permissions.

3. **Script not running on schedule**: Ensure that the system is running continuously. Consider setting up a service or using a tool like `systemd` to ensure the script runs continuously.

## Deployment

For production deployment, it's recommended to:

1. Set up the script as a service using `systemd` or similar
2. Configure log rotation to manage log files
3. Set up monitoring to ensure the service stays running

### Example systemd Service

Create a file `/etc/systemd/system/web-monitor.service`:

```ini
[Unit]
Description=Web Monitoring and LINE Notification System
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/web_monitor
ExecStart=/usr/bin/python3 /path/to/web_monitor/monitor_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl enable web-monitor.service
sudo systemctl start web-monitor.service
```

## Security Considerations

- The LINE Channel Access Token and Channel Secret are sensitive credentials. Do not share them or commit them to public repositories.
- Consider using environment variables or a secure configuration file to store these credentials.
- Regularly rotate the credentials according to LINE's security recommendations.

## Maintenance

- Regularly check the logs for any errors or issues
- Monitor the system's resource usage
- Update the Python packages regularly to ensure security and compatibility
