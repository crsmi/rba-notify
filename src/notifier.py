"""
Module to handle sending notifications via text and Discord
"""
import os
import logging
import time
from typing import Dict, Any, List
from discord_webhook import DiscordWebhook, DiscordEmbed
from twilio.rest import Client
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    filename='logs/notifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path='config/.env')

class Notifier:
    def __init__(self):
        """Initialize the notification services"""
        # Initialize Twilio for text messages
        self.twilio_enabled = False
        self.twilio_client = None
        self.twilio_from = None
        self.twilio_to_numbers = []
        
        # Initialize Discord webhook
        self.discord_enabled = False
        self.discord_webhook_url = None
        
        # Try to set up Twilio
        try:
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            self.twilio_from = os.getenv('TWILIO_FROM_NUMBER')
            to_numbers = os.getenv('TWILIO_TO_NUMBERS')
            
            if account_sid and auth_token and self.twilio_from and to_numbers:
                self.twilio_client = Client(account_sid, auth_token)
                self.twilio_to_numbers = to_numbers.split(',')
                self.twilio_enabled = True
                logger.info("Twilio notification service initialized successfully")
            else:
                logger.warning("Twilio not fully configured - text notifications disabled")
        except Exception as e:
            logger.error(f"Error initializing Twilio: {e}")
        
        # Try to set up Discord webhook
        try:
            self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            if self.discord_webhook_url:
                self.discord_enabled = True
                logger.info("Discord webhook notification service initialized successfully")
            else:
                logger.warning("Discord webhook URL not configured - Discord notifications disabled")
        except Exception as e:
            logger.error(f"Error initializing Discord webhook: {e}")
    
    def send_text_notification(self, message: str) -> bool:
        """
        Send text notification via Twilio
        
        Args:
            message: The message to send
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.twilio_enabled:
            logger.warning("Attempted to send text but Twilio is not configured")
            return False
        
        try:
            for to_number in self.twilio_to_numbers:
                self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_from,
                    to=to_number
                )
            logger.info(f"Text notification sent to {len(self.twilio_to_numbers)} recipients")
            return True
        except Exception as e:
            logger.error(f"Error sending text notification: {e}")
            return False
    
    def send_discord_notification(self, title: str, description: str, fields: List[Dict[str, str]] = None, 
                                 color: str = "03b2f8") -> bool:
        """
        Send notification via Discord webhook
        
        Args:
            title: Title for the Discord embed
            description: Description for the Discord embed
            fields: Optional list of field dictionaries for the embed
            color: Hex color for the embed (default is light blue)
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.discord_enabled:
            logger.warning("Attempted to send Discord message but webhook is not configured")
            return False
        
        try:
            # Use the built-in rate limiting retry functionality
            webhook = DiscordWebhook(url=self.discord_webhook_url, rate_limit_retry=True)
            embed = DiscordEmbed(title=title, description=description, color=color)
            
            if fields:
                for field in fields:
                    embed.add_embed_field(
                        name=field.get('name', ''), 
                        value=field.get('value', ''), 
                        inline=field.get('inline', False)
                    )
            
            webhook.add_embed(embed)
            response = webhook.execute()
            
            # Still check for error status codes other than rate limiting
            status = getattr(response, 'status_code', None)
            if status and status >= 400:
                logger.error(f"Discord webhook returned status code {status}: {getattr(response, 'text', '')}")
                return False
                
            logger.info("Discord notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False
            
    def notify_new_bird(self, alert: Dict[str, Any], county: Dict[str, str], use_text: bool = True, 
                       use_discord: bool = True) -> None:
        """
        Send notification about a new rare bird sighting
        
        Args:
            alert: Dictionary containing alert details
            county: Dictionary with county information
            use_text: Whether to send a text notification
            use_discord: Whether to send a Discord notification
        """
        # Create text message
        species_text = alert['species']
        if 'scientificName' in alert and alert['scientificName']:
            species_text += f" ({alert['scientificName']})"
            
        text_message = (
            f"New Rare Bird Alert!\n"
            f"{species_text} - Count: {alert['count']}\n"
            f"Date: {alert['date']}\n"
            f"Location: {alert['location']}, {county['name']} County, {county['state']}\n"
            f"Observer: {alert['observer']}\n"
            f"View checklist: {alert['checklistUrl']}"
        )
        
        # Send text if enabled
        if use_text and self.twilio_enabled:
            self.send_text_notification(text_message)
        
        # Send Discord notification if enabled
        if use_discord and self.discord_enabled:
            title = f"🦜 New Rare Bird Alert: {alert['species']}"
            scientific_name = f"*{alert['scientificName']}*" if 'scientificName' in alert and alert['scientificName'] else ""
            description = f"A rare bird has been spotted in {county['name']} County, {county['state']}!"
            if scientific_name:
                description += f"\n{scientific_name}"
            
            fields = [
                {"name": "Species", "value": alert['species'], "inline": True},
                {"name": "Count", "value": alert['count'], "inline": True},
                {"name": "Date", "value": alert['date'], "inline": True},
                {"name": "Location", "value": alert['location'], "inline": True},
                {"name": "Observer", "value": alert['observer'], "inline": True},
                {"name": "View", "value": f"[eBird Checklist]({alert['checklistUrl']})", "inline": True}
            ]
            
            self.send_discord_notification(
                title=title,
                description=description,
                fields=fields,
                color="f8aa03"  # Orange/yellow color
            )