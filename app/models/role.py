"""
Role model for role-based access control.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func
from api.app.core.enums import RoleEnum
from api.app.database.base import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(RoleEnum), unique=True, nullable=False, index=True)
    description = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False, index=True)
    assigned_at = Column(DateTime, default=func.now(), nullable=False)
