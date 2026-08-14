from __future__ import annotations

from typing import Dict, Optional


IPV4_ETH_TYPE = 0x0800
TCP_PROTOCOL = 6
UDP_PROTOCOL = 17


def forwarding_match_fields(
    src_ip: str, dst_ip: str, protocol: int, dst_port: Optional[int]
) -> Dict[str, object]:
    fields: Dict[str, object] = {
        "eth_type": IPV4_ETH_TYPE,
        "ipv4_src": src_ip,
        "ipv4_dst": dst_ip,
    }
    if protocol == TCP_PROTOCOL and dst_port is not None:
        fields.update(ip_proto=protocol, tcp_dst=dst_port)
    elif protocol == UDP_PROTOCOL and dst_port is not None:
        fields.update(ip_proto=protocol, udp_dst=dst_port)
    return fields
