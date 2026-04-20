from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta, timezone
import bcrypt
from core.config import settings

JWT_KEY = {"kty": "oct", "k": settings.JWT_SECRET}
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode({"alg": ALGORITHM}, payload, JWT_KEY).decode("utf-8")


def verify_token(token: str) -> str:
    """Decode and validate JWT. Raises JoseError if invalid/expired."""
    try:
        claims = jwt.decode(token, JWT_KEY)
        claims.validate()
        return claims["sub"]
    except JoseError as e:
        raise ValueError(f"Invalid token: {e}")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def validate_csv_file(content: bytes) -> bool:
    """Reject files that aren't actually CSV/XLSX regardless of extension."""
    import magic
    mime = magic.from_buffer(content[:2048], mime=True)
    return mime in [
        "text/plain", "text/csv", "application/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]