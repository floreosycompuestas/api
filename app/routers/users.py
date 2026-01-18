from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.schemas.auth import TokenData
from api.app.schemas.user import UserCreate
from api.app.schemas.breeder import BreederCreate
from api.app.dependencies import get_current_user, get_db
from api.app.crud.user_crud import UserCRUD
from api.app.crud.breeder_crud import BreederCRUD
from api.app.crud.organization_crud import OrganizationCRUD

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Returns the created user without the hashed password.
    """
    # Check if email already exists
    if UserCRUD.user_exists_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if UserCRUD.user_exists_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = UserCRUD.create_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user"
        )

    # Create a default breeder for the user
    # First, get or create a default organization for the user
    default_org = OrganizationCRUD.get_default_organization(db)
    if not default_org:
        # If no default organization exists, create one
        from api.app.schemas.organization import OrganizationCreate
        org_data = OrganizationCreate(
            organization_code="DEFAULT",
            organization_name="Default Organization",
            organization_alias="DEF"
        )
        default_org = OrganizationCRUD.create_organization(db, org_data)

    if default_org:
        # Generate breeder code from username
        breeder_code = f"BR-{user.username.upper()}"

        breeder_data = BreederCreate(
            breeder_code=breeder_code,
            organization_id=default_org.id,
            user_id=user.id,
            first_name=user.full_name.split()[0] if user.full_name else user.username,
            last_name=user.full_name.split()[-1] if user.full_name and len(user.full_name.split()) > 1 else ""
        )
        breeder = BreederCRUD.create_breeder(db, breeder_data)
        if not breeder:
            # Log warning but don't fail user creation if breeder creation fails
            print(f"Warning: Could not create default breeder for user {user.id}")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": user.disabled
    }


@router.get("/")
async def read_users(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all users (protected route)."""
    users = UserCRUD.get_all_users(db, skip=skip, limit=limit)
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "disabled": user.disabled
        }
        for user in users
    ]


@router.get("/me")
async def read_user_me(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user profile."""
    user = UserCRUD.get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": user.disabled
    }


@router.get("/{username}")
async def read_user(
    username: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by username (protected route)."""
    user = UserCRUD.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": user.disabled
    }


@router.put("/{user_id}")
async def update_user_info(
    user_id: int,
    full_name: str = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information (users can only update their own profile)."""
    # Check if user is updating their own profile
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    user = UserCRUD.update_user(db, user_id, full_name=full_name)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": user.disabled
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user (users can only delete their own account)."""
    # Check if user is deleting their own account
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    success = UserCRUD.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "User account deleted successfully"}
