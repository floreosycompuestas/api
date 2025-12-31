"""
SQLAlchemy model for Owner.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from api.app.database.base import Base


class Owner(Base):
    """Owner model."""
    __tablename__ = "owner"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

