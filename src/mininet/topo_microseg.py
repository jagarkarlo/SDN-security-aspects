# src/mininet/topo_microseg.py

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def start() -> None:
    net = Mininet(controller=None, switch=OVSSwitch, build=False, autoSetMacs=True)

    info("*** Configuring hosts\n")
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    h3 = net.addHost("h3", ip="10.0.0.3/24")

    info("*** Starting controller\n")
    c0 = net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)

    info("*** Starting 1 switches\n")
    s1 = net.addSwitch("s1", protocols="OpenFlow13")

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    net.build()
    c0.start()
    s1.start([c0])

    info("\n[+] Topology started.\n")
    info("[+] Now in Mininet CLI you can run:\n")
    info("    pingall\n")
    info("    h1 hping3 -S -c 3 -p 22 10.0.0.2   (should be DROPPED by ACL)\n")
    info("    h2 python3 -m http.server 80 &\n")
    info("    h1 wget -O - -T 3 http://10.0.0.2 | head\n")
    info("    h3 bash src/tests/ddos_simulation.sh 10.0.0.2\n\n")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    start()
