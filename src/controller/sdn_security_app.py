import eventlet
eventlet.monkey_patch()

from collections import defaultdict, deque
from typing import Deque, Dict, Tuple, Set

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp
from ryu.app.wsgi import WSGIApplication

from src.web.store import DashboardStore
from src.web.dashboard_wsgi import DashboardWSGI


class SdnSecurityApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {"wsgi": WSGIApplication}  # ensures kwargs["wsgi"] exists

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.store = DashboardStore(max_points=120, max_events=60)

        # register WSGI controller
        wsgi = kwargs["wsgi"]
        wsgi.register(DashboardWSGI, {"store": self.store})

        # L2 learning
        self.mac_to_port: Dict[int, Dict[str, int]] = defaultdict(dict)

        # ACL rules (example): block SSH h1->h2
        # tuple: (src_ip, dst_ip, proto, dst_port)
        self.acl_block: Set[Tuple[str, str, int, int]] = {
            ("10.0.0.1", "10.0.0.2", 6, 22)
        }

        # DDoS heuristic:
        self.ddos_window_s = 5.0
        self.ddos_threshold_ports = 40
        self._dst_ports: Dict[str, Deque[Tuple[float, int]]] = defaultdict(lambda: deque(maxlen=600))

        # tick loop: updated_at always moves
        hub.spawn(self._tick_loop)

        self.logger.info("UI:  http://127.0.0.1:8080/dashboard")
        self.logger.info("API: http://127.0.0.1:8080/api/dashboard")

    def _tick_loop(self):
        while True:
            hub.sleep(1)
            self.store.tick_1s()

    def ddos_flag(self, dst_ip: str, dst_port: int) -> bool:
        now = hub.get_time()
        dq = self._dst_ports[dst_ip]
        dq.append((now, dst_port))

        while dq and (now - dq[0][0]) > self.ddos_window_s:
            dq.popleft()

        uniq_ports = len({p for _, p in dq})
        return uniq_ports >= self.ddos_threshold_ports

    def add_flow(self, dp, priority, match, actions, idle_timeout=30):
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout
        )
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # table-miss -> controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions, idle_timeout=0)

        self.store.log("INFO", "Switch connected", dpid=dp.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if not eth:
            return

        dpid = dp.id
        src_mac = eth.src
        dst_mac = eth.dst

        # learn
        self.mac_to_port[dpid][src_mac] = in_port

        ip = pkt.get_protocol(ipv4.ipv4)
        if ip is None:
            # L2 / ARP etc. -> simple L2 forward
            out_port = self.mac_to_port[dpid].get(dst_mac, ofp.OFPP_FLOOD)
            actions = [parser.OFPActionOutput(out_port)]
            dp.send_msg(parser.OFPPacketOut(
                datapath=dp,
                buffer_id=ofp.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data
            ))
            return

        src_ip = ip.src
        dst_ip = ip.dst
        proto = ip.proto

        dst_port = None
        if proto == 6:
            t = pkt.get_protocol(tcp.tcp)
            dst_port = t.dst_port if t else None
        elif proto == 17:
            u = pkt.get_protocol(udp.udp)
            dst_port = u.dst_port if u else None

        self.store.inc_flow()

        # ACL DROP
        if dst_port is not None and (src_ip, dst_ip, proto, dst_port) in self.acl_block:
            match = parser.OFPMatch(
                eth_type=0x0800,
                ip_proto=6,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip,
                tcp_dst=dst_port
            )
            self.add_flow(dp, 150, match, [], idle_timeout=20)
            self.store.inc_acl_drop()
            self.store.log("WARN", "ACL DROP", src=src_ip, dst=dst_ip, proto=proto, dst_port=dst_port)
            return

        # DDoS flag (heuristic only - doesn't block traffic here, just flags)
        if dst_port is not None and proto in (6, 17) and self.ddos_flag(dst_ip, dst_port):
            self.store.inc_ddos_flag()
            self.store.log("WARN", "DDoS flagged", dst=dst_ip)

        # normal forwarding
        out_port = self.mac_to_port[dpid].get(dst_mac, ofp.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]
        self.store.inc_allowed()

        # install a simple IP forward flow to reduce controller load
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip, ipv4_dst=dst_ip)
        self.add_flow(dp, 50, match, actions, idle_timeout=30)

        dp.send_msg(parser.OFPPacketOut(
            datapath=dp,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data
        ))
