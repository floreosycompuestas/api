"""
Pydantic schemas for Organization model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OrganizationBase(BaseModel):
    """Base schema for organization data."""
    organization_code: str = Field(..., min_length=1, max_length=100, description="Unique organization code")
    organization_name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    organization_alias: Optional[str] = Field(None, max_length=20, description="Short alias for organization")
    address: Optional[str] = Field(None, max_length=200, description="Organization address")
    country_code: Optional[str] = Field(None, max_length=20, description="Country code")
    country_name: Optional[str] = Field(None, max_length=100, description="Country name")


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    organization_code: Optional[str] = Field(None, min_length=1, max_length=100)
    organization_name: Optional[str] = Field(None, min_length=1, max_length=100)
    organization_alias: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=200)
    country_code: Optional[str] = Field(None, max_length=20)
    country_name: Optional[str] = Field(None, max_length=100)


class OrganizationResponse(OrganizationBase):
    """Schema for organization response (with ID and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

