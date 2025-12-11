"""
Role management API routes.
Provides CRUD endpoints for role management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.app.schemas.auth import TokenData
from api.app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from api.app.dependencies import get_current_user, get_db
from api.app.crud.role_crud import RoleCRUD
from api.app.internal.admin import check_admin_role

authenticated_router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(get_current_user)])


@authenticated_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Create a new role.
    Admin only.
    """
    # Check if role_name already exists
    if RoleCRUD.role_exists_by_name(db, role_data.role_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )

    role = RoleCRUD.create_role(db, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create role"
        )

    return role


@authenticated_router.get("/", response_model=list[RoleResponse])
async def list_roles(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all roles with pagination.
    Any authenticated user can view roles.
    """
    roles = RoleCRUD.get_all_roles(db, skip=skip, limit=limit)
    return roles


@authenticated_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a role by ID.
    Any authenticated user can view role details.
    """
    role = RoleCRUD.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return role


@authenticated_router.get("/name/{role_name}", response_model=RoleResponse)
async def get_role_by_name(
    role_name: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a role by name.
    Any authenticated user can view role details.
    """
    role = RoleCRUD.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return role


@authenticated_router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Update role information.
    Admin only.
    """
    role = RoleCRUD.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return role


@authenticated_router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Delete a role.
    Admin only.
    """
    # Check if role exists first
    role = RoleCRUD.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    success = RoleCRUD.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete role"
        )

    return {"message": f"Role {role.role_name} deleted successfully"}


@authenticated_router.post("/{role_id}/assign/{user_id}")
async def assign_role_to_user(
    role_id: int,
    user_id: int,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Assign a role to a user.
    Admin only.
    """
    # Check if role exists
    role = RoleCRUD.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Check if user exists
    from api.app.crud.user_crud import UserCRUD
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user already has this role
    if RoleCRUD.user_has_role(db, user_id, role.role_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role"
        )

    user_role = RoleCRUD.assign_role_to_user(db, user_id, role_id)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not assign role to user"
        )

    return {
        "message": f"Role {role.role_name} assigned to user {user.username}",
        "user_id": user_id,
        "role_id": role_id
    }


@authenticated_router.delete("/{role_id}/unassign/{user_id}")
async def remove_role_from_user(
    role_id: int,
    user_id: int,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Remove a role from a user.
    Admin only.
    """
    # Check if role exists
    role = RoleCRUD.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    success = RoleCRUD.remove_role_from_user(db, user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have this role"
        )

    return {
        "message": f"Role {role.role_name} removed from user",
        "user_id": user_id,
        "role_id": role_id
    }


@authenticated_router.get("/{user_id}/user-roles", response_model=list[RoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all roles assigned to a user.
    Any authenticated user can view user roles.
    """
    # Check if user exists
    from api.app.crud.user_crud import UserCRUD
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    roles = RoleCRUD.get_user_roles(db, user_id)
    return roles


# Export router for use in main app
router = authenticated_router

