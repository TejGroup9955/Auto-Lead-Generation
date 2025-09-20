from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.campaign import Campaign
from app.models.product import Product
from app.models.region import Region
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.auth import require_sales_or_admin, get_current_user
from app.services.activity_logger import ActivityLogger
from app.services.lead_generation import LeadGenerationService

router = APIRouter()

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all campaigns"""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return [CampaignResponse.from_orm(campaign) for campaign in campaigns]

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    request: Request,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """Create new campaign"""
    # Verify product and region exist
    product = db.query(Product).filter(Product.id == campaign_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    region = db.query(Region).filter(Region.id == campaign_data.region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    # Use product keywords if no keywords provided
    keywords = campaign_data.keywords or product.keywords or []
    
    db_campaign = Campaign(
        name=campaign_data.name,
        description=campaign_data.description,
        product_id=campaign_data.product_id,
        region_id=campaign_data.region_id,
        keywords=keywords,
        scheduled_at=campaign_data.scheduled_at,
        is_recurring=campaign_data.is_recurring,
        recurrence_pattern=campaign_data.recurrence_pattern,
        created_by=current_user.id
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    # Log activity
    ActivityLogger.log_create(
        db, current_user, "campaign", db_campaign.id, db_campaign.name, request
    )
    
    return CampaignResponse.from_orm(db_campaign)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign by ID"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse.from_orm(campaign)

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    request: Request,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """Update campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Track changes for logging
    changes = {}
    update_data = campaign_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(campaign, field) and getattr(campaign, field) != value:
            changes[field] = {"old": getattr(campaign, field), "new": value}
            setattr(campaign, field, value)
    
    if changes:
        db.commit()
        db.refresh(campaign)
        
        # Log activity
        ActivityLogger.log_update(
            db, current_user, "campaign", campaign.id, campaign.name, changes, request
        )
    
    return CampaignResponse.from_orm(campaign)

@router.post("/{campaign_id}/run")
async def run_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(require_sales_or_admin),
    db: Session = Depends(get_db)
):
    """Run campaign to generate leads"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Add background task to generate leads
    background_tasks.add_task(generate_leads_for_campaign, campaign_id, db)
    
    # Update campaign status
    campaign.status = "active"
    db.commit()
    
    # Log activity
    ActivityLogger.log_activity(
        db, current_user, "run_campaign", f"Started lead generation for campaign: {campaign.name}",
        "campaign", campaign.id, request=request
    )
    
    return {"message": "Campaign started successfully"}

async def generate_leads_for_campaign(campaign_id: str, db: Session):
    """Background task to generate leads for a campaign"""
    from app.models.lead import AutoLead
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return
        
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
        campaign.status = "completed"
        db.commit()
        
        print(f"Generated {saved_count} leads for campaign {campaign.name}")
        
    except Exception as e:
        print(f"Error generating leads for campaign {campaign_id}: {e}")
        db.rollback()