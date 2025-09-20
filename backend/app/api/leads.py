from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.lead import AutoLead, FinalLead, LeadStatus
from app.models.user import User
from app.schemas.lead import (
    AutoLeadCreate, AutoLeadResponse, 
    FinalLeadCreate, FinalLeadResponse, FinalLeadUpdate
)
from app.auth import require_reviewer_or_above, get_current_user
from app.services.activity_logger import ActivityLogger
import pandas as pd
from io import StringIO

router = APIRouter()

# Auto Leads endpoints
@router.get("/auto", response_model=List[AutoLeadResponse])
async def get_auto_leads(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in company name, email, industry"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get auto-generated leads"""
    query = db.query(AutoLead)
    
    if status_filter:
        query = query.filter(AutoLead.status == status_filter)
    
    if search:
        query = query.filter(
            or_(
                AutoLead.company_name.contains(search),
                AutoLead.email.contains(search),
                AutoLead.industry.contains(search)
            )
        )
    
    leads = query.offset(skip).limit(limit).all()
    return [AutoLeadResponse.from_orm(lead) for lead in leads]

@router.post("/auto", response_model=AutoLeadResponse)
async def create_auto_lead(
    lead_data: AutoLeadCreate,
    request: Request,
    current_user: User = Depends(require_reviewer_or_above),
    db: Session = Depends(get_db)
):
    """Create new auto lead"""
    db_lead = AutoLead(**lead_data.dict())
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log activity
    ActivityLogger.log_create(
        db, current_user, "auto_lead", db_lead.id, db_lead.company_name, request
    )
    
    return AutoLeadResponse.from_orm(db_lead)

@router.put("/auto/{lead_id}/finalize")
async def finalize_auto_leads(
    lead_ids: List[str],
    request: Request,
    current_user: User = Depends(require_reviewer_or_above),
    db: Session = Depends(get_db)
):
    """Move auto leads to final leads"""
    finalized_count = 0
    
    for lead_id in lead_ids:
        auto_lead = db.query(AutoLead).filter(AutoLead.id == lead_id).first()
        if not auto_lead:
            continue
        
        # Create final lead from auto lead
        final_lead = FinalLead(
            auto_lead_id=auto_lead.id,
            company_name=auto_lead.company_name,
            website=auto_lead.website,
            linkedin_url=auto_lead.linkedin_url,
            email=auto_lead.email,
            phone=auto_lead.phone,
            address=auto_lead.address,
            industry=auto_lead.industry,
            employee_count=auto_lead.employee_count,
            revenue_range=auto_lead.revenue_range,
            keywords_matched=auto_lead.keywords_matched,
            relevance_score=auto_lead.relevance_score,
            approved_by=current_user.id
        )
        
        db.add(final_lead)
        
        # Update auto lead status
        auto_lead.status = LeadStatus.APPROVED
        auto_lead.is_selected = True
        
        finalized_count += 1
    
    db.commit()
    
    # Log activity
    ActivityLogger.log_activity(
        db, current_user, "finalize_leads", 
        f"Finalized {finalized_count} auto leads to final leads",
        request=request
    )
    
    return {"message": f"Successfully finalized {finalized_count} leads"}

# Final Leads endpoints
@router.get("/final", response_model=List[FinalLeadResponse])
async def get_final_leads(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    search: Optional[str] = Query(None, description="Search in company name, email, industry"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get final leads"""
    query = db.query(FinalLead)
    
    if status_filter:
        query = query.filter(FinalLead.status == status_filter)
    
    if assigned_to:
        query = query.filter(FinalLead.assigned_to == assigned_to)
    
    if search:
        query = query.filter(
            or_(
                FinalLead.company_name.contains(search),
                FinalLead.email.contains(search),
                FinalLead.industry.contains(search)
            )
        )
    
    leads = query.offset(skip).limit(limit).all()
    return [FinalLeadResponse.from_orm(lead) for lead in leads]

@router.post("/final", response_model=FinalLeadResponse)
async def create_final_lead(
    lead_data: FinalLeadCreate,
    request: Request,
    current_user: User = Depends(require_reviewer_or_above),
    db: Session = Depends(get_db)
):
    """Create new final lead"""
    db_lead = FinalLead(**lead_data.dict())
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log activity
    ActivityLogger.log_create(
        db, current_user, "final_lead", db_lead.id, db_lead.company_name, request
    )
    
    return FinalLeadResponse.from_orm(db_lead)

@router.put("/final/{lead_id}", response_model=FinalLeadResponse)
async def update_final_lead(
    lead_id: str,
    lead_update: FinalLeadUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update final lead"""
    lead = db.query(FinalLead).filter(FinalLead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Track changes for logging
    changes = {}
    update_data = lead_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(lead, field) and getattr(lead, field) != value:
            changes[field] = {"old": getattr(lead, field), "new": value}
            setattr(lead, field, value)
    
    if changes:
        db.commit()
        db.refresh(lead)
        
        # Log activity
        ActivityLogger.log_update(
            db, current_user, "final_lead", lead.id, lead.company_name, changes, request
        )
    
    return FinalLeadResponse.from_orm(lead)

@router.delete("/final/{lead_id}")
async def delete_final_lead(
    lead_id: str,
    request: Request,
    current_user: User = Depends(require_reviewer_or_above),
    db: Session = Depends(get_db)
):
    """Delete final lead"""
    lead = db.query(FinalLead).filter(FinalLead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    company_name = lead.company_name
    db.delete(lead)
    db.commit()
    
    # Log activity
    ActivityLogger.log_delete(
        db, current_user, "final_lead", lead_id, company_name, request
    )
    
    return {"message": "Lead deleted successfully"}

@router.get("/export")
async def export_leads(
    lead_type: str = Query("final", description="Type of leads to export: auto or final"),
    format: str = Query("csv", description="Export format: csv"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export leads to CSV"""
    if lead_type == "auto":
        leads = db.query(AutoLead).all()
        data = []
        for lead in leads:
            data.append({
                'Company Name': lead.company_name,
                'Website': lead.website or '',
                'Email': lead.email or '',
                'Phone': lead.phone or '',
                'Industry': lead.industry or '',
                'Employee Count': lead.employee_count or '',
                'Relevance Score': float(lead.relevance_score),
                'Status': lead.status.value,
                'Source': lead.source or '',
                'Created Date': lead.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
    else:
        leads = db.query(FinalLead).all()
        data = []
        for lead in leads:
            data.append({
                'Company Name': lead.company_name,
                'Website': lead.website or '',
                'Email': lead.email or '',
                'Phone': lead.phone or '',
                'Industry': lead.industry or '',
                'Employee Count': lead.employee_count or '',
                'Priority': lead.priority.value,
                'Status': lead.status.value,
                'Relevance Score': float(lead.relevance_score),
                'Assigned To': lead.assigned_user.full_name if lead.assigned_user else '',
                'Last Contact': lead.last_contact_date.strftime('%Y-%m-%d') if lead.last_contact_date else '',
                'Next Follow Up': lead.next_follow_up.strftime('%Y-%m-%d') if lead.next_follow_up else '',
                'Approved Date': lead.approved_at.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Create CSV
    df = pd.DataFrame(data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Log export activity
    ActivityLogger.log_export(
        db, current_user, f"{lead_type}_leads", len(data)
    )
    
    # Return CSV response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={lead_type}_leads.csv"}
    )