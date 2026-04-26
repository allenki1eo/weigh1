"""Dev-mode scale simulator — identical interface to ScaleReader."""
from __future__ import annotations

import logging
import random
import time

from PyQt6.QtCore import pyqtSignal

from weighmaster.hardware.scale_reader import ScaleReader
from weighmaster.config import STABLE_DURATION_SEC

log = logging.getLogger(__name__)

_TARE_MIN = 8_000.0
_TARE_MAX = 14_000.0
_GROSS_MIN = 20_000.0
_GROSS_MAX = 75_000.0
_RAMP_STEP = 500.0
_RAMP_INTERVAL = 0.1
_JITTER_PROB = 0.08


class ScaleSimulator(ScaleReader):
    """Simulates a loaded weighbridge for development without hardware."""

    weight_updated = pyqtSignal(float, bool, str)
    connection_ok = pyqtSignal(str)
    connection_lost = pyqtSignal(str)
    frame_error = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(port="SIM", parent=parent)
        self._target_weight: float = random.uniform(_TARE_MIN, _TARE_MAX)
        self._current_weight: float = 0.0
        self._stable_since: float | None = None
        self._tare_captured = False
        self._override: float | None = None

    def set_weight(self, kg: float) -> None:
        """Force a specific weight — used by unit tests."""
        self._override = kg

    def capture_tare(self) -> None:
        self._tare_captured = True
        self._current_weight = 0.0
        self._target_weight = random.uniform(_GROSS_MIN, _GROSS_MAX)
        self._stable_since = None

    def run(self) -> None:
        self._running = True
        log.info("Scale simulator started")
        self.connection_ok.emit("SIM")

        while self._running:
            if self._override is not None:
                w = self._override
            else:
                if abs(self._current_weight - self._target_weight) > _RAMP_STEP:
                    step = _RAMP_STEP if self._current_weight < self._target_weight else -_RAMP_STEP
                    self._current_weight += step
                else:
                    self._current_weight = self._target_weight

                if random.random() < _JITTER_PROB:
                    w = self._current_weight + random.uniform(-200.0, 200.0)
                    self._stable_since = None
                else:
                    w = self._current_weight

            near_target = abs(w - self._target_weight) <= 10.0
            if near_target and self._stable_since is None:
                self._stable_since = time.monotonic()

            settled = (
                self._stable_since is not None
                and (time.monotonic() - self._stable_since) >= STABLE_DURATION_SEC
            )
            is_stable = near_target and settled
            status = "stable" if is_stable else "unstable"
            self.weight_updated.emit(round(w, 2), is_stable, status)
            time.sleep(_RAMP_INTERVAL)
