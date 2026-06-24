import uuid
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import database

# In-memory session store: token -> user email
sessions: dict[str, str] = {}

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    description="Paste your session token here"
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_session_token(email: str) -> str:
    """Generate a new session token and store the email it belongs to."""
    token = str(uuid.uuid4())
    sessions[token] = email
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    Extract Bearer token from Authorization header and return the
    email of the logged-in user if the token is valid.
    """
    token = credentials.credentials
    email = sessions.get(token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return email