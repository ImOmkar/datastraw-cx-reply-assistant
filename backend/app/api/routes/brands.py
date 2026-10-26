
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.brand import Brand
from backend.app.schemas.brand import BrandCreate, BrandResponse


router = APIRouter(prefix="/brands", tags=["Brands"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_brand(
    brand_data: BrandCreate,
    db: Session = Depends(get_db),
):
    existing_brand = (
        db.query(Brand)
        .filter(Brand.name == brand_data.name)
        .first()
    )

    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A brand with this name already exists.",
        )

    brand = Brand(
        name=brand_data.name,
        description=brand_data.description,
    )

    db.add(brand)
    db.commit()
    db.refresh(brand)

    return brand




@router.get(
    "/",
    response_model=list[BrandResponse],
)
def list_brands(
    db: Session = Depends(get_db),
):
    return db.query(Brand).order_by(Brand.id).all()




@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int, 
    db: Session = Depends(get_db),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found."
        )
        
    return brand
    