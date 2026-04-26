"""Authentication and session management."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from passlib.context import CryptContext

from weighmaster.database.connection import get_session
from weighmaster.database.models import User
from weighmaster.config import LOGIN_LOCKOUT_ATTEMPTS, LOGIN_LOCKOUT_SEC

log = logging.getLogger(__name__)

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory lockout state: username -> (failure_count, lockout_until)
_lockouts: dict[str, tuple[int, float]] = {}


class AuthError(Exception):
    pass


class LockedOutError(AuthError):
    def __init__(self, seconds_remaining: int):
        self.seconds_remaining = seconds_remaining
        super().__init__(f"Account locked for {seconds_remaining}s")


class InvalidCredentialsError(AuthError):
    pass


def hash_password(plain: str) -> str:
    # bcrypt has a 72-byte limit; truncate cleanly to avoid library errors
    plain_bytes = plain.encode("utf-8")
    if len(plain_bytes) > 72:
        plain = plain_bytes[:72].decode("utf-8", errors="ignore")
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def check_lockout(username: str) -> None:
    if username not in _lockouts:
        return
    failures, lockout_until = _lockouts[username]
    if failures >= LOGIN_LOCKOUT_ATTEMPTS and lockout_until > time.monotonic():
        remaining = int(lockout_until - time.monotonic()) + 1
        raise LockedOutError(remaining)
    if lockout_until <= time.monotonic():
        del _lockouts[username]


def record_failure(username: str) -> int:
    failures, _ = _lockouts.get(username, (0, 0.0))
    failures += 1
    lockout_until = 0.0
    if failures >= LOGIN_LOCKOUT_ATTEMPTS:
        lockout_until = time.monotonic() + LOGIN_LOCKOUT_SEC
    _lockouts[username] = (failures, lockout_until)
    return failures


def clear_failures(username: str) -> None:
    _lockouts.pop(username, None)


def login(username: str, password: str) -> User:
    from weighmaster.services import audit_service
    username = username.strip().lower()
    check_lockout(username)

    with get_session() as session:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if user is None or not verify_password(password, user.password_hash):
            record_failure(username)
            dummy_user = User(id=0, username=username, full_name="", role="operator")
            try:
                audit_service.log_action(
                    dummy_user, "LOGIN_FAILED", "User", details={"username": username}
                )
            except Exception:
                pass
            raise InvalidCredentialsError("Invalid username or password")

        clear_failures(username)
        user.last_login = datetime.now()
        session.add(user)

        # Detach a copy for use outside session
        session.expunge(user)
        import sqlalchemy
        sqlalchemy.orm.make_transient(user)

    try:
        from weighmaster.services import audit_service
        audit_service.log_action(user, "LOGIN", "User", entity_id=user.id)
    except Exception:
        pass

    return user


def create_user(
    creator: User,
    username: str,
    full_name: str,
    password: str,
    role: str = "operator",
) -> User:
    from weighmaster.services import audit_service
    if role not in ("admin", "operator"):
        raise ValueError(f"Invalid role: {role}")

    with get_session() as session:
        existing = session.query(User).filter_by(username=username.lower()).first()
        if existing:
            raise ValueError(f"Username '{username}' already exists")

        user = User(
            username=username.strip().lower(),
            full_name=full_name.strip(),
            password_hash=hash_password(password),
            role=role,
            created_by=creator.id,
        )
        session.add(user)
        session.flush()
        uid = user.id

    audit_service.log_action(
        creator, "USER_CREATE", "User", entity_id=uid,
        details={"username": username, "role": role},
    )


def change_password(user: User, new_password: str) -> None:
    from weighmaster.services import audit_service
    with get_session() as session:
        db_user = session.query(User).filter_by(id=user.id).first()
        if db_user is None:
            raise ValueError("User not found")
        db_user.password_hash = hash_password(new_password)

    audit_service.log_action(user, "PASSWORD_CHANGED", "User", entity_id=user.id)


def deactivate_user(admin: User, target_user_id: int) -> None:
    from weighmaster.services import audit_service
    with get_session() as session:
        target = session.query(User).filter_by(id=target_user_id).first()
        if target is None:
            raise ValueError("User not found")
        target.is_active = False

    audit_service.log_action(
        admin, "USER_DEACTIVATE", "User", entity_id=target_user_id
    )


def check_permission(user: User, action: str) -> bool:
    """Check if user can perform an action.
    
    Special case: manual_weight is allowed for operators
    if company.allow_manual_weight is True.
    """
    admin_only = {
        "void_ticket", "user_management",
        "all_reports", "settings", "audit_log", "view_all_tickets",
    }
    if action == "manual_weight":
        if user.role == "admin":
            return True
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Company
        with get_session() as session:
            company = session.query(Company).first()
            return bool(company and company.allow_manual_weight)
    if action in admin_only:
        return user.role == "admin"
    return True


def create_first_admin(
    username: str, full_name: str, password: str
) -> User:
    with get_session() as session:
        user = User(
            username=username.strip().lower(),
            full_name=full_name.strip(),
            password_hash=hash_password(password),
            role="admin",
        )
        session.add(user)
        session.flush()
        uid = user.id

    with get_session() as session:
        return session.query(User).filter_by(id=uid).first()
