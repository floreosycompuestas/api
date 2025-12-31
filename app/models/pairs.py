"""
SQLAlchemy model for Pairs.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from api.app.database.base import Base


class Pairs(Base):
    """Pairs model for tracking bird breeding pairs."""
    __tablename__ = "pairs"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    cock = Column(Integer, ForeignKey("bird.id"), nullable=False)
    hen = Column(Integer, ForeignKey("bird.id"), nullable=False)
    date_paired = Column(DateTime, default=func.now(), nullable=False)
    number_eggs = Column(Integer, nullable=True)
    number_fertile_eggs = Column(Integer, nullable=True)
    incubation_start = Column(DateTime, nullable=True)
    incubation_end = Column(DateTime, nullable=True)
    band_date = Column(DateTime, nullable=True)
    number_of_offspring = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint: cock, hen, season, round
    __table_args__ = (
        UniqueConstraint('cock', 'hen', 'season', 'round', name='uq_pairs_cock_hen_season_round'),
    )

