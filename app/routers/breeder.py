"""
Breeder management API routes.
Provides CRUD endpoints for breeder management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.crud.breeder_crud import BreederCRUD
from api.app.dependencies import get_current_user, get_db
from api.app.schemas.breeder import BreederCreate, BreederUpdate, BreederResponse
from api.app.schemas.auth import TokenData

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


@authenticated_router.get("/me/breeder", response_model=BreederResponse)
async def get_current_user_breeder(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the breeder for the currently logged-in user.
    Requires authentication.
    """
    breeder = BreederCRUD.get_breeder_by_user_id(db, current_user.user_id)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found for current user"
        )

    return breeder


@authenticated_router.get("/user/{user_id}")
async def get_breeder_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a breeder by user ID.
    Requires authentication.
    Returns the breeder associated with the given user.
    """
    breeder = BreederCRUD.get_breeder_by_user_id(db, user_id)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found for this user"
        )

    return {
        "id": breeder.id,
        "breeder_code": breeder.breeder_code,
        "first_name": breeder.first_name,
        "last_name": breeder.last_name,
        "created_at": breeder.created_at,
        "updated_at": breeder.updated_at
    }


@authenticated_router.get("/by-user/{user_id}/id")
async def get_breeder_id_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the breeder ID for a specific user.
    Requires authentication.

    Returns:
        JSON object with breeder_id field
    """
    breeder = BreederCRUD.get_breeder_by_user_id(db, user_id)
    if not breeder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeder not found for this user"
        )

    return {"breeder_id": breeder.id}


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
