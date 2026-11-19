"""
JWT authentication middleware for SafeStar Service API.
"""

import os
from functools import wraps

import jwt
from flask import request, jsonify

JWT_SECRET = os.environ.get("JWT_SECRET", "safestar-secret")
JWT_ALGORITHM = "HS256"


def require_auth(f):
    """Decorator that validates a JWT Bearer token on every request."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify(
                    {
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "Missing or malformed Authorization header.",
                            "details": {},
                        }
                    }
                ),
                401,
            )

        token = auth_header[len("Bearer "):]
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "TOKEN_EXPIRED",
                            "message": "The provided JWT token has expired.",
                            "details": {},
                        }
                    }
                ),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "INVALID_TOKEN",
                            "message": "The provided JWT token is invalid.",
                            "details": {},
                        }
                    }
                ),
                401,
            )

        return f(*args, **kwargs)

    return decorated
