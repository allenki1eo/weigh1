"""Tests for plate and password validators."""
import pytest
from weighmaster.utils.validators import validate_plate, normalise_plate, validate_password


def test_valid_plates():
    for plate in ["T 245 DAR", "KCA 123A", "T245DAR", "TZ-001"]:
        valid, _ = validate_plate(plate)
        assert valid, f"Expected {plate!r} to be valid"


def test_invalid_plates():
    for plate in ["", "  ", "!@#$%", "A" * 20]:
        valid, _ = validate_plate(plate)
        assert not valid, f"Expected {plate!r} to be invalid"


def test_normalise_plate():
    assert normalise_plate("t 245 dar") == "T 245 DAR"
    assert normalise_plate("  kca123a  ") == "KCA123A"


def test_password_too_short():
    valid, msg, _ = validate_password("abc")
    assert not valid
    assert "8" in msg


def test_password_weak():
    _, _, strength = validate_password("password")
    assert strength in ("weak", "medium")


def test_password_strong():
    _, _, strength = validate_password("Str0ng!Pass#2026")
    assert strength == "strong"


def test_password_valid():
    valid, _, _ = validate_password("ValidPass1!")
    assert valid
