import unittest

from src.controller.flow_rules import forwarding_match_fields


class ForwardingMatchFieldsTest(unittest.TestCase):
    def test_tcp_flow_keeps_the_destination_port_specific(self):
        fields = forwarding_match_fields("10.0.0.1", "10.0.0.2", 6, 443)

        self.assertEqual(fields["eth_type"], 0x0800)
        self.assertEqual(fields["ip_proto"], 6)
        self.assertEqual(fields["tcp_dst"], 443)
        self.assertNotIn("udp_dst", fields)

    def test_udp_flow_keeps_the_destination_port_specific(self):
        fields = forwarding_match_fields("10.0.0.1", "10.0.0.2", 17, 53)

        self.assertEqual(fields["ip_proto"], 17)
        self.assertEqual(fields["udp_dst"], 53)
        self.assertNotIn("tcp_dst", fields)

    def test_non_transport_flow_uses_only_ip_fields(self):
        fields = forwarding_match_fields("10.0.0.1", "10.0.0.2", 1, None)

        self.assertEqual(fields, {
            "eth_type": 0x0800,
            "ipv4_src": "10.0.0.1",
            "ipv4_dst": "10.0.0.2",
        })


if __name__ == "__main__":
    unittest.main()
