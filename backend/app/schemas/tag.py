from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LeadTagBase(BaseModel):
    name: str
    color: str = "#3b82f6"
    description: Optional[str] = None

class LeadTagCreate(LeadTagBase):
    pass

class LeadTagResponse(LeadTagBase):
    id: str
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeadTagAssignmentCreate(BaseModel):
    lead_id: str
    lead_type: str  # 'auto' or 'final'
    tag_id: str