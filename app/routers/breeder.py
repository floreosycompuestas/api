"""
Breeder management API routes.
Provides CRUD endpoints for breeder management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.crud.breeder_crud import BreederCRUD
from api.app.dependencies import get_current_user, get_db
from api.app.schemas.breeder import BreederCreate, BreederUpdate, BreederResponse

authenticated_router = APIRouter(prefix="/breeders", tags=["breeders"], dependencies=[Depends(get_current_user)])


@authenticated_router.post("/", response_model=BreederResponse, status_code=status.HTTP_201_CREATED)
async def create_breeder(
    breeder_data: BreederCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new breeder.
    Requires authentication.
    """
    # Check if breeder_code already exists for the organization
    if BreederCRUD.get_breeder_by_code_and_org(db, breeder_data.breeder_code, breeder_data.organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Breeder code already exists for this organization"
        )

    breeder = BreederCRUD.create_breeder(db, breeder_data)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create breeder"
        )

    return breeder


@authenticated_router.get("/", response_model=list[BreederResponse])
async def list_breeders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all breeders with pagination.
    Requires authentication.
    """
    breeders = BreederCRUD.get_all_breeders(db, skip=skip, limit=limit)
    return breeders


@authenticated_router.get("/search/{name}", response_model=list[BreederResponse])
async def search_breeders(
    name: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Search breeders by first name or last name.
    Requires authentication.
    """
    if len(name) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search name must be at least 1 character"
        )

    breeders = BreederCRUD.search_breeders_by_name(db, name, skip=skip, limit=limit)
    return breeders


@authenticated_router.get("/code/{breeder_code}", response_model=BreederResponse)
async def get_breeder_by_code(
    breeder_code: str,
    db: Session = Depends(get_db)
):
    """
    Get a breeder by breeder code.
    Requires authentication.
    """
    breeder = BreederCRUD.get_breeder_by_code(db, breeder_code)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found"
        )

    return breeder


@authenticated_router.get("/{breeder_id}", response_model=BreederResponse)
async def get_breeder(
    breeder_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a breeder by ID.
    Requires authentication.
    """
    breeder = BreederCRUD.get_breeder_by_id(db, breeder_id)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found"
        )

    return breeder


@authenticated_router.put("/{breeder_id}", response_model=BreederResponse)
async def update_breeder(
    breeder_id: int,
    breeder_data: BreederUpdate,
    db: Session = Depends(get_db)
):
    """
    Update breeder information.
    Requires authentication.
    """
    breeder = BreederCRUD.update_breeder(db, breeder_id, breeder_data)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found"
        )

    return breeder


@authenticated_router.delete("/{breeder_id}")
async def delete_breeder(
    breeder_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a breeder.
    Requires authentication.
    """
    success = BreederCRUD.delete_breeder(db, breeder_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found"
        )

    return {"message": "Breeder deleted successfully"}


@authenticated_router.get("/stats/total", response_model=dict)
async def get_breeder_stats(
    db: Session = Depends(get_db)
):
    """
    Get breeder statistics.
    Requires authentication.
    """
    total = BreederCRUD.count_breeders(db)

    return {
        "total_breeders": total
    }


# Export router for use in main app
router = authenticated_router
"""
Pydantic schemas for Breeder model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BreederBase(BaseModel):
    """Base schema for breeder data."""
    breeder_code: str = Field(..., min_length=1, max_length=80, description="Unique breeder code")
    first_name: str = Field(..., min_length=1, max_length=100, description="Breeder first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Breeder last name")


class BreederCreate(BreederBase):
    """Schema for creating a new breeder."""
    pass


class BreederUpdate(BaseModel):
    """Schema for updating a breeder."""
    breeder_code: Optional[str] = Field(None, min_length=1, max_length=80)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class BreederResponse(BreederBase):
    """Schema for breeder response (with ID and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Export router for use in main app
router = authenticated_router