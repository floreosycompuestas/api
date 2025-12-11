"""
Role enumerations for role-based access control.
"""

from enum import Enum


class RoleEnum(str, Enum):
    """Valid role names in the system."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    BREEDER = "breeder"
    OWNER = "owner"

    def __str__(self) -> str:
        return self.value

