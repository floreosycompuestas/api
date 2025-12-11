"""
Example usage of UserCRUD operations.
This demonstrates how to use the User CRUD repository in your application.
"""

from sqlmodel import Session
from api.app.crud.user_crud import UserCRUD
from api.app.schemas.user import UserCreate


# Example: Create a new user
def example_create_user(db: Session):
    """Create a new user."""
    user_data = UserCreate(
        username="john_doe",
        email="john@example.com",
        password="secure_password_123"
    )
    user = UserCRUD.create_user(db, user_data)
    if user:
        print(f"User created: {user.username} (ID: {user.id})")
    else:
        print("Failed to create user (duplicate email or username)")


# Example: Get user by ID
def example_get_user_by_id(db: Session, user_id: int):
    """Get user by ID."""
    user = UserCRUD.get_user_by_id(db, user_id)
    if user:
        print(f"Found user: {user.username} ({user.email})")
    else:
        print(f"User with ID {user_id} not found")


# Example: Get user by email
def example_get_user_by_email(db: Session, email: str):
    """Get user by email."""
    user = UserCRUD.get_user_by_email(db, email)
    if user:
        print(f"Found user: {user.username}")
    else:
        print(f"User with email {email} not found")


# Example: Get all users
def example_get_all_users(db: Session):
    """Get all users with pagination."""
    users = UserCRUD.get_all_users(db, skip=0, limit=10)
    for user in users:
        print(f"- {user.username} ({user.email})")


# Example: Update user
def example_update_user(db: Session, user_id: int):
    """Update user information."""
    user = UserCRUD.update_user(db, user_id, full_name="John Doe", disabled=False)
    if user:
        print(f"User updated: {user.full_name}")
    else:
        print(f"User with ID {user_id} not found")


# Example: Change password
def example_change_password(db: Session, user_id: int):
    """Change user password."""
    user = UserCRUD.update_user_password(db, user_id, "new_secure_password_456")
    if user:
        print(f"Password updated for {user.username}")
    else:
        print(f"User with ID {user_id} not found")


# Example: Verify password
def example_verify_password(db: Session, user_id: int, password: str):
    """Verify if password matches."""
    is_valid = UserCRUD.verify_user_password(db, user_id, password)
    print(f"Password valid: {is_valid}")


# Example: Disable/Enable user
def example_disable_user(db: Session, user_id: int):
    """Disable a user account."""
    user = UserCRUD.disable_user(db, user_id)
    if user:
        print(f"User {user.username} disabled")
    else:
        print(f"User with ID {user_id} not found")


def example_enable_user(db: Session, user_id: int):
    """Enable a user account."""
    user = UserCRUD.enable_user(db, user_id)
    if user:
        print(f"User {user.username} enabled")
    else:
        print(f"User with ID {user_id} not found")


# Example: Check if user exists
def example_check_user_exists(db: Session, email: str, username: str):
    """Check if user exists."""
    email_exists = UserCRUD.user_exists_by_email(db, email)
    username_exists = UserCRUD.user_exists_by_username(db, username)

    print(f"Email exists: {email_exists}")
    print(f"Username exists: {username_exists}")


# Example: Delete user
def example_delete_user(db: Session, user_id: int):
    """Delete a user."""
    success = UserCRUD.delete_user(db, user_id)
    if success:
        print(f"User with ID {user_id} deleted")
    else:
        print(f"User with ID {user_id} not found")


# Example: Count users
def example_count_users(db: Session):
    """Count total users and active users."""
    total = UserCRUD.count_users(db)
    active = UserCRUD.count_active_users(db)

    print(f"Total users: {total}")
    print(f"Active users: {active}")
    print(f"Disabled users: {total - active}")
"""
CRUD operations package for database models.
"""

from api.app.crud.user_crud import UserCRUD

__all__ = ["UserCRUD"]

