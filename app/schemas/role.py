"""
Pydantic schemas for Role model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from api.app.core.enums import RoleEnum


class RoleBase(BaseModel):
    """Base role schema."""
    role_name: RoleEnum = Field(..., description="Unique role name")
    description: Optional[str] = Field(None, max_length=100, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    description: Optional[str] = Field(None, max_length=100)


class RoleResponse(RoleBase):
    """Schema for role responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleResponse(BaseModel):
    """Schema for user role assignment."""
    user_id: int
    role_id: int
    assigned_at: datetime

    class Config:
        from_attributes = True
