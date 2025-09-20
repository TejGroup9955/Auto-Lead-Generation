import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """Send email to recipients"""
        if not self.username or not self.password:
            print("Email credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.username
            msg['To'] = ', '.join(to_emails)
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_lead_notification(
        self,
        to_emails: List[str],
        lead_count: int,
        campaign_name: str
    ) -> bool:
        """Send notification about new leads generated"""
        subject = f"New Leads Generated - {campaign_name}"
        body = f"""
        Hello,
        
        {lead_count} new leads have been generated for campaign: {campaign_name}
        
        Please review the leads in the CRM system.
        
        Best regards,
        CRM System
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>New Leads Generated</h2>
            <p><strong>{lead_count}</strong> new leads have been generated for campaign: <strong>{campaign_name}</strong></p>
            <p>Please review the leads in the CRM system.</p>
            <br>
            <p>Best regards,<br>CRM System</p>
        </body>
        </html>
        """
        
        return self.send_email(to_emails, subject, body, html_body)
    
    def send_lead_assignment_notification(
        self,
        to_email: str,
        assignee_name: str,
        lead_count: int
    ) -> bool:
        """Send notification about lead assignment"""
        subject = f"New Leads Assigned to You"
        body = f"""
        Hello {assignee_name},
        
        {lead_count} new leads have been assigned to you.
        
        Please review and follow up on these leads in the CRM system.
        
        Best regards,
        CRM System
        """
        
        return self.send_email([to_email], subject, body)