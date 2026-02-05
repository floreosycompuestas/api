"""
Bird management API routes.
Provides CRUD endpoints for bird management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

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
    Uses father_band_id and mother_band_id to resolve parent birds.
    If parent birds don't exist, they are automatically created with appropriate sex.

    Band ID can be:
    - Provided directly via band_id field, OR
    - Auto-generated from breeder_code-bird_year-bird_number

    Requires authentication.
    """
    # Check if band_id already exists (only if provided)
    if bird_data.band_id and BirdCRUD.bird_exists_by_band_id(db, bird_data.band_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Band ID already exists"
        )

    try:
        bird = BirdCRUD.create_bird(db, bird_data)
        if not bird:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create bird"
            )
        return bird
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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


@authenticated_router.get("/breeder/{breeder_id}/{bird_id}", response_model=BirdResponse)
async def get_bird_by_breeder_and_id(
    breeder_id: int,
    bird_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific bird by breeder ID and bird ID.
    Ensures the bird belongs to the specified breeder.
    Requires authentication.
    """
    bird = BirdCRUD.get_bird_by_id(db, bird_id)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    # Verify the bird belongs to the specified breeder
    if bird.breeder_id != breeder_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird does not belong to the specified breeder"
        )

    return bird


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


@authenticated_router.get("/band/{band_id}/sex/{sex}", response_model=BirdResponse)
async def get_bird_by_band_and_sex(
    band_id: str,
    sex: str,
    db: Session = Depends(get_db)
):
    """
    Get a bird by band ID and sex.
    Validates that the bird matches both criteria.
    Requires authentication.

    Example:
        GET /birds/band/2024-001/sex/M
    """
    if sex not in ["M", "F"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sex must be 'M' or 'F'"
        )

    bird = BirdCRUD.get_bird_by_band_id(db, band_id)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found"
        )

    # Verify the bird has the specified sex
    if bird.sex != sex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bird with band ID '{band_id}' is not {sex} (found: {bird.sex})"
        )

    return bird


@authenticated_router.get("/breeder-code/{breeder_code}/band/{band_id}", response_model=BirdResponse)
async def get_bird_by_breeder_code_and_band(
    breeder_code: str,
    band_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a bird by breeder code and band ID.
    This allows retrieving a specific bird using business identifiers
    instead of database IDs.
    Requires authentication.

    Example:
        GET /birds/breeder-code/BR001/band/2024-001
    """
    bird = BirdCRUD.get_bird_by_breeder_code_and_band_id(db, breeder_code, band_id)
    if not bird:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bird not found for the specified breeder code and band ID"
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
