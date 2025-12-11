"""
Bird management API routes.
Provides CRUD endpoints for bird management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.schemas.auth import TokenData
from api.app.schemas.bird import BirdCreate, BirdUpdate, BirdResponse
from api.app.dependencies import get_current_user, get_db
from api.app.crud.bird_crud import BirdCRUD

authenticated_router = APIRouter(prefix="/birds", tags=["birds"], dependencies=[Depends(get_current_user)])


@authenticated_router.post("/", response_model=BirdResponse, status_code=status.HTTP_201_CREATED)
async def create_bird(
    bird_data: BirdCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new bird.
    Requires authentication.
    """
    # Check if band_id already exists
    if BirdCRUD.bird_exists_by_band_id(db, bird_data.band_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Band ID already exists"
        )

    bird = BirdCRUD.create_bird(db, bird_data)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create bird"
        )

    return bird


@authenticated_router.get("/", response_model=list[BirdResponse])
async def list_birds(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all birds with pagination.
    Requires authentication.
    """
    birds = BirdCRUD.get_all_birds(db, skip=skip, limit=limit)
    return birds


@authenticated_router.get("/stats/total", response_model=dict)
async def get_bird_stats(
    db: Session = Depends(get_db)
):
    """
    Get bird statistics.
    Requires authentication.
    """
    total = BirdCRUD.count_birds(db)
    males = BirdCRUD.count_birds_by_sex(db, "M")
    females = BirdCRUD.count_birds_by_sex(db, "F")

    return {
        "total_birds": total,
        "males": males,
        "females": females
    }


@authenticated_router.get("/breeder/{breeder_id}", response_model=list[BirdResponse])
async def get_birds_by_breeder(
    breeder_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all birds for a specific breeder.
    Requires authentication.
    """
    birds = BirdCRUD.get_birds_by_breeder(db, breeder_id, skip=skip, limit=limit)
    return birds


@authenticated_router.get("/owner/{owner_id}", response_model=list[BirdResponse])
async def get_birds_by_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all birds for a specific owner.
    Requires authentication.
    """
    birds = BirdCRUD.get_birds_by_owner(db, owner_id, skip=skip, limit=limit)
    return birds


@authenticated_router.get("/sex/{sex}", response_model=list[BirdResponse])
async def get_birds_by_sex(
    sex: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all birds by sex (M for male, F for female).
    Requires authentication.
    """
    if sex not in ["M", "F"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sex must be 'M' or 'F'"
        )

    birds = BirdCRUD.get_birds_by_sex(db, sex, skip=skip, limit=limit)
    return birds


@authenticated_router.get("/band/{band_id}", response_model=BirdResponse)
async def get_bird_by_band(
    band_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a bird by band ID.
    Requires authentication.
    """
    bird = BirdCRUD.get_bird_by_band_id(db, band_id)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    return bird


@authenticated_router.get("/{bird_id}", response_model=BirdResponse)
async def get_bird(
    bird_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a bird by ID.
    Requires authentication.
    """
    bird = BirdCRUD.get_bird_by_id(db, bird_id)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    return bird


@authenticated_router.get("/{bird_id}/offspring", response_model=list[BirdResponse])
async def get_bird_offspring(
    bird_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all offspring of a bird (birds where this bird is father or mother).
    Requires authentication.
    """
    # First check if parent bird exists
    parent = BirdCRUD.get_bird_by_id(db, bird_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent bird not found"
        )

    offspring = BirdCRUD.get_offspring(db, bird_id)
    return offspring


@authenticated_router.put("/{bird_id}", response_model=BirdResponse)
async def update_bird(
    bird_id: int,
    bird_data: BirdUpdate,
    db: Session = Depends(get_db)
):
    """
    Update bird information.
    Requires authentication.
    """
    bird = BirdCRUD.update_bird(db, bird_id, bird_data)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    return bird


@authenticated_router.delete("/{bird_id}")
async def delete_bird(
    bird_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a bird.
    Requires authentication.
    """
    success = BirdCRUD.delete_bird(db, bird_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    return {"message": "Bird deleted successfully"}


# Export router for use in main app
router = authenticated_router
