"""
Router for Organization endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.app.dependencies import get_db
from api.app.crud.organization_crud import OrganizationCRUD
from api.app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all organizations."""
    organizations = OrganizationCRUD.get_organizations(db, skip=skip, limit=limit)
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    """Get organization by ID."""
    organization = OrganizationCRUD.get_organization(db, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.get("/code/{organization_code}", response_model=OrganizationResponse)
def read_organization_by_code(organization_code: str, db: Session = Depends(get_db)):
    """Get organization by code."""
    organization = OrganizationCRUD.get_organization_by_code(db, organization_code)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_new_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization."""
    # Check if organization code already exists
    existing = OrganizationCRUD.get_organization_by_code(db, organization.organization_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization code already exists"
        )
    return OrganizationCRUD.create_organization(db, organization)


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_existing_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    db: Session = Depends(get_db)
):
    """Update an organization."""
    db_organization = OrganizationCRUD.update_organization(db, organization_id, organization)
    if not db_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return db_organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_organization(organization_id: int, db: Session = Depends(get_db)):
    """Delete an organization."""
    organization = OrganizationCRUD.delete_organization(db, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return None

