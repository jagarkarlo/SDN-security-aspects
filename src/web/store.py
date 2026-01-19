from __future__ import annotations
import json
import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class EventItem:
    ts: str
    level: str
    msg: str
    extra: Dict[str, Any]


class DashboardStore:
    """
    Thread-safe store for:
    - KPIs (counters)
    - last events
    - timeseries buffers (ring buffers)
    - updated_at tick even without traffic
    """

    def __init__(self, max_points: int = 120, max_events: int = 60) -> None:
        self._lock = threading.Lock()

        self.started_at = utc_iso()
        self.updated_at = utc_iso()

        self.events_total = 0
        self.acl_drops_total = 0
        self.ddos_flags_total = 0
        self.allowed_total = 0

        # per-second counters (for graphs)
        self._sec_flows = 0
        self._sec_acl = 0
        self._sec_ddos = 0
        self._sec_allowed = 0

        self.labels: Deque[str] = deque(maxlen=max_points)
        self.ts_flows: Deque[int] = deque(maxlen=max_points)
        self.ts_acl: Deque[int] = deque(maxlen=max_points)
        self.ts_ddos: Deque[int] = deque(maxlen=max_points)
        self.ts_allowed: Deque[int] = deque(maxlen=max_points)

        self.last_events: Deque[EventItem] = deque(maxlen=max_events)

    def tick_1s(self) -> None:
        """Call every second to push a new datapoint into time-series buffers."""
        with self._lock:
            now = datetime.now().strftime("%H:%M:%S")
            self.labels.append(now)
            self.ts_flows.append(self._sec_flows)
            self.ts_acl.append(self._sec_acl)
            self.ts_ddos.append(self._sec_ddos)
            self.ts_allowed.append(self._sec_allowed)

            self._sec_flows = 0
            self._sec_acl = 0
            self._sec_ddos = 0
            self._sec_allowed = 0

            self.updated_at = utc_iso()

    def log(self, level: str, msg: str, **extra: Any) -> None:
        with self._lock:
            self.events_total += 1
            self.updated_at = utc_iso()
            self.last_events.appendleft(EventItem(ts=self.updated_at, level=level, msg=msg, extra=extra))

    def inc_flow(self) -> None:
        with self._lock:
            self._sec_flows += 1

    def inc_acl_drop(self) -> None:
        with self._lock:
            self.acl_drops_total += 1
            self._sec_acl += 1

    def inc_ddos_flag(self) -> None:
        with self._lock:
            self.ddos_flags_total += 1
            self._sec_ddos += 1

    def inc_allowed(self) -> None:
        with self._lock:
            self.allowed_total += 1
            self._sec_allowed += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "started_at": self.started_at,
                "updated_at": self.updated_at,
                "counters": {
                    "events_total": self.events_total,
                    "acl_drops_total": self.acl_drops_total,
                    "ddos_flags_total": self.ddos_flags_total,
                    "allowed_total": self.allowed_total,
                },
                "timeseries": {
                    "labels": list(self.labels),
                    "flows_per_sec": list(self.ts_flows),
                    "acl_drops_per_sec": list(self.ts_acl),
                    "ddos_flags_per_sec": list(self.ts_ddos),
                    "allowed_per_sec": list(self.ts_allowed),
                },
                "last_events": [
                    {"ts": e.ts, "level": e.level, "msg": e.msg, "extra": e.extra} for e in list(self.last_events)
                ],
            }

    def snapshot_json(self) -> str:
        return json.dumps(self.snapshot(), ensure_ascii=False, indent=2)
