from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Response after successful login/refresh - tokens sent via HttpOnly cookies"""
    message: str = "Login successful"
    user_id: int
    email: str


class CookieTokenResponse(BaseModel):
    """Response with token data - for internal use only, not sent to client"""
    access_token: str
    refresh_token: str
    user_id: int
    email: str


class TokenData(BaseModel):
    user_id: int
    sub: str


class UserInfoResponse(BaseModel):
    """Response for GET /me endpoint - current authenticated user information"""
    user_id: int
    email: str


class LoginRequest(BaseModel):
    """Custom login request - accepts either email or username."""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(min_length=6, max_length=60, description="User password")
    remember_me: bool = Field(default=False, description="Extend refresh token expiration to 30 days")
