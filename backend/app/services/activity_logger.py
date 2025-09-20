from sqlalchemy.orm import Session
from app.models.activity import ActivityLog
from app.models.user import User
from typing import Optional, Dict, Any
from fastapi import Request

class ActivityLogger:
    @staticmethod
    def log_activity(
        db: Session,
        user: User,
        activity_type: str,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log user activity"""
        try:
            # Extract IP and user agent from request if provided
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            
            # Create activity log entry
            activity_log = ActivityLog(
                user_id=user.id,
                activity_type=activity_type,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(activity_log)
            db.commit()
            
        except Exception as e:
            print(f"Activity logging error: {e}")
            db.rollback()
    
    @staticmethod
    def log_login(db: Session, user: User, request: Optional[Request] = None):
        """Log user login"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="login",
            description=f"User {user.full_name} logged in",
            request=request
        )
    
    @staticmethod
    def log_logout(db: Session, user: User, request: Optional[Request] = None):
        """Log user logout"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="logout",
            description=f"User {user.full_name} logged out",
            request=request
        )
    
    @staticmethod
    def log_create(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        request: Optional[Request] = None
    ):
        """Log entity creation"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="create",
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"User {user.full_name} created {entity_type}: {entity_name}",
            request=request
        )
    
    @staticmethod
    def log_update(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log entity update"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="update",
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"User {user.full_name} updated {entity_type}: {entity_name}",
            metadata={"changes": changes} if changes else None,
            request=request
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        request: Optional[Request] = None
    ):
        """Log entity deletion"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="delete",
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"User {user.full_name} deleted {entity_type}: {entity_name}",
            request=request
        )
    
    @staticmethod
    def log_export(
        db: Session,
        user: User,
        export_type: str,
        record_count: int,
        request: Optional[Request] = None
    ):
        """Log data export"""
        ActivityLogger.log_activity(
            db=db,
            user=user,
            activity_type="export",
            description=f"User {user.full_name} exported {record_count} {export_type} records",
            metadata={"export_type": export_type, "record_count": record_count},
            request=request
        )