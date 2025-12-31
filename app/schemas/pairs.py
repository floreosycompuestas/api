"""
Pydantic schemas for Pairs model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PairsBase(BaseModel):
    """Base schema for pairs data."""
    season: int = Field(..., description="Breeding season")
    round: int = Field(..., description="Round number")
    cock: int = Field(..., description="Male bird ID")
    hen: int = Field(..., description="Female bird ID")
    number_eggs: Optional[int] = Field(None, ge=0, description="Number of eggs")
    number_fertile_eggs: Optional[int] = Field(None, ge=0, description="Number of fertile eggs")
    number_of_offspring: Optional[int] = Field(None, ge=0, description="Number of offspring")


class PairsCreate(PairsBase):
    """Schema for creating a new pair."""
    pass


class PairsUpdate(BaseModel):
    """Schema for updating a pair."""
    season: Optional[int] = Field(None, description="Breeding season")
    round: Optional[int] = Field(None, description="Round number")
    cock: Optional[int] = Field(None, description="Male bird ID")
    hen: Optional[int] = Field(None, description="Female bird ID")
    number_eggs: Optional[int] = Field(None, ge=0, description="Number of eggs")
    number_fertile_eggs: Optional[int] = Field(None, ge=0, description="Number of fertile eggs")
    incubation_start: Optional[datetime] = Field(None, description="Incubation start date")
    incubation_end: Optional[datetime] = Field(None, description="Incubation end date")
    band_date: Optional[datetime] = Field(None, description="Banding date")
    number_of_offspring: Optional[int] = Field(None, ge=0, description="Number of offspring")


class PairsResponse(PairsBase):
    """Schema for pairs response (with ID and timestamps)."""
    id: int
    date_paired: datetime
    incubation_start: Optional[datetime]
    incubation_end: Optional[datetime]
    band_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

