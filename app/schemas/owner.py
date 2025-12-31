"""
Pydantic schemas for Owner model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OwnerBase(BaseModel):
    """Base schema for owner data."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Owner first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Owner last name")


class OwnerCreate(OwnerBase):
    """Schema for creating a new owner."""
    pass


class OwnerUpdate(BaseModel):
    """Schema for updating an owner."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class OwnerResponse(OwnerBase):
    """Schema for owner response (with ID and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

