"""
CRUD operations for Pairs model.
This module provides database repository functions for pairs management.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.app.models.pairs import Pairs
from api.app.models.bird import Bird
from api.app.schemas.pairs import PairsCreate, PairsUpdate


class PairsCRUD:
    """Database repository for Pairs model operations."""

    @staticmethod
    def create_pair(db: Session, pair_data: PairsCreate) -> Optional[Pairs]:
        """
        Create a new pair in the database.

        Supports two ways to specify birds:
        1. Using cock/hen IDs directly (takes precedence)
        2. Using cock_band_id/hen_band_id (auto-creates birds if they don't exist)

        Validates that cock is male and hen is female.

        Args:
            db: Database session
            pair_data: PairsCreate schema with pair information

        Returns:
            Created Pairs object or None if creation fails

        Raises:
            ValueError: If cock is not male or hen is not female,
                       or if the combination already exists,
                       or if required fields are missing
        """
        try:
            cock_id = pair_data.cock
            hen_id = pair_data.hen

            # Get breeder_id and owner_id for potential bird creation
            breeder_id = pair_data.breeder_id
            owner_id = pair_data.owner_id

            # Resolve cock_band_id to cock_id if cock_id not provided
            if cock_id is None and pair_data.cock_band_id:
                cock = db.query(Bird).filter(Bird.band_id == pair_data.cock_band_id).first()
                if not cock:
                    # Create new male bird with the cock_band_id
                    cock = Bird(
                        band_id=pair_data.cock_band_id,
                        sex='M',
                        breeder_id=breeder_id,
                        owner_id=owner_id
                    )
                    db.add(cock)
                    db.flush()  # Flush to get the ID without committing
                elif cock.sex != 'M':
                    raise ValueError(
                        f"Cock bird with band ID '{pair_data.cock_band_id}' must be male (sex='M'), found sex='{cock.sex}'"
                    )
                cock_id = cock.id

            # Resolve hen_band_id to hen_id if hen_id not provided
            if hen_id is None and pair_data.hen_band_id:
                hen = db.query(Bird).filter(Bird.band_id == pair_data.hen_band_id).first()
                if not hen:
                    # Create new female bird with the hen_band_id
                    hen = Bird(
                        band_id=pair_data.hen_band_id,
                        sex='F',
                        breeder_id=breeder_id,
                        owner_id=owner_id
                    )
                    db.add(hen)
                    db.flush()  # Flush to get the ID without committing
                elif hen.sex != 'F':
                    raise ValueError(
                        f"Hen bird with band ID '{pair_data.hen_band_id}' must be female (sex='F'), found sex='{hen.sex}'"
                    )
                hen_id = hen.id

            # Validate we have both cock_id and hen_id
            if cock_id is None:
                raise ValueError("Either cock (ID) or cock_band_id must be provided")
            if hen_id is None:
                raise ValueError("Either hen (ID) or hen_band_id must be provided")

            # Validate cock is male (if using ID directly)
            if pair_data.cock is not None:
                cock = db.query(Bird).filter(Bird.id == cock_id).first()
                if not cock:
                    raise ValueError(f"Cock bird with ID {cock_id} not found")
                if cock.sex != 'M':
                    raise ValueError(f"Cock bird must be male (sex='M'), found sex='{cock.sex}'")

            # Validate hen is female (if using ID directly)
            if pair_data.hen is not None:
                hen = db.query(Bird).filter(Bird.id == hen_id).first()
                if not hen:
                    raise ValueError(f"Hen bird with ID {hen_id} not found")
                if hen.sex != 'F':
                    raise ValueError(f"Hen bird must be female (sex='F'), found sex='{hen.sex}'")

            # Check if this combination already exists
            existing = PairsCRUD.get_pair_by_composite_key(
                db, cock_id, hen_id, pair_data.season, pair_data.clutch
            )
            if existing:
                raise ValueError(
                    f"Pair combination (cock={cock_id}, hen={hen_id}, "
                    f"season={pair_data.season}, clutch={pair_data.clutch}) already exists"
                )

            # Create the pair
            db_pair = Pairs(
                season=pair_data.season,
                clutch=pair_data.clutch,
                cock=cock_id,
                hen=hen_id,
                date_paired=pair_data.date_paired,
                number_eggs=pair_data.number_eggs,
                number_fertile_eggs=pair_data.number_fertile_eggs,
                number_of_offspring=pair_data.number_of_offspring
            )
            db.add(db_pair)
            db.commit()
            db.refresh(db_pair)
            return db_pair
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")

    @staticmethod
    def get_pair_by_id(db: Session, pair_id: int) -> Optional[Pairs]:
        """
        Retrieve a pair by ID.

        Args:
            db: Database session
            pair_id: Pair ID

        Returns:
            Pairs object or None if not found
        """
        return db.query(Pairs).filter(Pairs.id == pair_id).first()

    @staticmethod
    def get_pair_by_composite_key(
        db: Session, cock_id: int, hen_id: int, season: int, clutch: int
    ) -> Optional[Pairs]:
        """
        Get pair by composite unique key: cock, hen, season, clutch.

        Args:
            db: Database session
            cock_id: Cock bird ID
            hen_id: Hen bird ID
            season: Season
            clutch: Clutch number

        Returns:
            Pairs object or None if not found
        """
        return db.query(Pairs).filter(
            (Pairs.cock == cock_id) &
            (Pairs.hen == hen_id) &
            (Pairs.season == season) &
            (Pairs.clutch == clutch)
        ).first()

    @staticmethod
    def get_all_pairs(db: Session, skip: int = 0, limit: int = 100) -> List[Pairs]:
        """
        Retrieve all pairs with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).offset(skip).limit(limit).all()

    @staticmethod
    def get_pairs_by_season(db: Session, season: int, skip: int = 0, limit: int = 100) -> List[Pairs]:
        """
        Retrieve all pairs for a specific season.

        Args:
            db: Database session
            season: Season
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).filter(Pairs.season == season).offset(skip).limit(limit).all()

    @staticmethod
    def get_pairs_by_season_and_clutch(
        db: Session, season: int, clutch: int, skip: int = 0, limit: int = 100
    ) -> List[Pairs]:
        """
        Get pairs by season and clutch.

        Args:
            db: Database session
            season: Season
            clutch: Clutch number
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).filter(
            (Pairs.season == season) & (Pairs.clutch == clutch)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_pairs_by_bird(db: Session, bird_id: int, skip: int = 0, limit: int = 100) -> List[Pairs]:
        """
        Get pairs where bird is either cock or hen.

        Args:
            db: Database session
            bird_id: Bird ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).filter(
            (Pairs.cock == bird_id) | (Pairs.hen == bird_id)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_pairs_by_cock(db: Session, cock_id: int, skip: int = 0, limit: int = 100) -> List[Pairs]:
        """
        Get pairs where bird is the cock (male).

        Args:
            db: Database session
            cock_id: Cock bird ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).filter(Pairs.cock == cock_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_pairs_by_hen(db: Session, hen_id: int, skip: int = 0, limit: int = 100) -> List[Pairs]:
        """
        Get pairs where bird is the hen (female).

        Args:
            db: Database session
            hen_id: Hen bird ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Pairs objects
        """
        return db.query(Pairs).filter(Pairs.hen == hen_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_pair(db: Session, pair_id: int, pair_data: PairsUpdate) -> Optional[Pairs]:
        """
        Update pair information.

        Supports two ways to update birds:
        1. Using cock/hen IDs directly (takes precedence)
        2. Using cock_band_id/hen_band_id (auto-creates birds if they don't exist)

        Validates sex if cock or hen is being updated.

        Args:
            db: Database session
            pair_id: Pair ID
            pair_data: PairsUpdate schema with fields to update

        Returns:
            Updated Pairs object or None if pair not found

        Raises:
            ValueError: If cock is not male or hen is not female,
                       or if the updated combination creates a duplicate
        """
        db_pair = db.query(Pairs).filter(Pairs.id == pair_id).first()
        if not db_pair:
            return None

        try:
            # Get breeder_id and owner_id for potential bird creation
            breeder_id = pair_data.breeder_id if pair_data.breeder_id is not None else None
            owner_id = pair_data.owner_id if pair_data.owner_id is not None else None

            update_data = pair_data.model_dump(exclude_unset=True, exclude={'cock_band_id', 'hen_band_id', 'breeder_id', 'owner_id'})

            # Resolve cock_band_id to cock ID if provided (and cock ID not directly provided)
            if pair_data.cock is None and pair_data.cock_band_id is not None:
                if pair_data.cock_band_id == "":
                    # Empty string means clear the cock (though this doesn't make sense for pairs)
                    raise ValueError("Cannot clear cock from pair - delete the pair instead")
                else:
                    cock = db.query(Bird).filter(Bird.band_id == pair_data.cock_band_id).first()
                    if not cock:
                        # Create new male bird with the cock_band_id
                        cock = Bird(
                            band_id=pair_data.cock_band_id,
                            sex='M',
                            breeder_id=breeder_id,
                            owner_id=owner_id
                        )
                        db.add(cock)
                        db.flush()  # Flush to get the ID without committing
                    elif cock.sex != 'M':
                        raise ValueError(
                            f"Cock bird with band ID '{pair_data.cock_band_id}' must be male (sex='M'), found sex='{cock.sex}'"
                        )
                    update_data['cock'] = cock.id

            # Resolve hen_band_id to hen ID if provided (and hen ID not directly provided)
            if pair_data.hen is None and pair_data.hen_band_id is not None:
                if pair_data.hen_band_id == "":
                    # Empty string means clear the hen (though this doesn't make sense for pairs)
                    raise ValueError("Cannot clear hen from pair - delete the pair instead")
                else:
                    hen = db.query(Bird).filter(Bird.band_id == pair_data.hen_band_id).first()
                    if not hen:
                        # Create new female bird with the hen_band_id
                        hen = Bird(
                            band_id=pair_data.hen_band_id,
                            sex='F',
                            breeder_id=breeder_id,
                            owner_id=owner_id
                        )
                        db.add(hen)
                        db.flush()  # Flush to get the ID without committing
                    elif hen.sex != 'F':
                        raise ValueError(
                            f"Hen bird with band ID '{pair_data.hen_band_id}' must be female (sex='F'), found sex='{hen.sex}'"
                        )
                    update_data['hen'] = hen.id

            # Validate cock is male if being updated with ID
            if 'cock' in update_data:
                cock = db.query(Bird).filter(Bird.id == update_data['cock']).first()
                if not cock:
                    raise ValueError(f"Cock bird with ID {update_data['cock']} not found")
                if cock.sex != 'M':
                    raise ValueError(f"Cock bird must be male (sex='M'), found sex='{cock.sex}'")

            # Validate hen is female if being updated with ID
            if 'hen' in update_data:
                hen = db.query(Bird).filter(Bird.id == update_data['hen']).first()
                if not hen:
                    raise ValueError(f"Hen bird with ID {update_data['hen']} not found")
                if hen.sex != 'F':
                    raise ValueError(f"Hen bird must be female (sex='F'), found sex='{hen.sex}'")

            # Check for duplicate composite key if relevant fields are being updated
            updated_cock = update_data.get('cock', db_pair.cock)
            updated_hen = update_data.get('hen', db_pair.hen)
            updated_season = update_data.get('season', db_pair.season)
            updated_clutch = update_data.get('clutch', db_pair.clutch)

            # Only check if the composite key has changed
            if (updated_cock != db_pair.cock or updated_hen != db_pair.hen or
                updated_season != db_pair.season or updated_clutch != db_pair.clutch):
                existing = PairsCRUD.get_pair_by_composite_key(
                    db, updated_cock, updated_hen, updated_season, updated_clutch
                )
                if existing and existing.id != pair_id:
                    raise ValueError(
                        f"Pair combination (cock={updated_cock}, hen={updated_hen}, "
                        f"season={updated_season}, clutch={updated_clutch}) already exists (ID: {existing.id})"
                    )

            # Update fields
            for field, value in update_data.items():
                setattr(db_pair, field, value)

            db.commit()
            db.refresh(db_pair)
            return db_pair
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")

    @staticmethod
    def delete_pair(db: Session, pair_id: int) -> bool:
        """
        Delete a pair from the database.

        Args:
            db: Database session
            pair_id: Pair ID

        Returns:
            True if pair was deleted, False if pair not found
        """
        db_pair = db.query(Pairs).filter(Pairs.id == pair_id).first()
        if not db_pair:
            return False

        db.delete(db_pair)
        db.commit()
        return True

    @staticmethod
    def count_pairs(db: Session) -> int:
        """
        Get total number of pairs in the database.

        Args:
            db: Database session

        Returns:
            Total number of pairs
        """
        return db.query(Pairs).count()

    @staticmethod
    def count_pairs_by_season(db: Session, season: int) -> int:
        """
        Get total number of pairs in a season.

        Args:
            db: Database session
            season: Season

        Returns:
            Total number of pairs in the season
        """
        return db.query(Pairs).filter(Pairs.season == season).count()

    @staticmethod
    def count_pairs_by_bird(db: Session, bird_id: int) -> int:
        """
        Get total number of pairs for a bird (as cock or hen).

        Args:
            db: Database session
            bird_id: Bird ID

        Returns:
            Total number of pairs
        """
        return db.query(Pairs).filter(
            (Pairs.cock == bird_id) | (Pairs.hen == bird_id)
        ).count()


