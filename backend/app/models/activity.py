from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"))
    activity_type = Column(String(50), nullable=False)  # login, create, update, etc.
    entity_type = Column(String(50))  # lead, campaign, product, etc.
    entity_id = Column(CHAR(36))
    description = Column(Text, nullable=False)
    metadata = Column(JSON)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="activity_logs")