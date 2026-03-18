"""
Pydantic schemas for Pairs model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PairsBase(BaseModel):
    """Base schema for pairs data."""
    season: int = Field(..., description="Breeding season")
    clutch: int = Field(..., description="Clutch number")
    number_eggs: Optional[int] = Field(None, ge=0, description="Number of eggs")
    number_fertile_eggs: Optional[int] = Field(None, ge=0, description="Number of fertile eggs")
    number_of_offspring: Optional[int] = Field(None, ge=0, description="Number of offspring")


class PairsCreate(PairsBase):
    """
    Schema for creating a new pair.

    You can specify birds using either:
    1. Bird IDs: cock and hen (numeric IDs)
    2. Band IDs: cock_band_id and hen_band_id (auto-creates birds if they don't exist)

    Priority: If both cock and cock_band_id are provided, cock (ID) takes precedence.
    Same for hen and hen_band_id.
    """
    cock: Optional[int] = Field(None, description="Male bird ID")
    hen: Optional[int] = Field(None, description="Female bird ID")
    cock_band_id: Optional[str] = Field(None, max_length=100, description="Male bird band ID (auto-creates if not found)")
    hen_band_id: Optional[str] = Field(None, max_length=100, description="Female bird band ID (auto-creates if not found)")
    date_paired: Optional[datetime] = Field(None, description="Date paired (defaults to current timestamp)")
    breeder_id: Optional[int] = Field(None, description="Breeder ID (used when auto-creating birds from band IDs)")
    owner_id: Optional[int] = Field(None, description="Owner ID (used when auto-creating birds from band IDs)")


class PairsUpdate(BaseModel):
    """
    Schema for updating a pair.

    You can update birds using either:
    1. Bird IDs: cock and hen
    2. Band IDs: cock_band_id and hen_band_id (auto-creates if not found)
    """
    season: Optional[int] = Field(None, description="Breeding season")
    clutch: Optional[int] = Field(None, description="Clutch number")
    cock: Optional[int] = Field(None, description="Male bird ID")
    hen: Optional[int] = Field(None, description="Female bird ID")
    cock_band_id: Optional[str] = Field(None, max_length=100, description="Male bird band ID (auto-creates if not found)")
    hen_band_id: Optional[str] = Field(None, max_length=100, description="Female bird band ID (auto-creates if not found)")
    date_paired: Optional[datetime] = Field(None, description="Date paired")
    number_eggs: Optional[int] = Field(None, ge=0, description="Number of eggs")
    number_fertile_eggs: Optional[int] = Field(None, ge=0, description="Number of fertile eggs")
    incubation_start: Optional[datetime] = Field(None, description="Incubation start date")
    incubation_end: Optional[datetime] = Field(None, description="Incubation end date")
    band_date: Optional[datetime] = Field(None, description="Banding date")
    number_of_offspring: Optional[int] = Field(None, ge=0, description="Number of offspring")
    breeder_id: Optional[int] = Field(None, description="Breeder ID (used when auto-creating birds)")
    owner_id: Optional[int] = Field(None, description="Owner ID (used when auto-creating birds)")


class PairsResponse(PairsBase):
    """Schema for pairs response (with ID and timestamps)."""
    id: int
    cock: int
    hen: int
    date_paired: datetime
    incubation_start: Optional[datetime] = None
    incubation_end: Optional[datetime] = None
    band_date: Optional[datetime] = None

    class Config:
        from_attributes = True

