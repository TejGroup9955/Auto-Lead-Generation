from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class LeadNoteBase(BaseModel):
    note: str
    is_internal: bool = True

class LeadNoteCreate(LeadNoteBase):
    lead_id: str
    lead_type: str  # 'auto' or 'final'

class LeadNoteResponse(LeadNoteBase):
    id: str
    lead_id: str
    lead_type: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True