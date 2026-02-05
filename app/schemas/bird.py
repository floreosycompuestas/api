"""
Pydantic schemas for Bird model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BirdBase(BaseModel):
    """Base schema for bird data."""
    band_id: str = Field(..., min_length=1, max_length=100, description="Unique band ID")
    name: Optional[str] = Field(None, max_length=80, description="Bird name")
    dob: Optional[datetime] = Field(None, description="Date of birth")
    sex: Optional[str] = Field(None, pattern="^[MF]?$", description="Sex (M/F)")
    father_id: Optional[int] = Field(None, description="Father bird ID")
    mother_id: Optional[int] = Field(None, description="Mother bird ID")
    breeder_id: Optional[int] = Field(None, description="Breeder ID")
    owner_id: Optional[int] = Field(None, description="Owner ID")


class BirdCreate(BaseModel):
    """Schema for creating a new bird."""
    band_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Unique band ID (auto-generated if not provided)")
    bird_year: Optional[int] = Field(None, description="Bird year for band_id generation (e.g., 2024)")
    bird_number: Optional[int] = Field(None, description="Bird number for band_id generation (e.g., 1)")
    name: Optional[str] = Field(None, max_length=80, description="Bird name")
    dob: Optional[datetime] = Field(None, description="Date of birth")
    sex: Optional[str] = Field(None, pattern="^[MF]?$", description="Sex (M/F)")
    father_band_id: Optional[str] = Field(None, max_length=100, description="Father bird band ID")
    mother_band_id: Optional[str] = Field(None, max_length=100, description="Mother bird band ID")
    breeder_id: Optional[int] = Field(None, description="Breeder ID")
    owner_id: Optional[int] = Field(None, description="Owner ID")


class BirdUpdate(BaseModel):
    """Schema for updating a bird."""
    band_id: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, max_length=80)
    dob: Optional[datetime] = None
    sex: Optional[str] = Field(None, pattern="^[MF]?$")
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    breeder_id: Optional[int] = None
    owner_id: Optional[int] = None


class BirdResponse(BirdBase):
    """Schema for bird response (with ID and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BirdDetailResponse(BirdResponse):
    """Detailed bird response with parent information."""
    pass
