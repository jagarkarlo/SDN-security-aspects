# Setup and Run

This guide starts the Ryu OpenFlow controller, local dashboard, and three-host
Mininet topology on Ubuntu or Debian.

## Prerequisites

Use Python 3.10. Ryu 4.34 has legacy packaging and does not install on Python
3.12.

```bash
sudo apt update
sudo apt install -y \
  python3.10 python3.10-venv python3-pip \
  mininet openvswitch-switch hping3 curl jq

python3.10 --version
sudo mn --version
sudo ovs-vsctl --version
```

## Install the Controller

```bash
git clone https://github.com/jagarkarlo/SDN-security-aspects.git
cd SDN-security-aspects

python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Start the Lab

In the first terminal, start the controller and dashboard:

```bash
cd SDN-security-aspects
source venv/bin/activate
PYTHONPATH=. python run_controller.py
```

Open `http://127.0.0.1:8080/dashboard` or inspect the snapshot directly:

```bash
curl -s http://127.0.0.1:8080/api/dashboard | jq
```

In a second terminal, start the OpenFlow 1.3 topology:

```bash
cd SDN-security-aspects
sudo python3.10 src/mininet/topo_microseg.py
```

The Mininet topology always calls `net.stop()` when the CLI exits. If a prior
run left stale state behind, clean it with:

```bash
sudo mn -c
sudo ovs-vsctl show
```

## Verify the Switch

From the Mininet CLI:

```bash
sh ovs-vsctl get bridge s1 protocols
sh ovs-vsctl get-controller s1
```

Expected values include `OpenFlow13` and `tcp:127.0.0.1:6653`.
