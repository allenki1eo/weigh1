"""Append-only audit log writer."""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from weighmaster.database.connection import get_session
from weighmaster.database.models import AuditLog, User

log = logging.getLogger(__name__)


def log_action(
    user: User,
    action: str,
    entity: str,
    entity_id: Optional[int] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    try:
        with get_session() as session:
            entry = AuditLog(
                user_id=user.id,
                username=user.username,
                action=action,
                entity=entity,
                entity_id=entity_id,
                details=json.dumps(details or {}),
            )
            session.add(entry)
    except Exception as exc:
        log.error("Audit log write failed: %s", exc)
