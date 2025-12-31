"""
Router for Owner endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.app.dependencies import get_db
from api.app.crud.owner_crud import (
    get_owner,
    get_owners,
    get_owners_by_name,
    create_owner,
    update_owner,
    delete_owner,
)
from api.app.schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse

router = APIRouter(prefix="/owners", tags=["owners"])


@router.get("/", response_model=list[OwnerResponse])
def list_owners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all owners."""
    owners = get_owners(db, skip=skip, limit=limit)
    return owners


@router.get("/{owner_id}", response_model=OwnerResponse)
def read_owner(owner_id: int, db: Session = Depends(get_db)):
    """Get owner by ID."""
    owner = get_owner(db, owner_id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    return owner


@router.get("/search/{name}", response_model=list[OwnerResponse])
def search_owners(name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Search owners by first name or last name."""
    if len(name) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search name must be at least 1 character"
        )
    owners = get_owners_by_name(db, name, skip=skip, limit=limit)
    return owners


@router.post("/", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
def create_new_owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    """Create a new owner."""
    return create_owner(db, owner)


@router.put("/{owner_id}", response_model=OwnerResponse)
def update_existing_owner(
    owner_id: int,
    owner: OwnerUpdate,
    db: Session = Depends(get_db)
):
    """Update an owner."""
    db_owner = update_owner(db, owner_id, owner)
    if not db_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    return db_owner


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_owner(owner_id: int, db: Session = Depends(get_db)):
    """Delete an owner."""
    owner = delete_owner(db, owner_id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    return None

