
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp
from ryu.lib import hub

class TrafficClassifier(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficClassifier, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stats = {
            'TCP':   {'count': 0, 'bytes': 0},
            'UDP':   {'count': 0, 'bytes': 0},
            'ICMP':  {'count': 0, 'bytes': 0},
            'OTHER': {'count': 0, 'bytes': 0},
        }
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        match    = parser.OFPMatch()
        actions  = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                           ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, 0, match, actions)
        self.logger.info("Switch %s connected", datapath.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg      = ev.msg
        datapath = msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        in_port  = msg.match['in_port']

        pkt     = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if eth_pkt is None:
            return

        dst  = eth_pkt.dst
        src  = eth_pkt.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)
        actions  = [parser.OFPActionOutput(out_port)]

        protocol = self._classify(pkt)
        pkt_len  = len(msg.data)
        self.stats[protocol]['count'] += 1
        self.stats[protocol]['bytes'] += pkt_len
        self.logger.info("[CLASSIFIED: %s] src=%s dst=%s in_port=%s len=%d",
                         protocol, src, dst, in_port, pkt_len)

        if out_port != ofproto.OFPP_FLOOD:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            if ip_pkt:
                match = self._build_match(parser, in_port, ip_pkt, pkt, protocol)
                if match:
                    self._add_flow(datapath, 10, match, actions, idle_timeout=30)

        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        out  = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def _classify(self, pkt):
        if pkt.get_protocol(tcp.tcp):   return 'TCP'
        if pkt.get_protocol(udp.udp):   return 'UDP'
        if pkt.get_protocol(icmp.icmp): return 'ICMP'
        return 'OTHER'

    def _build_match(self, parser, in_port, ip_pkt, pkt, protocol):
        base = dict(in_port=in_port, eth_type=0x0800,
                    ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
        if protocol == 'TCP':
            t = pkt.get_protocol(tcp.tcp)
            return parser.OFPMatch(**base, ip_proto=6,
                                   tcp_src=t.src_port, tcp_dst=t.dst_port)
        elif protocol == 'UDP':
            u = pkt.get_protocol(udp.udp)
            return parser.OFPMatch(**base, ip_proto=17,
                                   udp_src=u.src_port, udp_dst=u.dst_port)
        elif protocol == 'ICMP':
            return parser.OFPMatch(**base, ip_proto=1)
        return None

    def _add_flow(self, datapath, priority, match, actions,
                  idle_timeout=0, hard_timeout=0):
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser
        inst    = [parser.OFPInstructionActions(
                       ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match,
            instructions=inst, idle_timeout=idle_timeout,
            hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    def _monitor(self):
        while True:
            hub.sleep(10)
            total = sum(v['count'] for v in self.stats.values()) or 1
            print("\n========= Traffic Classification Report =========")
            print(f"{'Protocol':<10} {'Packets':>10} {'Bytes':>12} {'Share':>8}")
            print("-" * 45)
            for proto, data in self.stats.items():
                pct = data['count'] / total * 100
                print(f"{proto:<10} {data['count']:>10} {data['bytes']:>12} {pct:>7.1f}%")
            print("=================================================\n")

