"""
CRUD operations for Pairs model.
"""

from sqlalchemy.orm import Session
from api.app.models.pairs import Pairs
from api.app.schemas.pairs import PairsCreate, PairsUpdate


def get_pair(db: Session, pair_id: int):
    """Get pair by ID."""
    return db.query(Pairs).filter(Pairs.id == pair_id).first()


def get_pairs(db: Session, skip: int = 0, limit: int = 100):
    """Get all pairs with pagination."""
    return db.query(Pairs).offset(skip).limit(limit).all()


def get_pairs_by_season(db: Session, season: int, skip: int = 0, limit: int = 100):
    """Get pairs by breeding season."""
    return db.query(Pairs).filter(Pairs.season == season).offset(skip).limit(limit).all()


def get_pairs_by_bird(db: Session, bird_id: int, skip: int = 0, limit: int = 100):
    """Get pairs where bird is either cock or hen."""
    return db.query(Pairs).filter(
        (Pairs.cock == bird_id) | (Pairs.hen == bird_id)
    ).offset(skip).limit(limit).all()


def get_pairs_by_cock(db: Session, cock_id: int, skip: int = 0, limit: int = 100):
    """Get pairs where bird is the cock (male)."""
    return db.query(Pairs).filter(Pairs.cock == cock_id).offset(skip).limit(limit).all()


def get_pairs_by_hen(db: Session, hen_id: int, skip: int = 0, limit: int = 100):
    """Get pairs where bird is the hen (female)."""
    return db.query(Pairs).filter(Pairs.hen == hen_id).offset(skip).limit(limit).all()


def get_pairs_by_season_and_round(db: Session, season: int, round: int, skip: int = 0, limit: int = 100):
    """Get pairs by season and round."""
    return db.query(Pairs).filter(
        (Pairs.season == season) & (Pairs.round == round)
    ).offset(skip).limit(limit).all()


def get_pair_by_composite_key(db: Session, cock_id: int, hen_id: int, season: int, round: int):
    """Get pair by composite key: cock, hen, season, round."""
    return db.query(Pairs).filter(
        (Pairs.cock == cock_id) & (Pairs.hen == hen_id) &
        (Pairs.season == season) & (Pairs.round == round)
    ).first()


def create_pair(db: Session, pair: PairsCreate):
    """Create a new pair."""
    db_pair = Pairs(**pair.model_dump())
    db.add(db_pair)
    db.commit()
    db.refresh(db_pair)
    return db_pair


def update_pair(db: Session, pair_id: int, pair: PairsUpdate):
    """Update a pair."""
    db_pair = get_pair(db, pair_id)
    if not db_pair:
        return None

    update_data = pair.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pair, field, value)

    db.commit()
    db.refresh(db_pair)
    return db_pair


def delete_pair(db: Session, pair_id: int):
    """Delete a pair."""
    db_pair = get_pair(db, pair_id)
    if not db_pair:
        return None

    db.delete(db_pair)
    db.commit()
    return db_pair


def count_pairs(db: Session):
    """Get total number of pairs."""
    return db.query(Pairs).count()


def count_pairs_by_season(db: Session, season: int):
    """Get total number of pairs in a season."""
    return db.query(Pairs).filter(Pairs.season == season).count()

