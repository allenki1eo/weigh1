"""Multi-protocol serial scale reader — runs in a QThread."""
from __future__ import annotations

import logging
import time
from collections import deque
from typing import Deque

import serial
from PyQt6.QtCore import QThread, pyqtSignal

from weighmaster.config import (
    STABLE_THRESHOLD_KG, STABLE_DURATION_SEC, SCALE_READ_TIMEOUT
)
from weighmaster.hardware.protocols import get_protocol, ScaleProtocol

log = logging.getLogger(__name__)


class ScaleReader(QThread):
    weight_updated = pyqtSignal(float, bool, str)
    connection_ok = pyqtSignal(str)
    connection_lost = pyqtSignal(str)
    frame_error = pyqtSignal(str)

    def __init__(
        self,
        port: str = "COM3",
        baud_rate: int = 9600,
        data_bits: int = 8,
        parity: str = "E",
        stop_bits: int = 1,
        protocol: str = "xk3190",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self._protocol: ScaleProtocol = get_protocol(protocol)
        self._running = False
        self._recent: Deque[tuple[float, float]] = deque()  # (timestamp, weight)

    def parse_frame(self, raw: bytes) -> tuple[float, bool, str]:
        """Parse a frame using the selected protocol."""
        return self._protocol.parse(raw)

    def _is_truly_stable(self, weight: float, reported_stable: bool) -> bool:
        if not reported_stable:
            return False
        now = time.monotonic()
        self._recent.append((now, weight))
        cutoff = now - STABLE_DURATION_SEC
        while self._recent and self._recent[0][0] < cutoff:
            self._recent.popleft()
        if not self._recent:
            return False
        weights = [w for _, w in self._recent]
        variance = max(weights) - min(weights)
        return variance <= STABLE_THRESHOLD_KG

    def run(self) -> None:
        self._running = True
        parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
        parity = parity_map.get(self.parity, serial.PARITY_EVEN)

        while self._running:
            try:
                with serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    bytesize=self.data_bits,
                    parity=parity,
                    stopbits=self.stop_bits,
                    timeout=SCALE_READ_TIMEOUT,
                ) as ser:
                    log.info("Scale connected on %s", self.port)
                    self.connection_ok.emit(self.port)
                    self._recent.clear()
                    while self._running:
                        raw = ser.readline()
                        if not raw:
                            continue
                        try:
                            weight, reported_stable, status = self.parse_frame(raw)
                            stable = self._is_truly_stable(weight, reported_stable)
                            self.weight_updated.emit(weight, stable, status)
                        except Exception as exc:
                            self.frame_error.emit(str(exc))
            except serial.SerialException as exc:
                msg = str(exc)
                log.warning("Scale disconnected: %s", msg)
                self.connection_lost.emit(msg)
                if self._running:
                    time.sleep(3)

    def stop(self) -> None:
        self._running = False
        self.wait(3000)
