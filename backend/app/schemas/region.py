from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegionResponse(BaseModel):
    id: str
    name: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True