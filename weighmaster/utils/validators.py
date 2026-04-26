"""Input validators for plates, weights, and passwords."""
from __future__ import annotations

import re

from weighmaster.config import MAX_WEIGHT_KG, OVERLOAD_KG

_PLATE_RE = re.compile(r"^[A-Z0-9\s\-]{2,15}$")


def validate_plate(plate: str) -> tuple[bool, str]:
    clean = plate.strip().upper()
    if not clean:
        return False, "Vehicle plate is required"
    if not _PLATE_RE.match(clean):
        return False, "Invalid plate format (letters, numbers, spaces, hyphens only)"
    return True, ""


def normalise_plate(plate: str) -> str:
    return plate.strip().upper()


def validate_weight(weight_kg: float) -> tuple[bool, str]:
    if weight_kg < 0:
        return False, "Weight cannot be negative — check scale zeroing"
    if weight_kg >= OVERLOAD_KG:
        return False, f"OVERLOAD — weight {weight_kg:.2f} kg exceeds {OVERLOAD_KG:.0f} kg"
    if weight_kg > MAX_WEIGHT_KG:
        return False, f"Weight {weight_kg:.2f} kg exceeds maximum {MAX_WEIGHT_KG:.0f} kg"
    return True, ""


def validate_password(password: str) -> tuple[bool, str, str]:
    """Returns (is_valid, error_msg, strength: 'weak'|'medium'|'strong')."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters", "weak"
    if len(password.encode("utf-8")) > 72:
        return False, "Password too long (max 72 bytes)", "weak"
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    score = sum([has_upper, has_digit, has_special, len(password) >= 12])
    if score >= 3:
        strength = "strong"
    elif score >= 1:
        strength = "medium"
    else:
        strength = "weak"
    return True, "", strength
