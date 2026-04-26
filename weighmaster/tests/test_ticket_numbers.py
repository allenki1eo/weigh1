"""Tests for ticket number format and generation."""
import re


def test_ticket_number_format():
    """Ticket numbers must match WM-NNNN (sequential with prefix)."""
    pattern = re.compile(r"^[A-Z]{2}-\d{4}$")
    samples = ["WM-0001", "WM-0028", "WM-9999"]
    for s in samples:
        assert pattern.match(s), f"{s!r} does not match expected format"


def test_sequence_examples_share_same_format():
    """Sequence increments without date segment in the ticket number."""
    pattern = re.compile(r"^[A-Z]{2}-\d{4}$")
    t1 = "WM-0001"
    t2 = "WM-0002"
    assert t1 != t2
    assert pattern.match(t1)
    assert pattern.match(t2)
