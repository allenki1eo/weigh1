"""Tests for scale protocol parsers."""
import pytest

from weighmaster.hardware.protocols import (
    XK3190Protocol,
    ToledoProtocol,
    AveryProtocol,
    GenericProtocol,
)


@pytest.fixture
def reader():
    # Legacy compatibility: return an object with a parse_frame method
    class _LegacyReader:
        def __init__(self):
            self._protocol = XK3190Protocol()

        def parse_frame(self, raw: bytes):
            return self._protocol.parse(raw)

    return _LegacyReader()


def test_stable_frame(reader):
    raw = b"WG0034260.00kgA\r"
    weight, stable, status = reader.parse_frame(raw)
    assert weight == 34260.0
    assert stable is True
    assert status == "stable"


def test_unstable_frame(reader):
    raw = b"WU0034260.00kgA\r"
    weight, stable, status = reader.parse_frame(raw)
    assert stable is False
    assert status == "unstable"


def test_overload_frame(reader):
    weight, stable, status = reader.parse_frame(b"OL\r")
    assert status == "overload"
    assert stable is False


def test_underload_frame(reader):
    weight, stable, status = reader.parse_frame(b"UL\r")
    assert status == "underload"


def test_zero_weight(reader):
    raw = b"WG0000000.00kgA\r"
    weight, stable, status = reader.parse_frame(raw)
    assert weight == 0.0


def test_bad_frame_raises(reader):
    with pytest.raises(ValueError):
        reader.parse_frame(b"BADDATA\r")


# ---- Toledo / SICS -------------------------------------------------


def test_toledo_stable():
    p = ToledoProtocol()
    w, s, st = p.parse(b"S D   12345 kg\r")
    assert w == 12345.0
    assert s is True
    assert st == "stable"


def test_toledo_unstable():
    p = ToledoProtocol()
    w, s, st = p.parse(b"S I   12345 kg\r")
    assert w == 12345.0
    assert s is False
    assert st == "unstable"


def test_toledo_overload():
    p = ToledoProtocol()
    w, s, st = p.parse(b"S +   12345 kg\r")
    assert st == "overload"
    assert s is False


def test_toledo_underload():
    p = ToledoProtocol()
    w, s, st = p.parse(b"S -   12345 kg\r")
    assert st == "underload"
    assert s is False


def test_toledo_simple_overload():
    p = ToledoProtocol()
    w, s, st = p.parse(b"S +\r")
    assert st == "overload"


# ---- Avery Berkel --------------------------------------------------


def test_avery_comma_format():
    p = AveryProtocol()
    w, s, st = p.parse(b"01,   12345,kg\r")
    assert w == 12345.0
    assert s is True


def test_avery_plain_numeric():
    p = AveryProtocol()
    w, s, st = p.parse(b"  12345  \r")
    assert w == 12345.0
    assert s is True


# ---- Generic / Continuous --------------------------------------------


def test_generic_decimal():
    p = GenericProtocol()
    w, s, st = p.parse(b"12345.67\r")
    assert w == 12345.67
    assert s is True


def test_generic_padded():
    p = GenericProtocol()
    w, s, st = p.parse(b"  12345  \r")
    assert w == 12345.0
    assert s is True
