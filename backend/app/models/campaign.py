from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.mysql import CHAR, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid

class CampaignStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    product_id = Column(CHAR(36), ForeignKey("products.id"))
    region_id = Column(CHAR(36), ForeignKey("regions.id"))
    keywords = Column(JSON)  # Store as JSON array
    status = Column(Enum(CampaignStatus), default=CampaignStatus.SCHEDULED)
    scheduled_at = Column(DateTime(timezone=True))
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # weekly, monthly, etc.
    leads_generated = Column(Integer, default=0)
    created_by = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="campaigns")
    region = relationship("Region", back_populates="campaigns")
    creator = relationship("User", backref="created_campaigns")
    auto_leads = relationship("AutoLead", back_populates="campaign")