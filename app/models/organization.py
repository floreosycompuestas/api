"""
SQLAlchemy model for Organization.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from api.app.database.base import Base


class Organization(Base):
    """Organization model."""
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    organization_code = Column(String(100), unique=True, nullable=False, index=True)
    organization_name = Column(String(100), nullable=False)
    organization_alias = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    country_code = Column(String(20), nullable=True)
    country_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

