from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from api.app.database.base import Base


class Bird(Base):
    __tablename__ = "bird"

    id = Column(Integer, primary_key=True, index=True)
    band_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(80), nullable=True)
    dob = Column(DateTime, nullable=True)
    sex = Column(String(1), nullable=True)
    father_id = Column(Integer, ForeignKey("bird.id"), nullable=True)
    mother_id = Column(Integer, ForeignKey("bird.id"), nullable=True)
    breeder_id = Column(Integer, ForeignKey("breeder.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("breeder.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

