"""
Admin management routes.
Provides administrative endpoints for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import text

from api.app.schemas.auth import TokenData
from api.app.dependencies import get_current_user, get_db
from api.app.crud.user_crud import UserCRUD
from api.app.crud.bird_crud import BirdCRUD
from api.app.crud.breeder_crud import BreederCRUD
from api.app.core.redis_client import RedisClient
from api.app.core.enums import RoleEnum

authenticated_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_user)])


def check_admin_role(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)) -> TokenData:
    """
    Verify that the current user has admin role.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Current user if admin, raises exception otherwise

    Raises:
        HTTPException: If user is not an admin
    """
    from api.app.crud.role_crud import RoleCRUD

    user = UserCRUD.get_user_by_id(db, current_user.user_id)

    if not user or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    if not RoleCRUD.user_has_role(db, current_user.user_id, RoleEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )

    return current_user


@authenticated_router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get system statistics (users, birds, breeders).
    Admin only.
    """
    total_users = UserCRUD.count_users(db)
    active_users = UserCRUD.count_active_users(db)
    total_birds = BirdCRUD.count_birds(db)
    total_breeders = BreederCRUD.count_breeders(db)

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "disabled": total_users - active_users
        },
        "birds": {
            "total": total_birds
        },
        "breeders": {
            "total": total_breeders
        }
    }


@authenticated_router.get("/users", response_model=list[Dict[str, Any]])
async def list_all_users(
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users with admin details.
    Admin only.
    """
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


@authenticated_router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Disable a user account.
    Admin only.
    """
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )

    user = UserCRUD.disable_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": f"User {user.username} disabled successfully"}


@authenticated_router.post("/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Enable a user account.
    Admin only.
    """
    user = UserCRUD.enable_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": f"User {user.username} enabled successfully"}


@authenticated_router.get("/redis/info", response_model=Dict[str, Any])
async def get_redis_info(
    current_user: TokenData = Depends(check_admin_role)
):
    """
    Get Redis server information.
    Admin only.
    """
    if not RedisClient.health_check():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is not available"
        )

    return {
        "status": "connected",
        "message": "Redis is operational"
    }


@authenticated_router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user: TokenData = Depends(check_admin_role)
):
    """
    Get cache/Redis statistics.
    Admin only.
    """
    try:
        client = RedisClient.get_client()
        info = client.info()

        return {
            "memory_used": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands": info.get("total_commands_processed"),
            "uptime_seconds": info.get("uptime_in_seconds")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not retrieve cache stats: {str(e)}"
        )


@authenticated_router.post("/cache/flush")
async def flush_cache(
    current_user: TokenData = Depends(check_admin_role)
):
    """
    Clear all revoked tokens from Redis.
    WARNING: This will invalidate all revoked tokens.
    Admin only.
    """
    try:
        client = RedisClient.get_client()
        # Only flush keys matching revoked_token: pattern
        cursor = 0
        deleted_count = 0

        while True:
            cursor, keys = client.scan(cursor, match="revoked_token:*")
            for key in keys:
                client.delete(key)
                deleted_count += 1

            if cursor == 0:
                break

        return {
            "message": "Cache flushed successfully",
            "revoked_tokens_deleted": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not flush cache: {str(e)}"
        )


@authenticated_router.get("/health/detailed", response_model=Dict[str, Any])
async def get_detailed_health(
    current_user: TokenData = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get detailed system health information.
    Admin only.
    """
    db_health = "healthy"
    redis_health = "healthy"

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_health = "unhealthy"

    if not RedisClient.health_check():
        redis_health = "unhealthy"

    return {
        "database": db_health,
        "redis": redis_health,
        "timestamp": str(datetime.now(timezone.utc))
    }


# Export router for use in main app
router = authenticated_router
