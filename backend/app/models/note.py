from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class LeadNote(Base):
    __tablename__ = "lead_notes"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(CHAR(36), nullable=False)  # Can reference auto_leads or final_leads
    lead_type = Column(String(10), nullable=False)  # 'auto' or 'final'
    note = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True)
    created_by = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="lead_notes")