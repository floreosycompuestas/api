"""
CRUD operations for Organization model.
"""

from sqlalchemy.orm import Session
from api.app.models.organization import Organization
from api.app.schemas.organization import OrganizationCreate, OrganizationUpdate


def get_organization(db: Session, organization_id: int):
    """Get organization by ID."""
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organization_by_code(db: Session, organization_code: str):
    """Get organization by code."""
    return db.query(Organization).filter(Organization.organization_code == organization_code).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    """Get all organizations with pagination."""
    return db.query(Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: OrganizationCreate):
    """Create a new organization."""
    db_organization = Organization(**organization.model_dump())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(db: Session, organization_id: int, organization: OrganizationUpdate):
    """Update an organization."""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return None

    update_data = organization.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_organization, field, value)

    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, organization_id: int):
    """Delete an organization."""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return None

    db.delete(db_organization)
    db.commit()
    return db_organization

