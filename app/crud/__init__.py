"""
CRUD operations package for database models.
"""

from api.app.crud.user_crud import UserCRUD
from api.app.crud.bird_crud import BirdCRUD
from api.app.crud.breeder_crud import BreederCRUD
from api.app.crud.role_crud import RoleCRUD
from api.app.crud.pairs_crud import PairsCRUD

__all__ = ["UserCRUD", "BirdCRUD", "BreederCRUD", "RoleCRUD", "PairsCRUD"]
