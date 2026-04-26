"""Bilingual string translator — always use t("key") for display strings."""
from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_LANG = "en"
_STRINGS: dict[str, dict[str, str]] = {}


def _i18n_dir() -> Path:
    """Return the i18n directory — works in normal Python and PyInstaller bundles."""
    import sys
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "weighmaster" / "i18n"
    return Path(__file__).parent


def _load() -> None:
    base = _i18n_dir()
    for lang in ("en", "sw"):
        path = base / f"{lang}.json"
        try:
            with open(path, encoding="utf-8") as f:
                _STRINGS[lang] = json.load(f)
        except Exception as exc:
            log.error("Failed to load %s.json: %s", lang, exc)
            _STRINGS[lang] = {}


_load()


def set_language(lang: str) -> None:
    global _LANG
    if lang in _STRINGS:
        _LANG = lang
    else:
        log.warning("Unknown language: %s", lang)


def get_language() -> str:
    return _LANG


def t(key: str, **kwargs) -> str:
    text = _STRINGS.get(_LANG, {}).get(key)
    if text is None:
        text = _STRINGS.get("en", {}).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text
