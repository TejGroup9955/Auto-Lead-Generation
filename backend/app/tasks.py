from celery import Celery
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.lead import AutoLead
from app.services.lead_generation import LeadGenerationService
from app.services.email_service import EmailService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

celery_app = Celery("crm_tasks")

@celery_app.task
def generate_leads_for_campaign(campaign_id: str):
    """Background task to generate leads for a campaign"""
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return
        
        logger.info(f"Starting lead generation for campaign: {campaign.name}")
        
        # Initialize lead generation service
        lead_service = LeadGenerationService()
        
        # Generate leads
        region_name = campaign.region.name if campaign.region else "India"
        generated_leads = lead_service.generate_leads(
            keywords=campaign.keywords,
            region=region_name,
            limit=20
        )
        
        # Save leads to database
        saved_count = 0
        for lead_data in generated_leads:
            auto_lead = AutoLead(
                campaign_id=campaign.id,
                company_name=lead_data.get('company_name', ''),
                website=lead_data.get('website'),
                email=lead_data.get('email'),
                phone=lead_data.get('phone'),
                address=lead_data.get('address'),
                industry=lead_data.get('industry'),
                keywords_matched=lead_data.get('keywords_matched', []),
                relevance_score=lead_data.get('relevance_score', 0.0),
                source=lead_data.get('source', 'unknown'),
                raw_data=lead_data.get('raw_data')
            )
            
            db.add(auto_lead)
            saved_count += 1
        
        # Update campaign
        campaign.leads_generated = saved_count
        campaign.status = CampaignStatus.COMPLETED
        db.commit()
        
        logger.info(f"Generated {saved_count} leads for campaign {campaign.name}")
        
        # Send email notification (optional)
        try:
            email_service = EmailService()
            # Get admin users for notification
            from app.models.user import User, UserRole
            admin_users = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.is_active == True
            ).all()
            
            admin_emails = [user.email for user in admin_users]
            if admin_emails:
                email_service.send_lead_notification(
                    admin_emails, saved_count, campaign.name
                )
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
        
        return {"campaign_id": campaign_id, "leads_generated": saved_count}
        
    except Exception as e:
        logger.error(f"Error generating leads for campaign {campaign_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@celery_app.task
def run_scheduled_campaigns():
    """Check for scheduled campaigns and run them"""
    db = SessionLocal()
    try:
        # Find campaigns scheduled to run
        now = datetime.utcnow()
        scheduled_campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.SCHEDULED,
            Campaign.scheduled_at <= now
        ).all()
        
        for campaign in scheduled_campaigns:
            logger.info(f"Running scheduled campaign: {campaign.name}")
            
            # Update status to active
            campaign.status = CampaignStatus.ACTIVE
            db.commit()
            
            # Start lead generation task
            generate_leads_for_campaign.delay(campaign.id)
        
        return {"scheduled_campaigns_run": len(scheduled_campaigns)}
        
    except Exception as e:
        logger.error(f"Error running scheduled campaigns: {e}")
        raise
    finally:
        db.close()

@celery_app.task
def send_lead_assignment_notifications():
    """Send notifications for newly assigned leads"""
    db = SessionLocal()
    try:
        from app.models.lead import FinalLead
        from app.models.user import User
        from datetime import timedelta
        
        # Find leads assigned in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_assignments = db.query(FinalLead).filter(
            FinalLead.assigned_to.isnot(None),
            FinalLead.updated_at >= one_hour_ago
        ).all()
        
        # Group by assigned user
        assignments_by_user = {}
        for lead in recent_assignments:
            if lead.assigned_to not in assignments_by_user:
                assignments_by_user[lead.assigned_to] = []
            assignments_by_user[lead.assigned_to].append(lead)
        
        # Send notifications
        email_service = EmailService()
        notifications_sent = 0
        
        for user_id, leads in assignments_by_user.items():
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                success = email_service.send_lead_assignment_notification(
                    user.email, user.full_name, len(leads)
                )
                if success:
                    notifications_sent += 1
        
        return {"notifications_sent": notifications_sent}
        
    except Exception as e:
        logger.error(f"Error sending lead assignment notifications: {e}")
        raise
    finally:
        db.close()