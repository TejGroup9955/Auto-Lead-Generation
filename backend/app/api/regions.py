from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.region import Region
from app.models.user import User
from app.schemas.region import RegionResponse
from app.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[RegionResponse])
async def get_regions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active regions"""
    regions = db.query(Region).filter(Region.is_active == True).offset(skip).limit(limit).all()
    return [RegionResponse.from_orm(region) for region in regions]