#!/usr/bin/env python3
# Ryu app: L2 switching + ACL + basic new-flow rate limiting (DoS mitigation)
#
# Run (recommended via your wrapper):
#   export EVENTLET_NO_GREENDNS=yes
#   PYTHONPATH=. python run_controller.py src.controller.sdn_security_app

import eventlet
eventlet.monkey_patch()

import time
from collections import defaultdict, deque

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, ipv4, tcp, udp
from ryu.lib import hub


class SdnSecurityApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # --- Security policy (example) ---
    # (src_ip, dst_ip, proto, dst_port) -> allow?
    # proto: "tcp" | "udp"
    ACL_ALLOW = {
        ("10.0.0.1", "10.0.0.2", "tcp", 80): True,    # h1 -> h2 HTTP
        ("10.0.0.1", "10.0.0.2", "tcp", 443): True,   # h1 -> h2 HTTPS
        ("10.0.0.2", "10.0.0.1", "tcp", 80): True,    # h2 -> h1 HTTP (optional)
        ("10.0.0.2", "10.0.0.1", "tcp", 443): True,   # h2 -> h1 HTTPS (optional)
    }

    # default: deny for inter-host TCP/UDP unless explicitly allowed
    DEFAULT_DENY_L4 = True

    # --- Rate limiting / mitigation ---
    WINDOW_SEC = 2.0
    NEWFLOWS_THRESHOLD = 60          # new flows per WINDOW_SEC per src_ip
    BLOCK_DURATION_SEC = 15          # how long to block attacker

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mac_to_port = defaultdict(dict)          # dpid -> {mac: port}
        self.newflows = defaultdict(lambda: deque())  # src_ip -> timestamps of new flows
        self.blocked_until = {}                       # src_ip -> epoch until blocked

        self._cleanup_thread = hub.spawn(self._cleanup_loop)

    # -------------------------
    # Housekeeping
    # -------------------------
    def _cleanup_loop(self):
        while True:
            now = time.time()
            expired = [ip for ip, until in self.blocked_until.items() if until <= now]
            for ip in expired:
                del self.blocked_until[ip]
                self.logger.info("UNBLOCK: %s", ip)
            hub.sleep(1)

    def _is_blocked(self, src_ip: str) -> bool:
        until = self.blocked_until.get(src_ip)
        return until is not None and until > time.time()

    def _record_newflow_and_maybe_block(self, src_ip: str):
        now = time.time()
        q = self.newflows[src_ip]
        q.append(now)

        while q and (now - q[0]) > self.WINDOW_SEC:
            q.popleft()

        if len(q) > self.NEWFLOWS_THRESHOLD and not self._is_blocked(src_ip):
            self.blocked_until[src_ip] = now + self.BLOCK_DURATION_SEC
            self.logger.warning("BLOCK: %s (new-flows=%d/%ss)", src_ip, len(q), self.WINDOW_SEC)

    # -------------------------
    # OpenFlow helpers
    # -------------------------
    def add_flow(self, datapath, priority, match, actions, idle_timeout=30, hard_timeout=0):
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
        )
        datapath.send_msg(mod)

    # -------------------------
    # ACL logic
    # -------------------------
    def _acl_allows(self, src_ip, dst_ip, proto, dst_port) -> bool:
        if proto in ("tcp", "udp"):
            if self.ACL_ALLOW.get((src_ip, dst_ip, proto, dst_port), False):
                return True
            if self.DEFAULT_DENY_L4 and src_ip != dst_ip:
                return False
        return True

    # -------------------------
    # Switch connect
    # -------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser

        # Table-miss: send to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, priority=0, match=match, actions=actions, idle_timeout=0)

        self.logger.info("Switch connected: dpid=%s", datapath.id)

    # -------------------------
    # Packet processing
    # -------------------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None:
            return

        dst = eth.dst
        src = eth.src

        # Learn MAC -> port
        self.mac_to_port[dpid][src] = in_port

        out_port = self.mac_to_port[dpid].get(dst, ofp.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        # -------------------------
        # ARP: allow + install ARP-only L2 flow
        # -------------------------
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            if out_port != ofp.OFPP_FLOOD:
                match = parser.OFPMatch(
                    in_port=in_port,
                    eth_src=src,
                    eth_dst=dst,
                    eth_type=0x0806,  # ARP only
                )
                self.add_flow(datapath, priority=10, match=match, actions=actions, idle_timeout=60)

            # PacketOut
            data = None if msg.buffer_id != ofp.OFP_NO_BUFFER else msg.data
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=data,
            )
            datapath.send_msg(out)
            return

        # -------------------------
        # IPv4: apply ACL + DoS mitigation
        # NOTE: we DO NOT install a generic L2 flow for IPv4,
        # because that would bypass ACL after first learning.
        # -------------------------
        ip = pkt.get_protocol(ipv4.ipv4)
        if ip:
            src_ip = ip.src
            dst_ip = ip.dst

            # If blocked: install DROP for this src_ip (any IPv4)
            if self._is_blocked(src_ip):
                drop_match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip)
                self.add_flow(datapath, priority=200, match=drop_match, actions=[], idle_timeout=5)
                return

            # Identify L4
            t = pkt.get_protocol(tcp.tcp)
            u = pkt.get_protocol(udp.udp)

            proto = None
            dport = None
            ip_proto_num = None

            if t:
                proto = "tcp"
                dport = t.dst_port
                ip_proto_num = 6
            elif u:
                proto = "udp"
                dport = u.dst_port
                ip_proto_num = 17

            # If TCP/UDP: enforce ACL
            if proto and dport is not None:
                # Treat each TCP/UDP packet as new-flow signal (simple heuristic)
                self._record_newflow_and_maybe_block(src_ip)

                if not self._acl_allows(src_ip, dst_ip, proto, dport):
                    # Install DROP flow for this L4 tuple
                    kwargs = dict(
                        eth_type=0x0800,
                        ipv4_src=src_ip,
                        ipv4_dst=dst_ip,
                        ip_proto=ip_proto_num,
                    )
                    if proto == "tcp":
                        kwargs["tcp_dst"] = dport
                    else:
                        kwargs["udp_dst"] = dport

                    drop_match = parser.OFPMatch(**kwargs)
                    self.add_flow(datapath, priority=150, match=drop_match, actions=[], idle_timeout=20)
                    self.logger.info("ACL DROP: %s -> %s %s/%s", src_ip, dst_ip, proto, dport)
                    return

                # ALLOW: install allow flow for this L4 tuple (so it becomes fast-path)
                if out_port != ofp.OFPP_FLOOD:
                    kwargs = dict(
                        in_port=in_port,
                        eth_type=0x0800,
                        ipv4_src=src_ip,
                        ipv4_dst=dst_ip,
                        ip_proto=ip_proto_num,
                    )
                    if proto == "tcp":
                        kwargs["tcp_dst"] = dport
                    else:
                        kwargs["udp_dst"] = dport

                    allow_match = parser.OFPMatch(**kwargs)
                    self.add_flow(datapath, priority=120, match=allow_match, actions=actions, idle_timeout=60)

            else:
                # Non-TCP/UDP IPv4 (e.g., ICMP): allow and optionally install an ICMP/IPv4 flow
                if out_port != ofp.OFPP_FLOOD:
                    allow_match = parser.OFPMatch(
                        in_port=in_port,
                        eth_type=0x0800,
                        ipv4_src=src_ip,
                        ipv4_dst=dst_ip,
                    )
                    self.add_flow(datapath, priority=50, match=allow_match, actions=actions, idle_timeout=30)

        # -------------------------
        # Default: PacketOut
        # -------------------------
        data = None if msg.buffer_id != ofp.OFP_NO_BUFFER else msg.data
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)
