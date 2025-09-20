from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tag import LeadTag, LeadTagAssignment
from app.models.user import User
from app.schemas.tag import LeadTagCreate, LeadTagResponse, LeadTagAssignmentCreate
from app.auth import get_current_user
from app.services.activity_logger import ActivityLogger

router = APIRouter()

@router.get("/", response_model=List[LeadTagResponse])
async def get_lead_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lead tags"""
    tags = db.query(LeadTag).all()
    return [LeadTagResponse.from_orm(tag) for tag in tags]

@router.post("/", response_model=LeadTagResponse)
async def create_lead_tag(
    tag_data: LeadTagCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new lead tag"""
    # Check if tag name already exists
    existing_tag = db.query(LeadTag).filter(LeadTag.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )
    
    db_tag = LeadTag(
        name=tag_data.name,
        color=tag_data.color,
        description=tag_data.description,
        created_by=current_user.id
    )
    
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    
    # Log activity
    ActivityLogger.log_create(
        db, current_user, "lead_tag", db_tag.id, db_tag.name, request
    )
    
    return LeadTagResponse.from_orm(db_tag)

@router.post("/assign")
async def assign_tag_to_lead(
    assignment_data: LeadTagAssignmentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign tag to lead"""
    # Check if assignment already exists
    existing_assignment = db.query(LeadTagAssignment).filter(
        LeadTagAssignment.lead_id == assignment_data.lead_id,
        LeadTagAssignment.tag_id == assignment_data.tag_id,
        LeadTagAssignment.lead_type == assignment_data.lead_type
    ).first()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already assigned to this lead"
        )
    
    db_assignment = LeadTagAssignment(
        lead_id=assignment_data.lead_id,
        lead_type=assignment_data.lead_type,
        tag_id=assignment_data.tag_id
    )
    
    db.add(db_assignment)
    db.commit()
    
    # Log activity
    tag = db.query(LeadTag).filter(LeadTag.id == assignment_data.tag_id).first()
    ActivityLogger.log_activity(
        db, current_user, "assign_tag",
        f"Assigned tag '{tag.name}' to {assignment_data.lead_type} lead",
        assignment_data.lead_type + "_lead", assignment_data.lead_id, request=request
    )
    
    return {"message": "Tag assigned successfully"}

@router.delete("/assign/{assignment_id}")
async def remove_tag_from_lead(
    assignment_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove tag assignment from lead"""
    assignment = db.query(LeadTagAssignment).filter(
        LeadTagAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag assignment not found"
        )
    
    tag = db.query(LeadTag).filter(LeadTag.id == assignment.tag_id).first()
    db.delete(assignment)
    db.commit()
    
    # Log activity
    ActivityLogger.log_activity(
        db, current_user, "remove_tag",
        f"Removed tag '{tag.name}' from {assignment.lead_type} lead",
        assignment.lead_type + "_lead", assignment.lead_id, request=request
    )
    
    return {"message": "Tag removed successfully"}