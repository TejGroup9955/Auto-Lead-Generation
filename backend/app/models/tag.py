from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class LeadTag(Base):
    __tablename__ = "lead_tags"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#3b82f6")  # Hex color
    description = Column(String(500))
    created_by = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", backref="created_tags")

class LeadTagAssignment(Base):
    __tablename__ = "lead_tag_assignments"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(CHAR(36), nullable=False)  # Can reference auto_leads or final_leads
    lead_type = Column(String(10), nullable=False)  # 'auto' or 'final'
    tag_id = Column(CHAR(36), ForeignKey("lead_tags.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('lead_id', 'tag_id', 'lead_type'),)
    
    # Relationships
    tag = relationship("LeadTag", backref="assignments")