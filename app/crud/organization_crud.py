"""
CRUD operations for Organization model.
"""
from ctypes import DEFAULT_MODE
from unittest.mock import DEFAULT

from sqlalchemy.orm import Session
from api.app.models.organization import Organization
from api.app.schemas.organization import OrganizationCreate, OrganizationUpdate
DEFAULT_ORGANIZATION_CODE = "FYC"

class OrganizationCRUD:
    """Database repository for Organization model operations."""

    @staticmethod
    def get_organization(db: Session, organization_id: int):
        """Get organization by ID."""
        return db.query(Organization).filter(Organization.id == organization_id).first()

    @staticmethod
    def get_organization_by_code(db: Session, organization_code: str):
        """Get organization by code."""
        return db.query(Organization).filter(Organization.organization_code == organization_code).first()

    @staticmethod
    def get_default_organization(db: Session):
        """Get the default organization (DEFAULT code)."""
        return db.query(Organization).filter(Organization.organization_code == DEFAULT_ORGANIZATION_CODE).first()

    @staticmethod
    def get_organizations(db: Session, skip: int = 0, limit: int = 100):
        """Get all organizations with pagination."""
        return db.query(Organization).offset(skip).limit(limit).all()

    @staticmethod
    def create_organization(db: Session, organization: OrganizationCreate):
        """Create a new organization."""
        db_organization = Organization(**organization.model_dump())
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization

    @staticmethod
    def update_organization(db: Session, organization_id: int, organization: OrganizationUpdate):
        """Update an organization."""
        db_organization = OrganizationCRUD.get_organization(db, organization_id)
        if not db_organization:
            return None

        update_data = organization.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_organization, field, value)

        db.commit()
        db.refresh(db_organization)
        return db_organization

    @staticmethod
    def delete_organization(db: Session, organization_id: int):
        """Delete an organization."""
        db_organization = OrganizationCRUD.get_organization(db, organization_id)
        if not db_organization:
            return None

        db.delete(db_organization)
        db.commit()
        return db_organization

