from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityLogResponse
from app.auth import require_admin, get_current_user

router = APIRouter()

@router.get("/", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity logs"""
    # Non-admin users can only see their own activity logs
    if current_user.role.value != "admin":
        user_id = current_user.id
    
    query = db.query(ActivityLog)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    if activity_type:
        query = query.filter(ActivityLog.activity_type == activity_type)
    
    logs = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()
    return [ActivityLogResponse.from_orm(log) for log in logs]

@router.get("/recent", response_model=List[ActivityLogResponse])
async def get_recent_activity(
    limit: int = Query(10, description="Number of recent activities to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recent system activity (Admin only)"""
    logs = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).limit(limit).all()
    
    return [ActivityLogResponse.from_orm(log) for log in logs]