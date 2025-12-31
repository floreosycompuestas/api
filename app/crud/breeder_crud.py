"""
CRUD operations for Breeder model.
This module provides database repository functions for breeder management.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from api.app.models.breeder import Breeder
from api.app.schemas.breeder import BreederCreate, BreederUpdate


class BreederCRUD:
    """Database repository for Breeder model operations."""

    @staticmethod
    def create_breeder(db: Session, breeder_data: BreederCreate) -> Optional[Breeder]:
        """
        Create a new breeder in the database.

        Args:
            db: Database session
            breeder_data: BreederCreate schema with breeder information

        Returns:
            Created Breeder object or None if creation fails (e.g., duplicate breeder_code)

        Raises:
            IntegrityError: If breeder_code already exists for the organization
        """
        try:
            db_breeder = Breeder(
                breeder_code=breeder_data.breeder_code,
                organization_id=breeder_data.organization_id,
                user_id=breeder_data.user_id,
                owner_id=breeder_data.owner_id,
                first_name=breeder_data.first_name,
                last_name=breeder_data.last_name,
            )
            db.add(db_breeder)
            db.commit()
            db.refresh(db_breeder)
            return db_breeder
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def get_breeder_by_id(db: Session, breeder_id: int) -> Optional[Breeder]:
        """
        Retrieve a breeder by ID.

        Args:
            db: Database session
            breeder_id: Breeder ID

        Returns:
            Breeder object or None if not found
        """
        return db.query(Breeder).filter(Breeder.id == breeder_id).first()

    @staticmethod
    def get_breeder_by_code(db: Session, breeder_code: str) -> Optional[Breeder]:
        """
        Retrieve a breeder by breeder code (unique identifier).

        Args:
            db: Database session
            breeder_code: Breeder code

        Returns:
            Breeder object or None if not found
        """
        return db.query(Breeder).filter(Breeder.breeder_code == breeder_code).first()

    @staticmethod
    def get_breeder_by_code_and_org(db: Session, breeder_code: str, organization_id: int) -> Optional[Breeder]:
        """
        Retrieve a breeder by breeder code and organization ID (composite unique key).

        Args:
            db: Database session
            breeder_code: Breeder code
            organization_id: Organization ID

        Returns:
            Breeder object or None if not found
        """
        return db.query(Breeder).filter(
            (Breeder.breeder_code == breeder_code) & (Breeder.organization_id == organization_id)
        ).first()

    @staticmethod
    def get_all_breeders(db: Session, skip: int = 0, limit: int = 100) -> List[Breeder]:
        """
        Retrieve all breeders with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Breeder objects
        """
        return db.query(Breeder).offset(skip).limit(limit).all()

    @staticmethod
    def search_breeders_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Breeder]:
        """
        Search breeders by first name or last name.

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Breeder objects matching the search
        """
        search_pattern = f"%{name}%"
        return db.query(Breeder).filter(
            (Breeder.first_name.ilike(search_pattern)) | (Breeder.last_name.ilike(search_pattern))
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_breeder(db: Session, breeder_id: int, breeder_data: BreederUpdate) -> Optional[Breeder]:
        """
        Update breeder information.

        Args:
            db: Database session
            breeder_id: Breeder ID
            breeder_data: BreederUpdate schema with fields to update

        Returns:
            Updated Breeder object or None if breeder not found
        """
        db_breeder = db.query(Breeder).filter(Breeder.id == breeder_id).first()
        if not db_breeder:
            return None

        # Update fields if provided
        update_data = breeder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_breeder, field, value)

        db_breeder.updated_at = datetime.now()

        try:
            db.commit()
            db.refresh(db_breeder)
            return db_breeder
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_breeder(db: Session, breeder_id: int) -> bool:
        """
        Delete a breeder from the database.

        Args:
            db: Database session
            breeder_id: Breeder ID

        Returns:
            True if breeder was deleted, False if breeder not found
        """
        db_breeder = db.query(Breeder).filter(Breeder.id == breeder_id).first()
        if not db_breeder:
            return False

        db.delete(db_breeder)
        db.commit()
        return True

    @staticmethod
    def delete_breeder_by_code(db: Session, breeder_code: str) -> bool:
        """
        Delete a breeder by breeder code.

        Args:
            db: Database session
            breeder_code: Breeder code

        Returns:
            True if breeder was deleted, False if breeder not found
        """
        db_breeder = db.query(Breeder).filter(Breeder.breeder_code == breeder_code).first()
        if not db_breeder:
            return False

        db.delete(db_breeder)
        db.commit()
        return True

    @staticmethod
    def breeder_exists_by_code(db: Session, breeder_code: str) -> bool:
        """
        Check if a breeder exists by breeder code.

        Args:
            db: Database session
            breeder_code: Breeder code

        Returns:
            True if breeder exists, False otherwise
        """
        return db.query(Breeder).filter(Breeder.breeder_code == breeder_code).first() is not None

    @staticmethod
    def count_breeders(db: Session) -> int:
        """
        Get total number of breeders in the database.

        Args:
            db: Database session

        Returns:
            Total number of breeders
        """
        return db.query(Breeder).count()

