#!/usr/bin/env python3
"""
LINE Notification System
This script handles sending notifications to LINE using the LINE Messaging API.
"""

import os
import logging
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("line_notification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LineNotifier:
    """Handles sending notifications to LINE"""
    
    def __init__(self, channel_access_token, user_id=None):
        """
        Initialize the LINE notifier
        
        Args:
            channel_access_token (str): LINE Channel Access Token
            user_id (str, optional): User ID to send messages to. If None, broadcasts to all users.
        """
        self.line_bot_api = LineBotApi(channel_access_token)
        self.user_id = user_id
        
    def send_message(self, message):
        """
        Send a text message to LINE
        
        Args:
            message (str): Message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.user_id:
                # Send to specific user
                self.line_bot_api.push_message(
                    self.user_id, 
                    TextSendMessage(text=message)
                )
            else:
                # Broadcast to all users (requires different permission)
                self.line_bot_api.broadcast(
                    TextSendMessage(text=message)
                )
            
            logger.info(f"Successfully sent message to LINE")
            return True
            
        except LineBotApiError as e:
            logger.error(f"Error sending message to LINE: {e}")
            return False
    
    def format_tender_notification(self, tender):
        """
        Format a tender notification message
        
        Args:
            tender (dict): Tender information
            
        Returns:
            str: Formatted message
        """
        message = "🔔 新招標公告通知 🔔\n\n"
        message += f"📋 標案編號: {tender.get('id', 'N/A')}\n"
        message += f"📝 標案名稱: {tender.get('title', 'N/A')}\n"
        message += f"🏢 招標機關: {tender.get('organization', 'N/A')}\n"
        message += f"📅 公告日期: {tender.get('date', 'N/A')}\n"
        
        if tender.get('link'):
            message += f"\n🔗 詳細資訊: {tender.get('link')}\n"
        
        message += "\n此通知由自動監控系統發送。"
        
        return message
    
    def send_tender_notification(self, tender):
        """
        Send a notification for a new tender
        
        Args:
            tender (dict): Tender information
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = self.format_tender_notification(tender)
        return self.send_message(message)
    
    def send_multiple_tenders_notification(self, tenders):
        """
        Send a notification for multiple new tenders
        
        Args:
            tenders (list): List of tender information dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not tenders:
            return True
            
        if len(tenders) == 1:
            return self.send_tender_notification(tenders[0])
            
        # For multiple tenders, send a summary and then individual notifications
        summary_message = f"🔔 發現 {len(tenders)} 個新招標公告符合您的關鍵字 ('交通局' 和 '水湳')\n\n"
        summary_message += "以下是標案清單:\n"
        
        for i, tender in enumerate(tenders, 1):
            summary_message += f"{i}. {tender.get('title', 'N/A')}\n"
            
        summary_message += "\n詳細資訊將在後續訊息中發送。"
        
        # Send the summary
        success = self.send_message(summary_message)
        
        # Send individual notifications
        for tender in tenders:
            self.send_tender_notification(tender)
            
        return success

# For testing
if __name__ == "__main__":
    # Channel access token from user input
    CHANNEL_ACCESS_TOKEN = "UZE4h+sLvPk/7ueINMMK+I/AoqyUIj9apJhk+clU0RHL2MzUu2YB9Whqt/zIvREQS8dJJxM0BEk6/T/zC6DQwfBT5xz+I2v6pmMm2996+d3r9uOj9T+4rw5RluMoSB9NqantoYxGXjfWY+oRexwTSQdB04t89/1O/w1cDnyilFU="
    
    # Create a test tender
    test_tender = {
        'id': 'TEST-001',
        'title': '水湳智慧城市建設計畫',
        'organization': '交通局',
        'date': '113/04/02',
        'link': 'https://web.pcc.gov.tw/pis/test_link',
        'found_date': '2025-04-02 05:49:00'
    }
    
    # Initialize the notifier
    notifier = LineNotifier(CHANNEL_ACCESS_TOKEN)
    
    # Send a test notification
    notifier.send_tender_notification(test_tender)
