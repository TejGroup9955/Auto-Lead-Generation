from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.mysql import CHAR, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid

class LeadStatus(str, enum.Enum):
    GENERATED = "generated"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONTACTED = "contacted"

class LeadPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AutoLead(Base):
    __tablename__ = "auto_leads"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(CHAR(36), ForeignKey("campaigns.id"))
    company_name = Column(String(255), nullable=False)
    website = Column(String(500))
    linkedin_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    industry = Column(String(255))
    employee_count = Column(String(50))
    revenue_range = Column(String(50))
    keywords_matched = Column(JSON)  # Store as JSON array
    relevance_score = Column(Numeric(3, 2), default=0.0)
    status = Column(Enum(LeadStatus), default=LeadStatus.GENERATED)
    is_selected = Column(Boolean, default=False)
    source = Column(String(100))  # duckduckgo, opencorporates, etc.
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="auto_leads")
    final_lead = relationship("FinalLead", back_populates="auto_lead", uselist=False)

class FinalLead(Base):
    __tablename__ = "final_leads"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auto_lead_id = Column(CHAR(36), ForeignKey("auto_leads.id"))
    company_name = Column(String(255), nullable=False)
    website = Column(String(500))
    linkedin_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    industry = Column(String(255))
    employee_count = Column(String(50))
    revenue_range = Column(String(50))
    keywords_matched = Column(JSON)
    relevance_score = Column(Numeric(3, 2), default=0.0)
    status = Column(Enum(LeadStatus), default=LeadStatus.APPROVED)
    priority = Column(Enum(LeadPriority), default=LeadPriority.MEDIUM)
    assigned_to = Column(CHAR(36), ForeignKey("users.id"))
    last_contact_date = Column(DateTime(timezone=True))
    next_follow_up = Column(DateTime(timezone=True))
    conversion_probability = Column(Numeric(3, 2))
    notes = Column(Text)
    approved_by = Column(CHAR(36), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    auto_lead = relationship("AutoLead", back_populates="final_lead")
    assigned_user = relationship("User", foreign_keys=[assigned_to], backref="assigned_leads")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_leads")