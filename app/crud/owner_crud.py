"""
CRUD operations for Owner model.
"""

from sqlalchemy.orm import Session
from api.app.models.owner import Owner
from api.app.schemas.owner import OwnerCreate, OwnerUpdate


def get_owner(db: Session, owner_id: int):
    """Get owner by ID."""
    return db.query(Owner).filter(Owner.id == owner_id).first()


def get_owners(db: Session, skip: int = 0, limit: int = 100):
    """Get all owners with pagination."""
    return db.query(Owner).offset(skip).limit(limit).all()


def get_owners_by_name(db: Session, name: str, skip: int = 0, limit: int = 100):
    """Search owners by first name or last name."""
    search_pattern = f"%{name}%"
    return db.query(Owner).filter(
        (Owner.first_name.ilike(search_pattern)) | (Owner.last_name.ilike(search_pattern))
    ).offset(skip).limit(limit).all()


def create_owner(db: Session, owner: OwnerCreate):
    """Create a new owner."""
    db_owner = Owner(**owner.model_dump())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner


def update_owner(db: Session, owner_id: int, owner: OwnerUpdate):
    """Update an owner."""
    db_owner = get_owner(db, owner_id)
    if not db_owner:
        return None

    update_data = owner.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_owner, field, value)

    db.commit()
    db.refresh(db_owner)
    return db_owner


def delete_owner(db: Session, owner_id: int):
    """Delete an owner."""
    db_owner = get_owner(db, owner_id)
    if not db_owner:
        return None

    db.delete(db_owner)
    db.commit()
    return db_owner

