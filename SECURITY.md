# Application Security Implementation

## Overview
The application is now fully secured with JWT-based authentication, password hashing, token revocation, and protected routes.

## Security Features Implemented

### 1. **JWT Authentication**
- **Access Tokens**: Short-lived tokens (30 min default) for API requests
- **Refresh Tokens**: Long-lived tokens (7 days default) for getting new access tokens
- **Token Type Validation**: Tokens include `type` field to prevent misuse
- **JTI (JWT ID)**: Unique ID per token for revocation support

### 2. **Password Security**
- **Bcrypt Hashing**: All passwords hashed with bcrypt (salted, iterated)
- **Password Verification**: Constant-time comparison to prevent timing attacks
- Located in: `api/app/core/security.py`

### 3. **Token Revocation**
- **Logout Support**: Tokens can be revoked immediately via logout endpoint
- **In-Memory Storage**: Currently uses in-memory set (replace with Redis for production)
- **JTI Tracking**: Each token has unique ID for revocation

### 4. **Protected Routes**
All user endpoints require valid JWT access token:
- `GET /users/` - List users (protected)
- `GET /users/me` - Get current user profile (protected)
- `GET /users/{username}` - Get specific user (protected)

### 5. **CORS Configuration**
- Restricted to `ALLOWED_HOSTS` from environment
- Credentials allowed only for specified origins
- Configured in: `api/app/main.py`

## API Endpoints

### Authentication Endpoints
All auth endpoints are prefixed with `/auth`

#### 1. Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=rick@example.com&password=secret123
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Demo Credentials:**
- Email: `rick@example.com`, Password: `secret123`
- Email: `morty@example.com`, Password: `secret456`

#### 2. Refresh Token
```bash
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 3. Logout
```bash
POST /auth/logout
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### Protected Endpoints

#### Get Current User
```bash
GET /users/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "user_id": 1,
  "email": "rick@example.com"
}
```

## Configuration

### Environment Variables (`.env`)
```env
# Required
SECRET_KEY=your-super-secret-key-min-32-characters-long!!!

# Optional (defaults shown)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=30
REFRESH_TOKEN_EXPIRES_MINUTES=10080
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fyc_db
```

**Important**: Generate a strong `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Architecture

### Core Security Module
**File**: `api/app/core/security.py`
- `hash_password()` - Hash passwords with bcrypt
- `verify_password()` - Verify plain password against hash
- `create_access_token()` - Create short-lived JWT
- `create_refresh_token()` - Create long-lived JWT
- `decode_token()` - Verify & decode JWT, check revocation
- `revoke_token()` - Revoke token by jti

### Authentication Router
**File**: `api/app/routers/auth.py`
- Login endpoint with email/username + password
- Refresh endpoint to get new access token
- Logout endpoint to revoke token
- Demo user database (replace with real DB)

### Dependencies
**File**: `api/app/dependencies.py`
- `get_current_user()` - Dependency to verify JWT in requests
- Checks token validity, type, expiration, and revocation status
- Returns `TokenData` with user_id and email

### User Routes
**File**: `api/app/routers/users.py`
- All routes protected with `Depends(get_current_user)`
- Returns current user info or list of users

## Production Checklist

### ⚠️ Before Going to Production

1. **Replace Demo Users**
   - Remove `DEMO_USERS` from `api/app/routers/auth.py`
   - Implement real database queries with User model

2. **Use External Token Revocation**
   - Replace in-memory `revoked_tokens` set with Redis
   - Allows horizontal scaling and persistence

3. **Secure SECRET_KEY**
   - Generate strong key: `secrets.token_urlsafe(32)`
   - Store in `.env` or secrets manager (AWS Secrets, HashiCorp Vault, etc.)
   - Rotate periodically

4. **HTTPS Only**
   - Enable HTTPS in production
   - Set `secure=True` in cookies if using them
   - Add HSTS headers

5. **Rate Limiting**
   - Add rate limiting to `/auth/login` to prevent brute force
   - Use `slowapi` or similar library

6. **Token Expiration**
   - Review `ACCESS_TOKEN_EXPIRES_MINUTES` (30 min default)
   - Review `REFRESH_TOKEN_EXPIRES_MINUTES` (7 days default)
   - Adjust based on security requirements

7. **CORS Settings**
   - Restrict `ALLOWED_HOSTS` to specific frontend domains
   - Example: `ALLOWED_HOSTS=https://app.example.com,https://www.example.com`

8. **Logging & Monitoring**
   - Log failed login attempts
   - Monitor token usage patterns
   - Alert on suspicious activity

9. **Input Validation**
   - Already using Pydantic schemas for validation
   - Email validation via `EmailStr`
   - Add more specific validators as needed

10. **Password Requirements**
    - Enforce strong password requirements at signup
    - Add endpoint to change password
    - Implement password reset flow

## Testing Authentication Flow

### 1. Login and Get Tokens
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=rick@example.com&password=secret123"
```

### 2. Use Access Token
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer {access_token}"
```

### 3. Refresh Token
```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Authorization: Bearer {refresh_token}"
```

### 4. Logout (Revoke Token)
```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer {access_token}"
```

### 5. Verify Token is Revoked
```bash
# This should now fail with 401
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer {revoked_access_token}"
```

## Security Best Practices Applied

✅ **Password Security**
- Bcrypt hashing with salt and iterations
- Never store plain passwords

✅ **JWT Security**
- HS256 algorithm with strong secret
- Expiration timestamps
- Unique JTI for revocation
- Token type validation

✅ **Token Management**
- Separate access and refresh tokens
- Short access token lifespan
- Refresh token rotation

✅ **Route Protection**
- All sensitive endpoints require authentication
- Dependency injection for clean code

✅ **Error Handling**
- Generic error messages (don't reveal user existence)
- Proper HTTP status codes

✅ **CORS Configuration**
- Restricted to allowed origins
- Credentials only from trusted hosts

## Files Modified

1. `api/app/core/security.py` - Core security functions
2. `api/app/routers/auth.py` - Authentication endpoints
3. `api/app/dependencies.py` - Token verification dependency
4. `api/app/routers/users.py` - Protected user routes
5. `api/app/main.py` - Include auth router

## Next Steps

1. Replace demo users with real database queries
2. Set up `.env` with strong `SECRET_KEY`
3. Test login/logout flow
4. Implement Redis for token revocation (production)
5. Add rate limiting to login endpoint
6. Add password reset flow
7. Add user registration endpoint
8. Implement role-based access control (RBAC)

