"""
CRUD operations for User model.
This module provides database repository functions for creating, reading, updating, and deleting users.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.app.models.user import User
from api.app.schemas.user import UserCreate
from api.app.core.security import hash_password, verify_password


class UserCRUD:
    """Database repository for User model operations."""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Optional[User]:
        """
        Create a new user in the database.

        Args:
            db: Database session
            user_data: UserCreate schema with username, email, and password

        Returns:
            Created User object or None if creation fails (e.g., duplicate email/username)

        Raises:
            IntegrityError: If username or email already exists
        """
        try:
            hashed_password = hash_password(user_data.password)
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.username,  # Default to username if not provided
                hashed_password=hashed_password,
                disabled=False
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Retrieve a user by username.

        Args:
            db: Database session
            username: User username

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all users with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of User objects
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all active (non-disabled) users.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of active User objects
        """
        return db.query(User).filter(User.disabled == False).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID
            **kwargs: Fields to update (username, email, full_name, disabled, hashed_password)

        Returns:
            Updated User object or None if user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # Only allow specific fields to be updated
        allowed_fields = {"username", "email", "full_name", "disabled", "hashed_password"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(db_user, key, value)

        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
        """
        Update user password.

        Args:
            db: Database session
            user_id: User ID
            new_password: New plain password (will be hashed)

        Returns:
            Updated User object or None if user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        db_user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def verify_user_password(db: Session, user_id: int, password: str) -> bool:
        """
        Verify if a password matches the user's hashed password.

        Args:
            db: Database session
            user_id: User ID
            password: Plain password to verify

        Returns:
            True if password matches, False otherwise
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        return verify_password(password, db_user.hashed_password)

    @staticmethod
    def disable_user(db: Session, user_id: int) -> Optional[User]:
        """
        Disable a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated User object or None if user not found
        """
        return UserCRUD.update_user(db, user_id, disabled=True)

    @staticmethod
    def enable_user(db: Session, user_id: int) -> Optional[User]:
        """
        Enable a user account.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated User object or None if user not found
        """
        return UserCRUD.update_user(db, user_id, disabled=False)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete a user from the database.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if user was deleted, False if user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def delete_user_by_email(db: Session, email: str) -> bool:
        """
        Delete a user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            True if user was deleted, False if user not found
        """
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def user_exists_by_email(db: Session, email: str) -> bool:
        """
        Check if a user exists by email.

        Args:
            db: Database session
            email: User email address

        Returns:
            True if user exists, False otherwise
        """
        return db.query(User).filter(User.email == email).first() is not None

    @staticmethod
    def user_exists_by_username(db: Session, username: str) -> bool:
        """
        Check if a user exists by username.

        Args:
            db: Database session
            username: User username

        Returns:
            True if user exists, False otherwise
        """
        return db.query(User).filter(User.username == username).first() is not None

    @staticmethod
    def count_users(db: Session) -> int:
        """
        Get total number of users in the database.

        Args:
            db: Database session

        Returns:
            Total number of users
        """
        return db.query(User).count()

    @staticmethod
    def count_active_users(db: Session) -> int:
        """
        Get total number of active (non-disabled) users.

        Args:
            db: Database session

        Returns:
            Total number of active users
        """
        return db.query(User).filter(User.disabled == False).count()

