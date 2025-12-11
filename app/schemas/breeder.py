"""
Pydantic schemas for Breeder model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BreederBase(BaseModel):
    """Base schema for breeder data."""
    breeder_code: str = Field(..., min_length=1, max_length=80, description="Unique breeder code")
    first_name: str = Field(..., min_length=1, max_length=100, description="Breeder first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Breeder last name")


class BreederCreate(BreederBase):
    """Schema for creating a new breeder."""
    pass


class BreederUpdate(BaseModel):
    """Schema for updating a breeder."""
    breeder_code: Optional[str] = Field(None, min_length=1, max_length=80)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class BreederResponse(BreederBase):
    """Schema for breeder response (with ID and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

