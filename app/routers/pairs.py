"""
Router for Pairs endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.app.dependencies import get_db
from api.app.crud.pairs_crud import (
    get_pair,
    get_pairs,
    get_pairs_by_season,
    get_pairs_by_bird,
    get_pairs_by_cock,
    get_pairs_by_hen,
    get_pairs_by_season_and_round,
    get_pair_by_composite_key,
    create_pair,
    update_pair,
    delete_pair,
    count_pairs,
)
from api.app.schemas.pairs import PairsCreate, PairsUpdate, PairsResponse

router = APIRouter(prefix="/pairs", tags=["pairs"])


@router.get("/", response_model=list[PairsResponse])
def list_pairs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all pairs with pagination."""
    pairs = get_pairs(db, skip=skip, limit=limit)
    return pairs


@router.get("/stats", response_model=dict)
def get_pairs_stats(db: Session = Depends(get_db)):
    """Get pairs statistics."""
    total = count_pairs(db)
    return {
        "total_pairs": total
    }


@router.get("/{pair_id}", response_model=PairsResponse)
def read_pair(pair_id: int, db: Session = Depends(get_db)):
    """Get pair by ID."""
    pair = get_pair(db, pair_id)
    if not pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pair not found")
    return pair


@router.get("/season/{season}", response_model=list[PairsResponse])
def get_pairs_in_season(season: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get pairs by breeding season."""
    pairs = get_pairs_by_season(db, season, skip=skip, limit=limit)
    return pairs


@router.get("/season/{season}/round/{round}", response_model=list[PairsResponse])
def get_pairs_in_season_and_round(season: int, round: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get pairs by season and round."""
    pairs = get_pairs_by_season_and_round(db, season, round, skip=skip, limit=limit)
    return pairs


@router.get("/bird/{bird_id}", response_model=list[PairsResponse])
def get_pairs_for_bird(bird_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get pairs where bird is either cock or hen."""
    pairs = get_pairs_by_bird(db, bird_id, skip=skip, limit=limit)
    return pairs


@router.get("/cock/{cock_id}", response_model=list[PairsResponse])
def get_pairs_for_cock(cock_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get pairs where bird is the cock (male)."""
    pairs = get_pairs_by_cock(db, cock_id, skip=skip, limit=limit)
    return pairs


@router.get("/hen/{hen_id}", response_model=list[PairsResponse])
def get_pairs_for_hen(hen_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get pairs where bird is the hen (female)."""
    pairs = get_pairs_by_hen(db, hen_id, skip=skip, limit=limit)
    return pairs


@router.post("/", response_model=PairsResponse, status_code=status.HTTP_201_CREATED)
def create_new_pair(pair: PairsCreate, db: Session = Depends(get_db)):
    """Create a new pair."""
    # Check if this pair combination already exists
    existing = get_pair_by_composite_key(db, pair.cock, pair.hen, pair.season, pair.round)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This pair combination (cock, hen, season, round) already exists"
        )
    return create_pair(db, pair)


@router.put("/{pair_id}", response_model=PairsResponse)
def update_existing_pair(
    pair_id: int,
    pair: PairsUpdate,
    db: Session = Depends(get_db)
):
    """Update a pair."""
    db_pair = update_pair(db, pair_id, pair)
    if not db_pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pair not found")
    return db_pair


@router.delete("/{pair_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_pair(pair_id: int, db: Session = Depends(get_db)):
    """Delete a pair."""
    pair = delete_pair(db, pair_id)
    if not pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pair not found")
    return None

