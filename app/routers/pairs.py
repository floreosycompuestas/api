"""
Pairs management API routes.
Provides CRUD endpoints for pairs management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.schemas.pairs import PairsCreate, PairsUpdate, PairsResponse
from api.app.dependencies import get_current_user, get_db
from api.app.crud.pairs_crud import PairsCRUD

authenticated_router = APIRouter(prefix="/pairs", tags=["pairs"], dependencies=[Depends(get_current_user)])


@authenticated_router.post("/", response_model=PairsResponse, status_code=status.HTTP_201_CREATED)
async def create_pair(
    pair_data: PairsCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new pair.

    Supports two ways to specify birds:
    1. Using cock/hen IDs: Provide cock and hen (numeric IDs)
    2. Using band IDs: Provide cock_band_id and hen_band_id (auto-creates birds if they don't exist)

    Priority: If both cock and cock_band_id are provided, cock (ID) takes precedence.

    Validates that cock is male and hen is female.
    Checks for duplicate combinations (cock, hen, season, clutch).

    Requires authentication.
    """
    try:
        pair = PairsCRUD.create_pair(db, pair_data)
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create pair"
            )
        return pair
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@authenticated_router.get("/", response_model=list[PairsResponse])
async def list_pairs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all pairs with pagination.
    Requires authentication.
    """
    pairs = PairsCRUD.get_all_pairs(db, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/stats/total", response_model=dict)
async def get_pair_stats(
    db: Session = Depends(get_db)
):
    """
    Get pair statistics.
    Requires authentication.
    """
    total = PairsCRUD.count_pairs(db)

    return {
        "total_pairs": total
    }


@authenticated_router.get("/season/{season}", response_model=list[PairsResponse])
async def get_pairs_by_season(
    season: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all pairs for a specific season.
    Requires authentication.
    """
    pairs = PairsCRUD.get_pairs_by_season(db, season, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/season/{season}/clutch/{clutch}", response_model=list[PairsResponse])
async def get_pairs_by_season_and_clutch(
    season: int,
    clutch: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get pairs by season and clutch.
    Requires authentication.
    """
    pairs = PairsCRUD.get_pairs_by_season_and_clutch(db, season, clutch, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/bird/{bird_id}", response_model=list[PairsResponse])
async def get_pairs_by_bird(
    bird_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all pairs where bird is either cock or hen.
    Requires authentication.
    """
    pairs = PairsCRUD.get_pairs_by_bird(db, bird_id, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/cock/{cock_id}", response_model=list[PairsResponse])
async def get_pairs_by_cock(
    cock_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get pairs where bird is the cock (male).
    Requires authentication.
    """
    pairs = PairsCRUD.get_pairs_by_cock(db, cock_id, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/hen/{hen_id}", response_model=list[PairsResponse])
async def get_pairs_by_hen(
    hen_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get pairs where bird is the hen (female).
    Requires authentication.
    """
    pairs = PairsCRUD.get_pairs_by_hen(db, hen_id, skip=skip, limit=limit)
    return pairs


@authenticated_router.get("/{pair_id}", response_model=PairsResponse)
async def get_pair(
    pair_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a pair by ID.
    Requires authentication.
    """
    pair = PairsCRUD.get_pair_by_id(db, pair_id)
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pair not found"
        )

    return pair


@authenticated_router.put("/{pair_id}", response_model=PairsResponse)
async def update_pair(
    pair_id: int,
    pair_data: PairsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update pair information.

    Supports two ways to update birds:
    1. Using cock/hen IDs: Provide cock and hen (numeric IDs)
    2. Using band IDs: Provide cock_band_id and hen_band_id (auto-creates birds if they don't exist)

    Priority: If both cock and cock_band_id are provided, cock (ID) takes precedence.

    Validates sex if cock or hen is being updated.
    Checks for duplicate combinations if composite key fields are updated.

    Requires authentication.
    """
    try:
        pair = PairsCRUD.update_pair(db, pair_id, pair_data)
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pair not found"
            )
        return pair
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@authenticated_router.delete("/{pair_id}")
async def delete_pair(
    pair_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a pair.
    Requires authentication.
    """
    success = PairsCRUD.delete_pair(db, pair_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pair not found"
        )

    return {"message": "Pair deleted successfully"}


# Export router for use in main app
router = authenticated_router


