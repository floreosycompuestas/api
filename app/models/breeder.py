from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from datetime import datetime
from api.app.database.base import Base


class Breeder(Base):
    __tablename__ = "breeder"

    id = Column(Integer, primary_key=True, index=True)
    breeder_code = Column(String(80), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("owner.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint on breeder_code and organization_id
    __table_args__ = (
        UniqueConstraint('breeder_code', 'organization_id', name='uq_breeder_code_org_id'),
    )
