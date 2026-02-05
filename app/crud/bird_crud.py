"""
CRUD operations for Bird model.
This module provides database repository functions for bird management.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from api.app.models.bird import Bird
from api.app.models.breeder import Breeder
from api.app.schemas.bird import BirdCreate, BirdUpdate


class BirdCRUD:
    """Database repository for Bird model operations."""

    @staticmethod
    def create_bird(db: Session, bird_data: BirdCreate) -> Optional[Bird]:
        """
        Create a new bird in the database.
        Resolves father_band_id and mother_band_id to their respective bird IDs.
        If father_band_id doesn't exist, automatically creates a new male bird.
        If mother_band_id doesn't exist, automatically creates a new female bird.
        If band_id is not provided, generates it as: breeder_code-YYYY-NN
        (4-digit year, 2-digit zero-padded bird_number)
        If breeder_id is not provided, derives it from band_id by extracting breeder_code.
        If bird_year is not provided, derives it from band_id by extracting the year.
        If bird_number is not provided, derives it from band_id by extracting the number.
        If dob is not provided, derives it from band_id year (sets to January 1st of that year).

        Args:
            db: Database session
            bird_data: BirdCreate schema with bird information

        Returns:
            Created Bird object or None if creation fails (e.g., duplicate band_id)

        Raises:
            IntegrityError: If band_id already exists or foreign key constraint fails
            ValueError: If father_band_id or mother_band_id exists but has wrong sex,
                       or if band_id generation requirements are not met,
                       or if breeder_code/bird_year/bird_number cannot be derived from band_id
        """
        try:
            # Generate band_id if not provided
            band_id = bird_data.band_id
            breeder_id = bird_data.breeder_id
            bird_year = bird_data.bird_year

            if not band_id:
                # Validate requirements for auto-generation
                if not breeder_id:
                    raise ValueError("breeder_id is required to auto-generate band_id")
                if not bird_year:
                    raise ValueError("bird_year is required to auto-generate band_id")
                if not bird_data.bird_number:
                    raise ValueError("bird_number is required to auto-generate band_id")

                # Get breeder code
                breeder = db.query(Breeder).filter(Breeder.id == breeder_id).first()
                if not breeder:
                    raise ValueError(f"Breeder with ID {breeder_id} not found")

                # Generate band_id: breeder_code-bird_year-bird_number
                # Format: 4-digit year, 2-digit zero-padded bird_number
                band_id = f"{breeder.breeder_code}-{bird_year:04d}-{bird_data.bird_number:02d}"

            # Derive breeder_id from band_id if not provided
            if not breeder_id and band_id:
                # Extract breeder_code from band_id format: breeder_code-YYYY-NN
                try:
                    parts = band_id.split('-')
                    if len(parts) >= 3:
                        # First part(s) before the last two parts is the breeder_code
                        # Handle cases like "BR001-2024-05" or "SMITH-JONES-2024-05"
                        breeder_code = '-'.join(parts[:-2])
                        breeder = db.query(Breeder).filter(Breeder.breeder_code == breeder_code).first()
                        if breeder:
                            breeder_id = breeder.id
                        else:
                            raise ValueError(f"Breeder with code '{breeder_code}' not found")
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Could not derive breeder from band_id '{band_id}': {str(e)}")

            # Derive bird_year from band_id if not provided
            if not bird_year and band_id:
                # Extract year from band_id format: breeder_code-YYYY-NN
                try:
                    parts = band_id.split('-')
                    if len(parts) >= 2:
                        bird_year = int(parts[-2])  # Second to last part is the year
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Could not derive bird_year from band_id '{band_id}': {str(e)}")

            # Derive bird_number from band_id if not provided
            bird_number = bird_data.bird_number
            if not bird_number and band_id:
                # Extract bird_number from band_id format: breeder_code-YYYY-NN
                try:
                    parts = band_id.split('-')
                    if len(parts) >= 1:
                        bird_number = int(parts[-1])  # Last part is the bird_number
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Could not derive bird_number from band_id '{band_id}': {str(e)}")

            father_id = None
            mother_id = None

            # Resolve father_band_id to father_id, create if doesn't exist
            if bird_data.father_band_id:
                father = db.query(Bird).filter(Bird.band_id == bird_data.father_band_id).first()
                if not father:
                    # Create new male bird with the father_band_id
                    father = Bird(
                        band_id=bird_data.father_band_id,
                        sex='M',
                        breeder_id=breeder_id,
                        owner_id=bird_data.owner_id
                    )
                    db.add(father)
                    db.flush()  # Flush to get the ID without committing
                elif father.sex != 'M':
                    raise ValueError(f"Father bird with band ID '{bird_data.father_band_id}' must be male (sex='M'), found sex='{father.sex}'")
                father_id = father.id

            # Resolve mother_band_id to mother_id, create if doesn't exist
            if bird_data.mother_band_id:
                mother = db.query(Bird).filter(Bird.band_id == bird_data.mother_band_id).first()
                if not mother:
                    # Create new female bird with the mother_band_id
                    mother = Bird(
                        band_id=bird_data.mother_band_id,
                        sex='F',
                        breeder_id=breeder_id,
                        owner_id=bird_data.owner_id
                    )
                    db.add(mother)
                    db.flush()  # Flush to get the ID without committing
                elif mother.sex != 'F':
                    raise ValueError(f"Mother bird with band ID '{bird_data.mother_band_id}' must be female (sex='F'), found sex='{mother.sex}'")
                mother_id = mother.id

            # Derive dob from bird_year if not provided
            dob = bird_data.dob
            if not dob and bird_year:
                # Set dob to January 1st of the bird_year
                try:
                    dob = datetime(bird_year, 1, 1)
                except (ValueError, TypeError):
                    # If we can't create the date, leave dob as None
                    pass

            db_bird = Bird(
                band_id=band_id,
                name=bird_data.name,
                dob=dob,
                sex=bird_data.sex,
                father_id=father_id,
                mother_id=mother_id,
                breeder_id=breeder_id,
                owner_id=bird_data.owner_id,
            )
            db.add(db_bird)
            db.commit()
            db.refresh(db_bird)
            return db_bird
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def get_bird_by_id(db: Session, bird_id: int) -> Optional[Bird]:
        """
        Retrieve a bird by ID.

        Args:
            db: Database session
            bird_id: Bird ID

        Returns:
            Bird object or None if not found
        """
        return db.query(Bird).filter(Bird.id == bird_id).first()

    @staticmethod
    def get_bird_by_band_id(db: Session, band_id: str) -> Optional[Bird]:
        """
        Retrieve a bird by band ID (unique identifier).

        Args:
            db: Database session
            band_id: Band ID

        Returns:
            Bird object or None if not found
        """
        return db.query(Bird).filter(Bird.band_id == band_id).first()

    @staticmethod
    def get_bird_by_breeder_code_and_band_id(db: Session, breeder_code: str, band_id: str) -> Optional[Bird]:
        """
        Retrieve a bird by breeder code and band ID.

        Args:
            db: Database session
            breeder_code: Breeder code (e.g., "BR001")
            band_id: Bird band ID

        Returns:
            Bird object or None if not found
        """
        from api.app.models.breeder import Breeder

        return db.query(Bird).join(
            Breeder, Bird.breeder_id == Breeder.id
        ).filter(
            Breeder.breeder_code == breeder_code,
            Bird.band_id == band_id
        ).first()

    @staticmethod
    def get_all_birds(db: Session, skip: int = 0, limit: int = 100) -> List[Bird]:
        """
        Retrieve all birds with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Bird objects
        """
        return db.query(Bird).offset(skip).limit(limit).all()

    @staticmethod
    def get_birds_by_breeder(db: Session, breeder_id: int, skip: int = 0, limit: int = 100) -> List[Bird]:
        """
        Retrieve all birds for a specific breeder.

        Args:
            db: Database session
            breeder_id: Breeder ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Bird objects
        """
        return db.query(Bird).filter(Bird.breeder_id == breeder_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_birds_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Bird]:
        """
        Retrieve all birds for a specific owner.

        Args:
            db: Database session
            owner_id: Owner ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Bird objects
        """
        return db.query(Bird).filter(Bird.owner_id == owner_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_offspring(db: Session, parent_id: int) -> List[Bird]:
        """
        Get all offspring of a bird (where bird is father or mother).

        Args:
            db: Database session
            parent_id: Parent bird ID

        Returns:
            List of offspring Bird objects
        """
        return db.query(Bird).filter(
            (Bird.father_id == parent_id) | (Bird.mother_id == parent_id)
        ).all()

    @staticmethod
    def get_birds_by_sex(db: Session, sex: str, skip: int = 0, limit: int = 100) -> List[Bird]:
        """
        Retrieve birds by sex (M or F).

        Args:
            db: Database session
            sex: Sex (M or F)
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Bird objects
        """
        return db.query(Bird).filter(Bird.sex == sex).offset(skip).limit(limit).all()

    @staticmethod
    def update_bird(db: Session, bird_id: int, bird_data: BirdUpdate) -> Optional[Bird]:
        """
        Update bird information.

        Args:
            db: Database session
            bird_id: Bird ID
            bird_data: BirdUpdate schema with fields to update

        Returns:
            Updated Bird object or None if bird not found
        """
        db_bird = db.query(Bird).filter(Bird.id == bird_id).first()
        if not db_bird:
            return None

        # Update fields if provided
        update_data = bird_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bird, field, value)

        db_bird.updated_at = datetime.utcnow()

        try:
            db.commit()
            db.refresh(db_bird)
            return db_bird
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_bird(db: Session, bird_id: int) -> bool:
        """
        Delete a bird from the database.

        Args:
            db: Database session
            bird_id: Bird ID

        Returns:
            True if bird was deleted, False if bird not found
        """
        db_bird = db.query(Bird).filter(Bird.id == bird_id).first()
        if not db_bird:
            return False

        db.delete(db_bird)
        db.commit()
        return True

    @staticmethod
    def delete_bird_by_band_id(db: Session, band_id: str) -> bool:
        """
        Delete a bird by band ID.

        Args:
            db: Database session
            band_id: Band ID

        Returns:
            True if bird was deleted, False if bird not found
        """
        db_bird = db.query(Bird).filter(Bird.band_id == band_id).first()
        if not db_bird:
            return False

        db.delete(db_bird)
        db.commit()
        return True

    @staticmethod
    def bird_exists_by_band_id(db: Session, band_id: str) -> bool:
        """
        Check if a bird exists by band ID.

        Args:
            db: Database session
            band_id: Band ID

        Returns:
            True if bird exists, False otherwise
        """
        return db.query(Bird).filter(Bird.band_id == band_id).first() is not None

    @staticmethod
    def count_birds(db: Session) -> int:
        """
        Get total number of birds in the database.

        Args:
            db: Database session

        Returns:
            Total number of birds
        """
        return db.query(Bird).count()

    @staticmethod
    def count_birds_by_breeder(db: Session, breeder_id: int) -> int:
        """
        Get total number of birds for a breeder.

        Args:
            db: Database session
            breeder_id: Breeder ID

        Returns:
            Total number of birds
        """
        return db.query(Bird).filter(Bird.breeder_id == breeder_id).count()

    @staticmethod
    def count_birds_by_owner(db: Session, owner_id: int) -> int:
        """
        Get total number of birds for an owner.

        Args:
            db: Database session
            owner_id: Owner ID

        Returns:
            Total number of birds
        """
        return db.query(Bird).filter(Bird.owner_id == owner_id).count()

    @staticmethod
    def count_birds_by_sex(db: Session, sex: str) -> int:
        """
        Get total number of birds by sex.

        Args:
            db: Database session
            sex: Sex (M or F)

        Returns:
            Total number of birds
        """
        return db.query(Bird).filter(Bird.sex == sex).count()
