#!/usr/bin/env bash
set -euo pipefail

echo "[+] Cleaning old Mininet state..."
sudo mn -c >/dev/null 2>&1 || true

echo "[+] Start topology in another terminal:"
echo "    sudo python3 src/mininet/topo_microseg.py"
echo ""
echo "[+] In Mininet CLI run:"
echo "    pingall"
echo "    h1 ping -c 5 h2"
echo "    h3 ping -c 5 h2"
echo ""
echo "[+] Optional flow table check:"
echo "    sh ovs-ofctl -O OpenFlow13 dump-flows s1"
