"""Shared API dependencies — current-user resolution from the JWT."""
from __future__ import annotations

from datetime import timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..core.security import decode_access_token
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token", auto_error=False)

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise _CREDENTIALS_ERROR
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise _CREDENTIALS_ERROR
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise _CREDENTIALS_ERROR
    # Reject tokens issued before the user's last password change (session revocation).
    issued_at = payload.get("iat")
    changed_at = getattr(user, "password_changed_at", None)
    if issued_at and changed_at:
        if changed_at.tzinfo is None:
            changed_at = changed_at.replace(tzinfo=timezone.utc)
        # 1s slack absorbs same-second issue/change ordering.
        if issued_at < int(changed_at.timestamp()) - 1:
            raise _CREDENTIALS_ERROR
    return user
