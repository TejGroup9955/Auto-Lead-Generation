from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.campaign import CampaignStatus
from app.schemas.product import ProductResponse
from app.schemas.region import RegionResponse

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_id: str
    region_id: str
    keywords: List[str] = []
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_id: Optional[str] = None
    region_id: Optional[str] = None
    keywords: Optional[List[str]] = None
    status: Optional[CampaignStatus] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: str
    status: CampaignStatus
    leads_generated: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None
    region: Optional[RegionResponse] = None
    
    class Config:
        from_attributes = True