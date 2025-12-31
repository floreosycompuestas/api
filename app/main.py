from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Union
from sqlalchemy import text

from api.app.routers import users, auth, bird, breeder, role, organization, owner, pairs
from api.app.internal import admin
from api.app.core.config import settings
from api.app.dependencies import get_db
from api.app.core.redis_client import RedisClient

app: FastAPI = FastAPI(title=settings.TITLE, description=settings.DESCRIPTION, version=settings.VERSION)

# CORS configuration - restrict in production
allowed_origins = settings.ALLOWED_HOSTS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,  # ✅ Allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bird.router)
app.include_router(breeder.router)
app.include_router(role.router)
app.include_router(organization.router)
app.include_router(owner.router)
app.include_router(pairs.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Hello API Applications!"}

@app.get("/health")
def health_check_all() -> Dict[str, Any]:
    """Check overall application health (database and Redis)."""
    db_health = health_check_db()
    redis_health = health_check_redis()

    overall_status = "ok" if db_health["status"] == "ok" and redis_health["status"] == "ok" else "error"

    return {
        "status": overall_status,
        "database": db_health,
        "redis": redis_health
    }

@app.get("/health/db")
def health_check_db() -> Dict[str, Union[str, None]]:
    """Check database connection health."""
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "service": "database"}
    except Exception as e:
        return {"status": "error", "service": "database", "message": str(e)}

@app.get("/health/redis")
def health_check_redis() -> Dict[str, Union[str, None]]:
    """Check Redis connection health."""
    if RedisClient.health_check():
        return {"status": "ok", "service": "redis"}
    else:
        return {"status": "error", "service": "redis", "message": "Redis connection failed"}
