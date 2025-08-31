# backend/auth.py
import os, time, typing as t
import jwt
from functools import wraps
from flask import request, abort, g

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def make_token(payload: dict) -> str:
    now = int(time.time())
    body = {
        "iat": now,
        "exp": now + JWT_EXPIRE_MIN * 60,
        **payload,          # e.g., {"sub": "admin", "role": "Admin"}
    }
    return jwt.encode(body, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

def require_auth(roles: t.Optional[t.Iterable[str]] = None):
    roles = set(roles or [])
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                abort(401, "Missing Bearer token")
            token = auth.split(" ", 1)[1].strip()
            try:
                claims = decode_token(token)
            except Exception as e:
                abort(401, f"Invalid token: {e}")
            g.user = claims  # {sub, role, ...}
            if roles and claims.get("role") not in roles:
                abort(403, "Insufficient role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
