import unittest

from src.controller.port_scan import PortScanDetector


class PortScanDetectorTest(unittest.TestCase):
    def test_flags_only_after_threshold_unique_ports_in_window(self):
        detector = PortScanDetector(window_s=5, threshold_ports=3)

        self.assertFalse(detector.flag("10.0.0.2", 1000, now=10))
        self.assertFalse(detector.flag("10.0.0.2", 1001, now=11))
        self.assertTrue(detector.flag("10.0.0.2", 1002, now=12))

    def test_duplicate_ports_do_not_raise_the_unique_port_count(self):
        detector = PortScanDetector(window_s=5, threshold_ports=3)

        self.assertFalse(detector.flag("10.0.0.2", 1000, now=10))
        self.assertFalse(detector.flag("10.0.0.2", 1000, now=11))
        self.assertFalse(detector.flag("10.0.0.2", 1001, now=12))

    def test_expired_ports_do_not_contribute_to_the_threshold(self):
        detector = PortScanDetector(window_s=5, threshold_ports=3)

        detector.flag("10.0.0.2", 1000, now=10)
        detector.flag("10.0.0.2", 1001, now=11)
        self.assertFalse(detector.flag("10.0.0.2", 1002, now=16))

    def test_destinations_are_tracked_independently(self):
        detector = PortScanDetector(window_s=5, threshold_ports=2)

        self.assertFalse(detector.flag("10.0.0.2", 1000, now=10))
        self.assertFalse(detector.flag("10.0.0.3", 1001, now=10))
        self.assertTrue(detector.flag("10.0.0.2", 1002, now=11))


if __name__ == "__main__":
    unittest.main()
