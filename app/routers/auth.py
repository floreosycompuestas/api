from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.requests import Request
from sqlmodel import Session

from api.app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token,
    revoke_token,
)
from api.app.core.config import settings
from api.app.schemas.auth import TokenResponse, TokenData, LoginRequest
from api.app.dependencies import get_db, get_current_user
from api.app.crud.user_crud import UserCRUD

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, refresh_cookie_max_age: int = None):
    """
    Set HttpOnly cookies for access and refresh tokens.

    Args:
        response: FastAPI Response object to set cookies on
        access_token: JWT access token
        refresh_token: JWT refresh token
        refresh_cookie_max_age: Optional max age for refresh token cookie (defaults to standard 7 days)
    """
    if refresh_cookie_max_age is None:
        refresh_cookie_max_age = settings.REFRESH_COOKIE_MAX_AGE

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # ✅ Prevents JavaScript access (XSS protection)
        secure=settings.SECURE_COOKIE,  # ✅ HTTPS only in production
        samesite=settings.COOKIE_SAMESITE,  # ✅ CSRF protection
        max_age=settings.ACCESS_COOKIE_MAX_AGE,  # 15 minutes
        domain=settings.COOKIE_DOMAIN,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,      # ✅ Prevents JavaScript access (XSS protection)
        secure=settings.SECURE_COOKIE,  # ✅ HTTPS only in production
        samesite=settings.COOKIE_SAMESITE,  # ✅ CSRF protection
        max_age=refresh_cookie_max_age,  # 7 days (default) or 30 days (remember_me)
        domain=settings.COOKIE_DOMAIN,
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint. Sets JWT tokens as HttpOnly cookies.
    Accepts either username or email for login.
    Supports 'remember_me' option to extend refresh token to 30 days.
    """
    # Try to find user by email or username
    user = UserCRUD.get_user_by_email(db, credentials.username_or_email)
    if not user:
        user = UserCRUD.get_user_by_username(db, credentials.username_or_email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )

    if user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
        remember_me=credentials.remember_me
    )

    response = Response(content='', status_code=status.HTTP_200_OK)

    # Set cookies with extended expiration if "remember me" is selected
    refresh_cookie_max_age = None
    if credentials.remember_me:
        refresh_cookie_max_age = settings.REMEMBER_ME_REFRESH_TOKEN_EXPIRES_MINUTES * 60  # Convert minutes to seconds

    _set_auth_cookies(response, access_token, refresh_token, refresh_cookie_max_age)

    # Manually set response content
    import json
    response.body = json.dumps({
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email
    }).encode()
    response.headers["content-type"] = "application/json"

    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request):
    """
    Refresh access token using refresh token from HttpOnly cookie.
    Preserves 'remember me' status if originally set.
    """
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token - not authenticated",
        )

    payload = decode_token(token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    email = payload.get("sub")
    user_id = payload.get("user_id")
    remember_me = payload.get("remember_me", False)  # Preserve remember_me status

    if email is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    new_access_token = create_access_token(
        data={"sub": email, "user_id": user_id}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": email, "user_id": user_id},
        remember_me=remember_me  # Preserve remember_me status for new token
    )

    response = Response(content='', status_code=status.HTTP_200_OK)

    # Set cookies with appropriate max_age based on remember_me status
    refresh_cookie_max_age = None
    if remember_me:
        refresh_cookie_max_age = settings.REMEMBER_ME_REFRESH_TOKEN_EXPIRES_MINUTES * 60

    _set_auth_cookies(response, new_access_token, new_refresh_token, refresh_cookie_max_age)

    # Manually set response content
    import json
    response.body = json.dumps({
        "message": "Token refreshed successfully",
        "user_id": user_id,
        "email": email
    }).encode()
    response.headers["content-type"] = "application/json"

    return response


@router.post("/logout")
async def logout(request: Request, current_user: TokenData = Depends(get_current_user)):
    """
    Logout endpoint. Revokes the current access token and clears cookies.
    """
    token = request.cookies.get("access_token")

    if token:
        revoke_token(token)

    response = Response(content='{"message": "Successfully logged out"}', status_code=status.HTTP_200_OK)
    response.headers["content-type"] = "application/json"

    # Clear both cookies
    response.delete_cookie(
        key="access_token",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.SECURE_COOKIE,
        samesite=settings.COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key="refresh_token",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.SECURE_COOKIE,
        samesite=settings.COOKIE_SAMESITE,
    )

    return response


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Returns 200 if user is authenticated, otherwise returns 401.
    Used by frontend to check if user is logged in.
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.sub,
        "authenticated": True,
    }

