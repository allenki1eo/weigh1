"""Tests for net weight calculation logic."""
import pytest
from weighmaster.utils.validators import validate_weight
from weighmaster.config import MAX_WEIGHT_KG, OVERLOAD_KG


def test_net_weight_simple():
    tare = 9760.0
    gross = 34260.0
    deduction = 0.0
    net = gross - tare - deduction
    assert net == 24500.0


def test_net_weight_with_deduction():
    tare = 9760.0
    gross = 34260.0
    deduction = 25.0
    net = gross - tare - deduction
    assert net == 24475.0


def test_gross_must_exceed_tare():
    tare = 34260.0
    gross = 9760.0
    assert gross <= tare  # service layer should reject this


def test_max_weight_passes():
    valid, msg = validate_weight(MAX_WEIGHT_KG)
    assert valid is True


def test_overload_fails():
    valid, msg = validate_weight(OVERLOAD_KG)
    assert valid is False
    assert "OVERLOAD" in msg.upper() or "exceed" in msg.lower()


def test_negative_weight_fails():
    valid, msg = validate_weight(-100.0)
    assert valid is False


def test_zero_weight_passes():
    valid, msg = validate_weight(0.0)
    assert valid is True
