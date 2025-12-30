"""
Notification services for email and SMS alerts
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiosmtplib
from twilio.rest import Client as TwilioClient


# ===== Email Configuration =====
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Workplace Safety Monitor")

# Alternatively, use SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# ===== SMS Configuration (Twilio) =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")


async def send_email_alert(
    to_email: str,
    action: str,
    confidence: float,
    video_filename: str,
    clip_path: Optional[str] = None
) -> bool:
    """
    Send email alert for unsafe action detection
    
    Args:
        to_email: Recipient email address
        action: Detected unsafe action
        confidence: Confidence score
        video_filename: Original video filename
        clip_path: Path to saved alert clip (optional)
    
    Returns:
        bool: True if email sent successfully
    """
    from datetime import datetime
    
    # Create email content
    subject = f"[ALERT] Unsafe Action Detected: {action}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #ff4444; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h1 style="margin: 0;">[!] Unsafe Action Detected</h1>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h2 style="color: #333; margin-top: 0;">Detection Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Action:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; color: #ff4444;">{action}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Confidence:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{confidence:.1%}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Video:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{video_filename}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;"><strong>Timestamp:</strong></td>
                        <td style="padding: 10px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404;">
                    <strong>Action Required:</strong> Please review the video footage and take appropriate safety measures.
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px;">
                <p>This is an automated alert from Workplace Safety Monitoring System</p>
                <p>To update your notification preferences, please log in to your account.</p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    *** UNSAFE ACTION DETECTED ***
    
    Action: {action}
    Confidence: {confidence:.1%}
    Video: {video_filename}
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Please review the video footage and take appropriate safety measures.
    
    ---
    This is an automated alert from Workplace Safety Monitoring System
    """
    
    try:
        if SENDGRID_API_KEY:
            # Use SendGrid
            return await send_email_sendgrid(to_email, subject, html_content, text_content)
        else:
            # Use SMTP
            return await send_email_smtp(to_email, subject, html_content, text_content)
    except Exception as e:
        print(f"Error sending email alert: {e}")
        return False


async def send_email_smtp(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    """Send email using SMTP"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Warning: SMTP credentials not configured. Email not sent.")
        print(f"Would have sent email to {to_email}: {subject}")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        # Add plain text and HTML parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True
        )
        
        print(f"Email alert sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email via SMTP: {e}")
        return False


async def send_email_sendgrid(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    """Send email using SendGrid API"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        message = Mail(
            from_email=Email(SMTP_FROM_EMAIL, SMTP_FROM_NAME),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"Email alert sent to {to_email} via SendGrid (status: {response.status_code})")
        return True
        
    except Exception as e:
        print(f"Error sending email via SendGrid: {e}")
        return False


async def send_sms_alert(
    to_phone: str,
    action: str,
    confidence: float,
    video_filename: str
) -> bool:
    """
    Send SMS alert for unsafe action detection using Twilio
    
    Args:
        to_phone: Recipient phone number (E.164 format: +1234567890)
        action: Detected unsafe action
        confidence: Confidence score
        video_filename: Original video filename
    
    Returns:
        bool: True if SMS sent successfully
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_FROM_NUMBER:
        print("Warning: Twilio credentials not configured. SMS not sent.")
        print(f"Would have sent SMS to {to_phone}: Unsafe action '{action}' detected")
        return False
    
    try:
        from datetime import datetime
        
        # Create SMS message (ASCII-safe for Windows compatibility)
        message_body = f"""
*** WORKPLACE SAFETY ALERT ***

Unsafe Action: {action}
Confidence: {confidence:.0%}
Video: {video_filename}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review immediately.
""".strip()
        
        # Send SMS using Twilio
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=to_phone
        )
        
        print(f"SMS alert sent to {to_phone} (SID: {message.sid})")
        return True
        
    except Exception as e:
        print(f"Error sending SMS alert: {e}")
        return False


def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    """
    Synchronous wrapper to send a simple email notification
    Used for test emails and simple notifications
    """
    import asyncio
    
    async def _send():
        return await send_email_smtp(to_email, subject, body, body)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_send())
        loop.close()
        return result
    except Exception as e:
        print(f"Error in send_email_notification: {e}")
        return False


def send_sms_notification(to_phone: str, message: str) -> bool:
    """
    Synchronous wrapper to send a simple SMS notification
    Used for test SMS and simple notifications
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_FROM_NUMBER:
        print("Warning: Twilio credentials not configured. SMS not sent.")
        # Encode message safely for printing to avoid charmap errors
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(f"Would have sent SMS to {to_phone}: {safe_message}")
        return False
    
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=to_phone
        )
        
        print(f"SMS sent to {to_phone} (SID: {twilio_message.sid})")
        return True
        
    except Exception as e:
        # Safely encode error message for printing
        error_str = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"Error sending SMS: {error_str}")
        return False


async def test_email_configuration() -> bool:
    """Test email configuration"""
    test_email = "test@example.com"
    try:
        result = await send_email_alert(
            test_email,
            "Test Action",
            0.95,
            "test_video.mp4"
        )
        return result
    except Exception as e:
        print(f"Email configuration test failed: {e}")
        return False


async def test_sms_configuration() -> bool:
    """Test SMS configuration"""
    test_phone = "+1234567890"
    try:
        result = await send_sms_alert(
            test_phone,
            "Test Action",
            0.95,
            "test_video.mp4"
        )
        return result
    except Exception as e:
        print(f"SMS configuration test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    
    print("Testing notification services...")
    print("\n=== Email Configuration ===")
    print(f"SMTP Host: {SMTP_HOST}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"SMTP Username: {SMTP_USERNAME[:5]}..." if SMTP_USERNAME else "Not configured")
    print(f"SendGrid API Key: {'Configured' if SENDGRID_API_KEY else 'Not configured'}")
    
    print("\n=== SMS Configuration ===")
    print(f"Twilio Account SID: {'Configured' if TWILIO_ACCOUNT_SID else 'Not configured'}")
    print(f"Twilio From Number: {TWILIO_FROM_NUMBER if TWILIO_FROM_NUMBER else 'Not configured'}")
    
    # Run tests
    print("\n=== Running Tests ===")
    asyncio.run(test_email_configuration())
    asyncio.run(test_sms_configuration())

