# Validation Guide

Run the following manual integration checks after starting the controller and
Mininet topology as described in [setup.md](setup.md).

## Connectivity

```bash
mininet> pingall
```

All three hosts should reach one another. The dashboard flow counter should
increase as IPv4 packets reach the controller.

## ACL Enforcement

```bash
mininet> h1 hping3 -S -c 3 -p 22 10.0.0.2
```

Traffic from `10.0.0.1` to TCP port `22` on `10.0.0.2` should be dropped. The
controller records an `ACL DROP` event and installs a priority-150 drop flow.

## Allowed HTTP Traffic

```bash
mininet> h2 python3 -m http.server 80 &
mininet> h1 wget -O - -T 3 http://10.0.0.2 | head
```

The request should succeed and increase the allowed-traffic counter.

## Port-Scan Heuristic

```bash
mininet> h3 bash src/tests/ddos_simulation.sh 10.0.0.2
```

The detector flags 40 distinct TCP or UDP destination ports for one target
within five seconds. It records one DDoS warning per target until that target's
window clears; it does not install a blocking flow. Stop the generator with
`Ctrl+C`.

## Inspect OpenFlow Rules

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

Look for the table-miss flow, priority-50 forwarding flows, and any
priority-150 ACL drop flow. TCP and UDP forwarding flows include the
destination port so distinct probes continue to reach the controller.

## Automated Checks

The repository also provides dependency-free checks that do not need root,
Mininet, Open vSwitch, or Ryu installed:

```bash
python -m compileall -q run_controller.py src
python -m unittest discover -s test -v
bash -n src/tests/*.sh
```

They cover the dashboard store, port-scan threshold/window/cooldown behavior,
and forwarding-match rules. The Mininet checks above remain manual integration
tests because they require privileged networking.
