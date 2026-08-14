import json
import unittest

from src.web.store import DashboardStore


class DashboardStoreTest(unittest.TestCase):
    def test_snapshot_tracks_security_counters_and_recent_events(self):
        store = DashboardStore(max_points=3, max_events=2)

        store.inc_flow()
        store.inc_acl_drop()
        store.inc_ddos_flag()
        store.inc_allowed()
        store.log("INFO", "Switch connected", dpid=1)
        store.log("WARN", "ACL DROP", src="10.0.0.1", dst="10.0.0.2")

        snapshot = store.snapshot()

        self.assertEqual(snapshot["counters"], {
            "events_total": 2,
            "acl_drops_total": 1,
            "ddos_flags_total": 1,
            "allowed_total": 1,
        })
        self.assertEqual(snapshot["last_events"][0]["msg"], "ACL DROP")
        self.assertEqual(snapshot["last_events"][0]["extra"]["src"], "10.0.0.1")

    def test_tick_rotates_second_counters_and_keeps_a_bounded_history(self):
        store = DashboardStore(max_points=2)

        store.inc_flow()
        store.inc_allowed()
        store.tick_1s()
        store.inc_acl_drop()
        store.tick_1s()
        store.tick_1s()

        snapshot = store.snapshot()

        self.assertEqual(len(snapshot["timeseries"]["labels"]), 2)
        self.assertEqual(snapshot["timeseries"]["flows_per_sec"], [0, 0])
        self.assertEqual(snapshot["timeseries"]["acl_drops_per_sec"], [1, 0])
        self.assertEqual(snapshot["timeseries"]["allowed_per_sec"], [0, 0])

    def test_snapshot_json_is_valid_json(self):
        store = DashboardStore()
        store.log("INFO", "Dashboard ready")

        snapshot = json.loads(store.snapshot_json())

        self.assertEqual(snapshot["last_events"][0]["msg"], "Dashboard ready")


if __name__ == "__main__":
    unittest.main()