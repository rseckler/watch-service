"""
Email notification service for new watch listings
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class EmailSender:
    """Send email notifications for new watch listings"""

    def __init__(self):
        """Initialize email client from environment variables"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

        # Validate configuration
        if not all([self.smtp_user, self.smtp_password, self.recipient_email]):
            logger.warning("Email configuration incomplete - notifications disabled")

    def send_new_watches_email(self, listings: List[Dict[str, Any]]) -> bool:
        """
        Send HTML email with new watch listings

        Args:
            listings: List of new listings to include in email

        Returns:
            True if email sent successfully, False otherwise
        """
        if not listings:
            logger.info("No listings to send - skipping email")
            return False

        if not all([self.smtp_user, self.smtp_password, self.recipient_email]):
            logger.warning("Email not configured - skipping notification")
            return False

        try:
            # Build HTML email
            html = self._build_html_email(listings)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 {len(listings)} neue Uhren gefunden!"
            msg['From'] = self.smtp_user
            msg['To'] = self.recipient_email

            # Attach HTML
            msg.attach(MIMEText(html, 'html', 'utf-8'))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully with {len(listings)} listings")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _build_html_email(self, listings: List[Dict[str, Any]]) -> str:
        """
        Build HTML email content

        Args:
            listings: List of listings

        Returns:
            HTML string
        """
        # Sort by price (ascending)
        sorted_listings = sorted(
            listings,
            key=lambda x: x.get('Price', 999999)
        )

        # Build listing cards
        listing_cards = []
        for listing in sorted_listings:
            manufacturer = listing.get('Manufacturer', 'Unknown')
            model = listing.get('Model', '')
            price = listing.get('Price', 0)
            currency = listing.get('Currency', 'EUR')
            condition = listing.get('Condition', 'Unbekannt')
            location = listing.get('Location', 'Unbekannt')
            source = listing.get('Source', 'Unknown')
            link = listing.get('Link', '#')
            ref_num = listing.get('Reference_Number', '')

            # Build title
            title = f"{manufacturer} {model}"
            if ref_num:
                title += f" ({ref_num})"

            card = f'''
            <div style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
                <h3 style="margin: 0 0 10px 0; color: #333;">{title}</h3>
                <p style="margin: 5px 0; font-size: 24px; font-weight: bold; color: #2c5aa0;">
                    {price:,.2f} {currency}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Zustand:</strong> {condition}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Standort:</strong> {location}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Quelle:</strong> {source}
                </p>
                <p style="margin: 15px 0 0 0;">
                    <a href="{link}" style="display: inline-block; padding: 10px 20px; background-color: #2c5aa0; color: white; text-decoration: none; border-radius: 5px;">
                        Angebot ansehen →
                    </a>
                </p>
            </div>
            '''
            listing_cards.append(card)

        # Build complete email
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            <div style="text-align: center; padding: 20px; background-color: #2c5aa0; color: white; border-radius: 8px;">
                <h1 style="margin: 0;">🎯 Watch Service</h1>
                <h2 style="margin: 10px 0 0 0; font-weight: normal;">
                    {len(listings)} neue Uhren gefunden!
                </h2>
            </div>

            <div style="margin: 20px 0; padding: 15px; background-color: #f0f0f0; border-radius: 8px;">
                <p style="margin: 0; color: #666;">
                    <strong>Datum:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr
                </p>
                <p style="margin: 5px 0 0 0; color: #666;">
                    <strong>Anzahl:</strong> {len(listings)} neue Angebote
                </p>
            </div>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

            {''.join(listing_cards)}

            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p style="margin: 0;">
                    Watch Service - Automated Luxury Watch Monitor
                </p>
                <p style="margin: 5px 0 0 0;">
                    Diese E-Mail wurde automatisch generiert
                </p>
            </div>
        </body>
        </html>
        '''

        return html

    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification email

        Args:
            error_message: Error description

        Returns:
            True if sent successfully
        """
        if not all([self.smtp_user, self.smtp_password, self.recipient_email]):
            return False

        try:
            html = f'''
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #d32f2f;">⚠️ Watch Service Error</h2>
                <p><strong>Zeitpunkt:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>Fehler:</strong></p>
                <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
{error_message}
                </pre>
            </body>
            </html>
            '''

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "⚠️ Watch Service Error"
            msg['From'] = self.smtp_user
            msg['To'] = self.recipient_email
            msg.attach(MIMEText(html, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("Error notification sent")
            return True

        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            return False
