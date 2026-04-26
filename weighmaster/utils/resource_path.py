"""Resource path resolver — handles both normal and PyInstaller frozen execution."""
from __future__ import annotations

import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Return the absolute path to a bundled resource.

    In a PyInstaller --onefile build everything is extracted to sys._MEIPASS.
    In --onedir and normal Python the package root is used.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        # Two levels up from this file: weighmaster/utils/ -> weighmaster/ -> project root
        base = Path(__file__).parent.parent
    return base.joinpath(*parts)
