"""Scale protocol parsers."""
from __future__ import annotations

import abc
import logging
import re

log = logging.getLogger(__name__)


class ScaleProtocol(abc.ABC):
    """Abstract base for scale serial protocols."""

    @abc.abstractmethod
    def parse(self, raw: bytes) -> tuple[float, bool, str]:
        """Parse raw bytes into (weight_kg, reported_stable, status)."""


class XK3190Protocol(ScaleProtocol):
    """XK3190-DS1 protocol parser.

    Format: ``W<mode><10-digit-weight>kg...`` where mode ``G`` = stable.
    """

    def parse(self, raw: bytes) -> tuple[float, bool, str]:
        text = raw.decode("ascii", errors="replace").strip()
        if text == "OL":
            return 0.0, False, "overload"
        if text == "UL":
            return 0.0, False, "underload"
        if len(text) < 14:
            raise ValueError(f"Frame too short: {repr(text)}")
        if text[0] != "W":
            raise ValueError(f"Bad frame header: {repr(text[0])}")
        mode_char = text[1]
        weight_str = text[2:12].strip()
        try:
            weight = float(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: {repr(weight_str)}")
        reported_stable = mode_char == "G"
        status = "stable" if reported_stable else "unstable"
        return weight, reported_stable, status


class ToledoProtocol(ScaleProtocol):
    """Toledo / Mettler Toledo SICS protocol parser.

    Examples::

        S D   12345 kg   (stable)
        S I   12345 kg   (unstable)
        S +   12345 kg   (overload)
        S -   12345 kg   (underload)
    """

    _SICS_RE = re.compile(
        r"^S\s+(?P<mode>[DI+\-])\s+(?P<weight>[+\-]?\d+(?:\.\d+)?)\s*(?:kg|g|t)?",
        re.IGNORECASE,
    )

    def parse(self, raw: bytes) -> tuple[float, bool, str]:
        text = raw.decode("ascii", errors="replace").strip()
        # Simple overload / underload indicators without weight
        if text.upper() in ("S +", "S +++", "S +++++"):
            return 0.0, False, "overload"
        if text.upper() in ("S -", "S ---", "S -----"):
            return 0.0, False, "underload"

        match = self._SICS_RE.match(text)
        if not match:
            raise ValueError(f"Cannot parse Toledo frame: {repr(text)}")

        mode = match.group("mode").upper()
        weight_str = match.group("weight")
        try:
            weight = float(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: {repr(weight_str)}")

        if mode == "D":
            return weight, True, "stable"
        if mode == "I":
            return weight, False, "unstable"
        if mode == "+":
            return 0.0, False, "overload"
        if mode == "-":
            return 0.0, False, "underload"
        return weight, False, "unstable"


class AveryProtocol(ScaleProtocol):
    """Avery Berkel protocol parser.

    Formats::

        01,   12345,kg
        02,  -12345,kg
        Or plain numeric ASCII
    """

    _AVERY_RE = re.compile(
        r"^(?:\d{2},)?\s*(?P<weight>[+\-]?\d+(?:\.\d+)?)\s*(?:,kg|,lb|kg|lb)?",
        re.IGNORECASE,
    )

    def parse(self, raw: bytes) -> tuple[float, bool, str]:
        text = raw.decode("ascii", errors="replace").strip()
        match = self._AVERY_RE.match(text)
        if not match:
            raise ValueError(f"Cannot parse Avery frame: {repr(text)}")
        weight_str = match.group("weight")
        try:
            weight = float(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: {repr(weight_str)}")
        # Avery streams typically do not contain a stability flag;
        # assume reported_stable=True and let variance-based checks decide.
        return weight, True, "stable"


class GenericProtocol(ScaleProtocol):
    """Generic / continuous protocol parser.

    Plain ASCII number such as ``12345.67`` or ``  12345  ``.
    """

    _GENERIC_RE = re.compile(r"(?P<weight>[+\-]?\d+(?:\.\d+)?)")

    def parse(self, raw: bytes) -> tuple[float, bool, str]:
        text = raw.decode("ascii", errors="replace").strip()
        match = self._GENERIC_RE.search(text)
        if not match:
            raise ValueError(f"Cannot parse generic frame: {repr(text)}")
        weight_str = match.group("weight")
        try:
            weight = float(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: {repr(weight_str)}")
        # Generic protocols rarely report stability; assume stable.
        return weight, True, "stable"


_PROTOCOL_MAP: dict[str, type[ScaleProtocol]] = {
    "xk3190": XK3190Protocol,
    "toledo": ToledoProtocol,
    "avery": AveryProtocol,
    "generic": GenericProtocol,
}


def get_protocol(name: str) -> ScaleProtocol:
    """Return a protocol instance by name."""
    try:
        return _PROTOCOL_MAP[name.lower()]()
    except KeyError:
        raise ValueError(f"Unknown scale protocol: {name!r}")
