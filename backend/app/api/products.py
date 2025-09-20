from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.auth import require_admin, get_current_user
from app.services.activity_logger import ActivityLogger

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search products by name or keywords"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active products"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.offset(skip).limit(limit).all()
    return [ProductResponse.from_orm(product) for product in products]

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new product (Admin only)"""
    db_product = Product(
        name=product_data.name,
        description=product_data.description,
        keywords=product_data.keywords,
        created_by=current_user.id
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Log activity
    ActivityLogger.log_create(
        db, current_user, "product", db_product.id, db_product.name, request
    )
    
    return ProductResponse.from_orm(db_product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product by ID"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse.from_orm(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update product (Admin only)"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Track changes for logging
    changes = {}
    update_data = product_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(product, field) and getattr(product, field) != value:
            changes[field] = {"old": getattr(product, field), "new": value}
            setattr(product, field, value)
    
    if changes:
        db.commit()
        db.refresh(product)
        
        # Log activity
        ActivityLogger.log_update(
            db, current_user, "product", product.id, product.name, changes, request
        )
    
    return ProductResponse.from_orm(product)

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Soft delete product (Admin only)"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = False
    db.commit()
    
    # Log activity
    ActivityLogger.log_delete(
        db, current_user, "product", product.id, product.name, request
    )
    
    return {"message": "Product deleted successfully"}