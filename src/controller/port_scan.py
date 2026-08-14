from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple


class PortScanDetector:
    def __init__(self, window_s: float, threshold_ports: int) -> None:
        self.window_s = window_s
        self.threshold_ports = threshold_ports
        self._dst_ports: Dict[str, Deque[Tuple[float, int]]] = defaultdict(
            lambda: deque(maxlen=600)
        )
        self._alerted: Dict[str, bool] = defaultdict(bool)

    def flag(self, dst_ip: str, dst_port: int, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        ports = self._dst_ports[dst_ip]
        ports.append((now, dst_port))

        while ports and (now - ports[0][0]) > self.window_s:
            ports.popleft()

        flagged = len({port for _, port in ports}) >= self.threshold_ports
        if not flagged:
            self._alerted[dst_ip] = False
        return flagged

    def should_alert(self, dst_ip: str, dst_port: int, now: float | None = None) -> bool:
        if not self.flag(dst_ip, dst_port, now):
            return False
        if self._alerted[dst_ip]:
            return False
        self._alerted[dst_ip] = True
        return True
