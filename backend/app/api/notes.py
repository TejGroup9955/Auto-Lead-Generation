from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.note import LeadNote
from app.models.user import User
from app.schemas.note import LeadNoteCreate, LeadNoteResponse
from app.auth import get_current_user
from app.services.activity_logger import ActivityLogger

router = APIRouter()

@router.get("/", response_model=List[LeadNoteResponse])
async def get_lead_notes(
    lead_id: str = Query(..., description="Lead ID"),
    lead_type: str = Query(..., description="Lead type: auto or final"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notes for a specific lead"""
    notes = db.query(LeadNote).filter(
        LeadNote.lead_id == lead_id,
        LeadNote.lead_type == lead_type
    ).order_by(LeadNote.created_at.desc()).all()
    
    return [LeadNoteResponse.from_orm(note) for note in notes]

@router.post("/", response_model=LeadNoteResponse)
async def create_lead_note(
    note_data: LeadNoteCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new lead note"""
    db_note = LeadNote(
        lead_id=note_data.lead_id,
        lead_type=note_data.lead_type,
        note=note_data.note,
        is_internal=note_data.is_internal,
        created_by=current_user.id
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Log activity
    ActivityLogger.log_activity(
        db, current_user, "create_note",
        f"Added note to {note_data.lead_type} lead",
        note_data.lead_type + "_lead", note_data.lead_id, request=request
    )
    
    return LeadNoteResponse.from_orm(db_note)

@router.delete("/{note_id}")
async def delete_lead_note(
    note_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete lead note"""
    note = db.query(LeadNote).filter(LeadNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Only allow deletion by note creator or admin
    if note.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(note)
    db.commit()
    
    # Log activity
    ActivityLogger.log_activity(
        db, current_user, "delete_note",
        f"Deleted note from {note.lead_type} lead",
        note.lead_type + "_lead", note.lead_id, request=request
    )
    
    return {"message": "Note deleted successfully"}