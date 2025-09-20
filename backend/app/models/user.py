from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALES_COORDINATOR = "sales_coordinator"
    REVIEWER = "reviewer"
    BDM = "bdm"

class User(Base):
    __tablename__ = "users"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.BDM, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())