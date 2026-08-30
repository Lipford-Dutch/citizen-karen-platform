import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Header, HTTPException

DEMO_USERS = {
    "citizen": {
        "sub": "demo-citizen",
        "name": "Karen Citizen",
        "email": "karen@example.test",
        "role": "citizen",
    },
    "admin": {
        "sub": "demo-admin",
        "name": "Alex Administrator",
        "email": "admin@example.test",
        "role": "admin",
    },
    "anonymous": {
        "sub": "demo-anonymous",
        "name": "Anonymous citizen",
        "email": "anonymous@example.test",
        "role": "anonymous",
    },
}


def _secret() -> str:
    return os.getenv("JWT_SECRET", "local-demo-only-change-before-deployment")


def issue_demo_token(role: str) -> dict[str, Any]:
    if not _demo_mode():
        raise HTTPException(status_code=404, detail="Demo login is disabled")
    user = DEMO_USERS.get(role)
    if user is None:
        raise HTTPException(status_code=400, detail="Unknown demo role")
    now = datetime.now(UTC)
    claims = {
        **user,
        "iat": now,
        "exp": now + timedelta(hours=8),
        "aud": "citizen-karen-demo",
    }
    return {
        "access_token": jwt.encode(claims, _secret(), algorithm="HS256"),
        "token_type": "bearer",
        "expires_in": 28800,
        "user": user,
    }


def _demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "true").lower() == "true"


def optional_user(
    authorization: str | None = Header(default=None),
) -> dict[str, Any] | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        return jwt.decode(
            authorization.split(" ", 1)[1],
            _secret(),
            algorithms=["HS256"],
            audience="citizen-karen-demo",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def require_admin(user: dict[str, Any] | None) -> dict[str, Any]:
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
