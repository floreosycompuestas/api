"""
CRUD operations for Role model.
This module provides database repository functions for role management.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from api.app.models.role import Role, UserRole
from api.app.schemas.role import RoleCreate, RoleUpdate
from api.app.core.enums import RoleEnum


class RoleCRUD:
    """Database repository for Role model operations."""

    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Optional[Role]:
        """
        Create a new role.

        Args:
            db: Database session
            role_data: RoleCreate schema with role information

        Returns:
            Created Role object or None if creation fails (e.g., duplicate role_name)
        """
        try:
            db_role = Role(
                role_name=role_data.role_name,
                description=role_data.description,
            )
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            return db_role
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """
        Retrieve a role by ID.

        Args:
            db: Database session
            role_id: Role ID

        Returns:
            Role object or None if not found
        """
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, role_name: RoleEnum) -> Optional[Role]:
        """
        Retrieve a role by name (unique identifier).

        Args:
            db: Database session
            role_name: Role name (RoleEnum)

        Returns:
            Role object or None if not found
        """
        return db.query(Role).filter(Role.role_name == role_name).first()

    @staticmethod
    def get_all_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """
        Retrieve all roles with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of Role objects
        """
        return db.query(Role).offset(skip).limit(limit).all()

    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """
        Update role information.

        Args:
            db: Database session
            role_id: Role ID
            role_data: RoleUpdate schema with fields to update

        Returns:
            Updated Role object or None if role not found
        """
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return None

        # Update fields if provided
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)

        db_role.updated_at = datetime.utcnow()

        try:
            db.commit()
            db.refresh(db_role)
            return db_role
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """
        Delete a role from the database.

        Args:
            db: Database session
            role_id: Role ID

        Returns:
            True if role was deleted, False if role not found
        """
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return False

        db.delete(db_role)
        db.commit()
        return True

    @staticmethod
    def delete_role_by_name(db: Session, role_name: RoleEnum) -> bool:
        """
        Delete a role by name.

        Args:
            db: Database session
            role_name: Role name (RoleEnum)

        Returns:
            True if role was deleted, False if role not found
        """
        db_role = db.query(Role).filter(Role.role_name == role_name).first()
        if not db_role:
            return False

        db.delete(db_role)
        db.commit()
        return True

    @staticmethod
    def role_exists_by_name(db: Session, role_name: RoleEnum) -> bool:
        """
        Check if a role exists by name.

        Args:
            db: Database session
            role_name: Role name (RoleEnum)

        Returns:
            True if role exists, False otherwise
        """
        return db.query(Role).filter(Role.role_name == role_name).first() is not None

    @staticmethod
    def count_roles(db: Session) -> int:
        """
        Get total number of roles in the database.

        Args:
            db: Database session

        Returns:
            Total number of roles
        """
        return db.query(Role).count()

    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_id: int) -> Optional[UserRole]:
        """
        Assign a role to a user.

        Args:
            db: Database session
            user_id: User ID
            role_id: Role ID

        Returns:
            Created UserRole object or None if fails
        """
        try:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            return user_role
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
        """
        Remove a role from a user.

        Args:
            db: Database session
            user_id: User ID
            role_id: Role ID

        Returns:
            True if role was removed, False if not found
        """
        user_role = db.query(UserRole).filter(
            (UserRole.user_id == user_id) & (UserRole.role_id == role_id)
        ).first()

        if not user_role:
            return False

        db.delete(user_role)
        db.commit()
        return True

    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[Role]:
        """
        Get all roles for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of Role objects assigned to the user
        """
        user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
        return [RoleCRUD.get_role_by_id(db, ur.role_id) for ur in user_roles if ur]

    @staticmethod
    def user_has_role(db: Session, user_id: int, role_name: RoleEnum) -> bool:
        """
        Check if user has a specific role.

        Args:
            db: Database session
            user_id: User ID
            role_name: Role name (RoleEnum) to check

        Returns:
            True if user has the role, False otherwise
        """
        role = RoleCRUD.get_role_by_name(db, role_name)
        if not role:
            return False

        user_role = db.query(UserRole).filter(
            (UserRole.user_id == user_id) & (UserRole.role_id == role.id)
        ).first()

        return user_role is not None
