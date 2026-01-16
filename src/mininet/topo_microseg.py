#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


def run():
    # Remote controller (Ryu on 127.0.0.1:6653)
    net = Mininet(controller=RemoteController, switch=OVSSwitch, autoSetMacs=True)

    net.addController("c0", ip="127.0.0.1", port=6653)

    s1 = net.addSwitch("s1", protocols="OpenFlow13")

    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    h3 = net.addHost("h3", ip="10.0.0.3/24")

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    net.start()

    print("\n[+] Topology started.")
    print("[+] Now in Mininet CLI you can run:")
    print("    pingall")
    print("    h1 hping3 -S -c 1 -p 22 10.0.0.2   (should be DROPPED by ACL)")
    print("    h1 hping3 -S -c 1 -p 80 10.0.0.2   (should be ALLOWED)")
    print("    h3 bash src/tests/ddos_simulation.sh 10.0.0.2\n")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
