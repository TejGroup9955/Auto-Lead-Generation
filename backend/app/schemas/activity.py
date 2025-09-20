from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from app.schemas.user import UserResponse

class ActivityLogResponse(BaseModel):
    id: str
    user_id: str
    activity_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: str
    metadata: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True