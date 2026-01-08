"""
Redis client for managing token revocation and caching.
Supports both standalone Redis and Redis Cluster.
"""

import redis
from redis.cluster import RedisCluster
from typing import Optional, Union
from api.app.core.config import settings


class RedisClient:
    """Redis client for token management and caching."""

    _instance: Optional[Union[redis.Redis, RedisCluster]] = None
    _is_cluster: bool = False

    @classmethod
    def get_client(cls) -> Union[redis.Redis, RedisCluster]:
        """
        Get or create Redis client instance (singleton pattern).
        Automatically detects and connects to Redis Cluster or standalone instance.

        Returns:
            Redis client instance (Redis or RedisCluster)
        """
        if cls._instance is None:
            try:
                # Check if connecting to a Redis Cluster
                if settings.REDIS_CLUSTER_ENABLED:
                    # Cluster mode - password is typically not used
                    cluster_kwargs = {
                        "host": settings.REDIS_HOST,
                        "port": settings.REDIS_PORT,
                        "decode_responses": True,
                        "socket_connect_timeout": 5,
                        "socket_keepalive": True,
                        "skip_full_coverage_check": True,  # For partial cluster coverage
                    }
                    # Only add password if provided
                    if settings.REDIS_PASSWORD:
                        cluster_kwargs["password"] = settings.REDIS_PASSWORD

                    cls._instance = RedisCluster(**cluster_kwargs)
                    cls._is_cluster = True
                else:
                    cls._instance = redis.from_url(
                        settings.REDIS_URL,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_keepalive=True,
                        health_check_interval=30
                    )
            except redis.cluster.RedisClusterException:
                # Fall back to standalone Redis if cluster connection fails
                print("Failed to connect to Redis Cluster, falling back to standalone Redis")
                cls._instance = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
        return cls._instance

    @classmethod
    def revoke_token(cls, jti: str, expiration_seconds: int) -> bool:
        """
        Revoke a token by adding its JTI to the revoked set.

        Args:
            jti: JWT ID (unique identifier)
            expiration_seconds: Time in seconds until token naturally expires

        Returns:
            True if token was revoked, False otherwise
        """
        try:
            client = cls.get_client()
            # Store revoked token with expiration matching token expiration
            # This saves memory by auto-deleting expired tokens
            client.setex(f"revoked_token:{jti}", expiration_seconds, "1")
            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False

    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        """
        Check if a token has been revoked.

        Args:
            jti: JWT ID (unique identifier)

        Returns:
            True if token is revoked, False otherwise
        """
        try:
            client = cls.get_client()
            return client.exists(f"revoked_token:{jti}") == 1
        except Exception as e:
            print(f"Error checking token revocation: {e}")
            # If Redis is down, err on the side of security
            return True

    @classmethod
    def cache_get(cls, key: str) -> Optional[str]:
        """
        Get a cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = cls.get_client()
            return client.get(key)
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    @classmethod
    def cache_set(cls, key: str, value: str, expiration_seconds: int = 3600) -> bool:
        """
        Set a cached value with expiration.

        Args:
            key: Cache key
            value: Value to cache
            expiration_seconds: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            client = cls.get_client()
            client.setex(key, expiration_seconds, value)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    @classmethod
    def cache_delete(cls, key: str) -> bool:
        """
        Delete a cached value.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            client = cls.get_client()
            client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False

    @classmethod
    def health_check(cls) -> bool:
        """
        Check if Redis is healthy and connected.

        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            client = cls.get_client()
            client.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False

