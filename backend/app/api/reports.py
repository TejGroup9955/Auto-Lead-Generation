from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.lead import AutoLead, FinalLead
from app.models.campaign import Campaign
from app.models.region import Region
from app.models.product import Product
from app.models.user import User
from app.auth import get_current_user

router = APIRouter()

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics"""
    
    # Total leads count
    total_auto_leads = db.query(func.count(AutoLead.id)).scalar() or 0
    total_final_leads = db.query(func.count(FinalLead.id)).scalar() or 0
    
    # Active campaigns
    active_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.status == "active"
    ).scalar() or 0
    
    # Conversion rate (final leads / auto leads)
    conversion_rate = (total_final_leads / total_auto_leads * 100) if total_auto_leads > 0 else 0
    
    # Leads by status
    auto_leads_by_status = db.query(
        AutoLead.status, func.count(AutoLead.id)
    ).group_by(AutoLead.status).all()
    
    final_leads_by_status = db.query(
        FinalLead.status, func.count(FinalLead.id)
    ).group_by(FinalLead.status).all()
    
    return {
        "total_leads": total_auto_leads + total_final_leads,
        "auto_leads": total_auto_leads,
        "final_leads": total_final_leads,
        "active_campaigns": active_campaigns,
        "conversion_rate": round(conversion_rate, 2),
        "auto_leads_by_status": {status.value: count for status, count in auto_leads_by_status},
        "final_leads_by_status": {status.value: count for status, count in final_leads_by_status}
    }

@router.get("/leads-by-region")
async def get_leads_by_region(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get leads count by region"""
    
    results = db.query(
        Region.name,
        func.count(AutoLead.id).label('lead_count')
    ).join(
        Campaign, Region.id == Campaign.region_id
    ).join(
        AutoLead, Campaign.id == AutoLead.campaign_id
    ).group_by(
        Region.name
    ).order_by(
        desc('lead_count')
    ).limit(10).all()
    
    return [
        {"region": region, "count": count}
        for region, count in results
    ]

@router.get("/top-products")
async def get_top_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get top products by lead generation"""
    
    results = db.query(
        Product.name,
        func.count(AutoLead.id).label('lead_count')
    ).join(
        Campaign, Product.id == Campaign.product_id
    ).join(
        AutoLead, Campaign.id == AutoLead.campaign_id
    ).group_by(
        Product.name
    ).order_by(
        desc('lead_count')
    ).limit(10).all()
    
    return [
        {"product": product, "count": count}
        for product, count in results
    ]

@router.get("/conversion-funnel")
async def get_conversion_funnel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get conversion funnel data"""
    
    # Count leads at each stage
    generated_leads = db.query(func.count(AutoLead.id)).filter(
        AutoLead.status == "generated"
    ).scalar() or 0
    
    reviewing_leads = db.query(func.count(AutoLead.id)).filter(
        AutoLead.status == "reviewing"
    ).scalar() or 0
    
    approved_leads = db.query(func.count(FinalLead.id)).filter(
        FinalLead.status == "approved"
    ).scalar() or 0
    
    contacted_leads = db.query(func.count(FinalLead.id)).filter(
        FinalLead.status == "contacted"
    ).scalar() or 0
    
    return {
        "stages": [
            {"name": "Generated", "count": generated_leads},
            {"name": "Under Review", "count": reviewing_leads},
            {"name": "Approved", "count": approved_leads},
            {"name": "Contacted", "count": contacted_leads}
        ]
    }

@router.get("/campaign-performance")
async def get_campaign_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get campaign performance metrics"""
    
    results = db.query(
        Campaign.name,
        Campaign.leads_generated,
        func.count(FinalLead.id).label('final_leads'),
        Campaign.status
    ).outerjoin(
        AutoLead, Campaign.id == AutoLead.campaign_id
    ).outerjoin(
        FinalLead, AutoLead.id == FinalLead.auto_lead_id
    ).group_by(
        Campaign.id, Campaign.name, Campaign.leads_generated, Campaign.status
    ).order_by(
        desc(Campaign.leads_generated)
    ).limit(10).all()
    
    return [
        {
            "campaign": name,
            "leads_generated": leads_generated or 0,
            "final_leads": final_leads or 0,
            "conversion_rate": round((final_leads / leads_generated * 100) if leads_generated > 0 else 0, 2),
            "status": status.value
        }
        for name, leads_generated, final_leads, status in results
    ]