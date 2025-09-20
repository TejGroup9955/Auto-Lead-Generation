from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from app.models.lead import LeadStatus, LeadPriority
from app.schemas.user import UserResponse

class AutoLeadBase(BaseModel):
    company_name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    revenue_range: Optional[str] = None
    keywords_matched: List[str] = []
    relevance_score: Decimal = Decimal('0.0')
    source: Optional[str] = None

class AutoLeadCreate(AutoLeadBase):
    campaign_id: str
    raw_data: Optional[dict] = None

class AutoLeadResponse(AutoLeadBase):
    id: str
    campaign_id: str
    status: LeadStatus
    is_selected: bool
    raw_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FinalLeadBase(BaseModel):
    company_name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    revenue_range: Optional[str] = None
    keywords_matched: List[str] = []
    relevance_score: Decimal = Decimal('0.0')
    priority: LeadPriority = LeadPriority.MEDIUM
    assigned_to: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    conversion_probability: Optional[Decimal] = None
    notes: Optional[str] = None

class FinalLeadCreate(FinalLeadBase):
    auto_lead_id: Optional[str] = None
    approved_by: str

class FinalLeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    assigned_to: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    conversion_probability: Optional[Decimal] = None
    notes: Optional[str] = None

class FinalLeadResponse(FinalLeadBase):
    id: str
    auto_lead_id: Optional[str] = None
    status: LeadStatus
    approved_by: str
    approved_at: datetime
    created_at: datetime
    updated_at: datetime
    assigned_user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True