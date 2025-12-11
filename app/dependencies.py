from sqlmodel import Session
from api.app.database.db import engine
from fastapi import Depends, HTTPException, status, Request
from api.app.core.security import decode_token
from api.app.schemas.auth import TokenData


async def get_current_user(request: Request) -> TokenData:
    """
    Verify JWT access token from HttpOnly cookie and return user data.
    Raises 401 if token is invalid, expired, or revoked.
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure this is an access token, not a refresh token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id: int = payload.get("user_id")
    email: str = payload.get("sub")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return TokenData(user_id=user_id, sub=email)


def get_db():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session