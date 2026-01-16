
<a name="top"></a>
# SDN Security Aspects - Ryu Controller - Mininet

A practical implementation of security mechanisms in **Software-Defined Networking (SDN)** using **Ryu OpenFlow Controller** and **Mininet** network emulation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Ryu](https://img.shields.io/badge/Ryu-SDN_Framework-green.svg)
![OpenFlow](https://img.shields.io/badge/OpenFlow-1.3-orange.svg)
![Mininet](https://img.shields.io/badge/Mininet-2.3+-red.svg)

---

## ✨ Značajke

### 🔒 Access Control List (ACL)
- **Centralizirano provođenje sigurnosnih politika** na razini kontrolera
- Layer-4 filtriranje (IP, protokol, port)
- Dinamička instalacija DROP pravila za nedopušteni promet
- Whitelist pristup (eksplicitno dopušteni tokovi)

### 🛡️ DoS Zaštita
- **Real-time detekcija napada** na temelju broja novih flowova
- Sliding window algoritam za praćenje aktivnosti
- Automatska privremena blokada napadača
- Konfigurirajući pragovi i trajanje blokade
- Automatsko deblokiranje nakon isteka vremena

### 🔄 L2 Learning Switch
- Automatsko učenje MAC → port mapiranja
- Dinamička instalacija forwarding pravila
- Flood za nepoznate destinacije
- Table-miss pravilo za rukovanje novim tokovima

### 📊 OpenFlow Upravljanje
- Hierarchija prioriteta pravila (0-200)
- Provjera i analiza instaliranih flowova
- Automatsko čišćenje isteklih pravila

---

## 🛠️ Tech Stack

### SDN Controller
- **Python 3.8+** - Programski jezik
- **Ryu Framework** - SDN kontroler framework
- **OpenFlow 1.3** - Protokol za upravljanje switchevima

### Network Emulation
- **Mininet 2.3+** - Emulacija mreže
- **Open vSwitch** - Virtualni OpenFlow switch

### Testing Tools
- **hping3** - Generiranje TCP/UDP prometa
- **curl** - HTTP testiranje
- **ping** - ICMP testiranje

---

## 📦 Preduvjeti

Provjerite da imate instalirano:

| Alat | Verzija | Komanda za provjeru |
|------|---------|---------------------|
| **Python** | 3.8+ | `python3 --version` |
| **pip** | 20.0+ | `pip3 --version` |
| **Mininet** | 2.3+ | `mn --version` |
| **Open vSwitch** | 2.x | `ovs-vsctl --version` |

### Instalacija osnovnih alata
```bash
# Ažuriranje sustava
sudo apt update && sudo apt upgrade -y

# Instalacija potrebnih paketa
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    mininet \
    openvswitch-switch \
    hping3 \
    curl \
    net-tools
```

---

## 🚀 Instalacija

### 1️⃣ Kloniranje projekta
```bash
git clone https://github.com/jagarkarlo/SDN-security-aspects.git
cd SDN-security-aspects
```

### 2️⃣ Postavljanje Python okruženja
```bash
# Kreiranje virtualnog okruženja
python3 -m venv venv

# Aktivacija virtualnog okruženja
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalacija dependencies
pip install --upgrade pip
pip install ryu eventlet
```

### 3️⃣ Verifikacija instalacije
```bash
# Provjera Ryu instalacije
ryu --version

# Provjera Mininet instalacije
sudo mn --version

# Provjera OVS instalacije
sudo ovs-vsctl --version
```

---

## ▶️ Pokretanje aplikacije

### Pokretanje SDN kontrolera
```bash
# Iz root direktorija projekta (s aktiviranim venv)
cd SDN-security-aspects
source venv/bin/activate

# Postavljanje environment varijable
export EVENTLET_NO_GREENDNS=yes

# Pokretanje Ryu kontrolera
PYTHONPATH=. python run_controller.py src.controller.sdn_security_app
```

**Kontroler će biti dostupan na:** `tcp://127.0.0.1:6653`

**Očekivani output:**
```
loading app src.controller.sdn_security_app
loading app ryu.controller.ofp_handler
instantiating app src.controller.sdn_security_app of SDNSecurityApp
creating context wsgi
creating context ofp_handler
```

### Pokretanje Mininet topologije
```bash
# U novom terminalu
cd SDN-security-aspects
sudo python3 src/mininet/topo_microseg.py
```

**Mininet CLI će se otvoriti:**
```
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3
*** Adding switches:
s1
*** Adding links:
(h1, s1) (h2, s1) (h3, s1)
*** Configuring hosts
h1 h2 h3
*** Starting controller
c0
*** Starting 1 switches
s1 ...
*** Starting CLI:
mininet>
```

---

## 🌐 Topologija

```
        ┌──────────────────┐
        │  Ryu Controller  │
        │  127.0.0.1:6653  │
        └────────┬─────────┘
                 │
                 │ OpenFlow 1.3
                 │
        ┌────────▼─────────┐
        │       s1         │
        │  (OVS Switch)    │
        └───┬────┬────┬────┘
            │    │    │
    ┌───────▼┐ ┌─▼──────┐ ┌─▼──────┐
    │   h1   │ │   h2   │ │   h3   │
    │10.0.0.1│ │10.0.0.2│ │10.0.0.3│
    └────────┘ └────────┘ └────────┘
```

**Konfiguracija:**
- **Switch:** OpenFlow 1.3, datapath_id=0000000000000001
- **Kontroler:** Remote (TCP 127.0.0.1:6653)
- **Hostovi:** 10.0.0.0/24 subnet

---

## 🧪 Testiranje

### Test 1️⃣: Osnovna povezivost
```bash
mininet> pingall
```

**Očekivani rezultat:**
```
*** Ping: testing ping reachability
h1 -> h2 h3
h2 -> h1 h3
h3 -> h1 h2
*** Results: 0% dropped (6/6 received)
```

---

### Test 2️⃣: ACL - Blokirani promet (SSH na port 22)
```bash
mininet> h1 hping3 -S -c 3 -p 22 10.0.0.2
```

**Očekivani rezultat:**
```
HPING 10.0.0.2 (h1-eth0 10.0.0.2): S set, 40 headers + 0 data bytes

--- 10.0.0.2 hping statistic ---
3 packets transmitted, 0 packets received, 100% packet loss
```

**Provjera instaliranog DROP pravila:**
```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1 | grep "tp_dst=22"
```

**Output:**
```
priority=150,tcp,nw_src=10.0.0.1,nw_dst=10.0.0.2,tp_dst=22 actions=drop
```

---

### Test 3️⃣: ACL - Dopušteni promet (HTTP na port 80)
```bash
# Pokretanje HTTP servera na h2
mininet> h2 python3 -m http.server 80 &

# Testiranje s h1
mininet> h1 curl http://10.0.0.2
```

**Očekivani rezultat:**
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"...>
<html>
<head>
<title>Directory listing for /</title>
</head>
...
```

**Provjera ALLOW pravila:**
```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1 | grep "tp_dst=80"
```

---

### Test 4️⃣: DoS simulacija
```bash
mininet> h3 bash src/tests/ddos_simulation.sh 10.0.0.2
```

**Script generira:**
- 50 paralelnih TCP SYN paketa
- Random portovi 8000-9000
- Brzo slanje za prekoračenje praga

**Očekivani output u kontroler logu:**
```
[DoS Detection] Source 10.0.0.3 exceeded flow rate threshold (15 flows in 2.0s)
[DoS Mitigation] Blocking 10.0.0.3 for 30 seconds
```

**Testiranje blokade:**
```bash
mininet> h3 ping -c 3 10.0.0.2
```

**Rezultat:**
```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss
```

**Provjera blokade:**
```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1 | grep "10.0.0.3"
```

**Output:**
```
priority=200,ip,nw_src=10.0.0.3 actions=drop
```

**Automatsko deblokiranje:**
- Nakon 30 sekundi blokada se automatski uklanja
- Host može ponovno slati promet

---

### Test 5️⃣: Analiza OpenFlow pravila

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Tipični output:**
```
cookie=0x0, duration=45.123s, table=0, n_packets=0, n_bytes=0, 
  priority=0 actions=CONTROLLER:65535

cookie=0x0, duration=30.456s, table=0, n_packets=12, n_bytes=1176, 
  priority=100,ip,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02 
  actions=output:2

cookie=0x0, duration=15.789s, table=0, n_packets=0, n_bytes=0, 
  priority=150,tcp,nw_src=10.0.0.1,nw_dst=10.0.0.2,tp_dst=22 
  actions=drop

cookie=0x0, duration=5.012s, table=0, n_packets=0, n_bytes=0, 
  priority=200,ip,nw_src=10.0.0.3 
  actions=drop
```

**Hierarchija prioriteta:**
| Prioritet | Tip pravila | Svrha |
|-----------|-------------|-------|
| 200 | DoS blokada | Privremena blokada napadača |
| 150 | ACL DROP | Blokirani TCP/UDP portovi |
| 100 | L2 Forward | MAC → port forwarding |
| 0 | Table-miss | Šalje nepoznati promet kontroleru |

---

## 📊 Pregled testnih scenarija

| Test | Protokol/Port | Očekivani rezultat | Status |
|------|---------------|-------------------|--------|
| Ping svi hostovi | ICMP | 100% uspješnost | ✅ |
| SSH h1→h2 | TCP/22 | 100% packet loss (DROP) | ✅ |
| HTTP h1→h2 | TCP/80 | Uspješna konekcija | ✅ |
| HTTPS h1→h2 | TCP/443 | Uspješna konekcija | ✅ |
| DoS napad h3→h2 | TCP/random | Detekcija + blokada | ✅ |
| Deblokiranje | - | Automatski nakon 30s | ✅ |

---

## 🧠 Implementacijski detalji

### ACL konfiguracija

**Datoteka:** `src/controller/sdn_security_app.py`

```python
ACL_ALLOW = {
    # Format: (src_ip, dst_ip, protocol, port): True
    ("10.0.0.1", "10.0.0.2", "tcp", 80): True,    # HTTP dopušten
    ("10.0.0.1", "10.0.0.2", "tcp", 443): True,   # HTTPS dopušten
    ("10.0.0.2", "10.0.0.1", "tcp", 80): True,    # Bidirekcijski
    ("10.0.0.2", "10.0.0.1", "tcp", 443): True,
}
```

**Logika:**
1. Novi TCP/UDP paket stiže na kontroler
2. Provjera tuple (src, dst, proto, port) u ACL_ALLOW
3. Ako je u listi → instalira se forward flow (priority 100)
4. Ako nije → instalira se DROP flow (priority 150)

---

### DoS parametri

```python
# Konfiguracija u kontroleru
FLOW_RATE_THRESHOLD = 10       # Max novih flowova
FLOW_RATE_WINDOW = 2.0         # Vremenski prozor (sekunde)
BLOCK_DURATION = 30            # Trajanje blokade (sekunde)
```

**Algoritam:**
1. Prati timestamp prvog paketa svakog novog toka
2. Broji tokove po src_ip u sliding window-u
3. Ako broj_flowova > threshold → blokada
4. Instalira DROP pravilo s prioritetom 200
5. Nakon BLOCK_DURATION → automatski uklanja pravilo

---

### OpenFlow pravila

**Table-miss (priority 0):**
```python
match = parser.OFPMatch()
actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                  ofproto.OFPCML_NO_BUFFER)]
self.add_flow(datapath, 0, match, actions)
```

**L2 Forwarding (priority 100):**
```python
match = parser.OFPMatch(
    in_port=in_port,
    eth_dst=dst_mac
)
actions = [parser.OFPActionOutput(out_port)]
self.add_flow(datapath, 100, match, actions)
```

**ACL DROP (priority 150):**
```python
match = parser.OFPMatch(
    eth_type=0x0800,
    ip_proto=6,  # TCP
    ipv4_src=src_ip,
    ipv4_dst=dst_ip,
    tcp_dst=port
)
actions = []  # Empty = DROP
self.add_flow(datapath, 150, match, actions)
```

**DoS Block (priority 200):**
```python
match = parser.OFPMatch(
    eth_type=0x0800,
    ipv4_src=blocked_ip
)
actions = []  # DROP
self.add_flow(datapath, 200, match, actions, hard_timeout=30)
```

---

## 🔧 Konfiguracija

### Promjena ACL pravila

**Uredite:** `src/controller/sdn_security_app.py`

```python
# Dodajte nova pravila u ACL_ALLOW dictionary
ACL_ALLOW = {
    # Postojeća pravila...
    ("10.0.0.1", "10.0.0.3", "tcp", 8080): True,  # Custom port
    ("10.0.0.3", "10.0.0.1", "udp", 53): True,    # DNS
}
```

**Restartajte kontroler:**
```bash
# Ctrl+C za zaustavljanje
# Ponovno pokrenite:
PYTHONPATH=. python run_controller.py src.controller.sdn_security_app
```

---

### Prilagodba DoS parametara

```python
# Strože postavke (osjetljivije na napade)
FLOW_RATE_THRESHOLD = 5
FLOW_RATE_WINDOW = 1.0
BLOCK_DURATION = 60

# Blaže postavke (tolerantnije)
FLOW_RATE_THRESHOLD = 20
FLOW_RATE_WINDOW = 5.0
BLOCK_DURATION = 15
```

---

## 🐛 Troubleshooting

### Problem: Kontroler se ne može povezati

**Simptomi:**
```
Connection refused at tcp://127.0.0.1:6653
```

**Rješenje:**
```bash
# Provjera je li kontroler pokrenut
ps aux | grep ryu

# Provjera porta
sudo netstat -tuln | grep 6653

# Provjerite firewall
sudo ufw status
sudo ufw allow 6653/tcp
```

---

### Problem: Mininet ne može kreirati topologiju

**Simptomi:**
```
*** Error setting resource limits
*** Creating network
Exception: Please shut down the controller
```

**Rješenje:**
```bash
# Očistite stare Mininet procese
sudo mn -c

# Provjerite OVS
sudo ovs-vsctl show
sudo service openvswitch-switch restart

# Provjerite nema starih kontrolera
ps aux | grep ryu
kill -9 <PID>
```

---

### Problem: Flowovi se ne instaliraju

**Dijagnostika:**
```bash
# Provjera OpenFlow verzije
mininet> sh ovs-vsctl get bridge s1 protocols

# Mora biti: ["OpenFlow13"]
# Ako je prazno, postavite:
mininet> sh ovs-vsctl set bridge s1 protocols=OpenFlow13

# Provjera konekcije s kontrolerom
mininet> sh ovs-vsctl get-controller s1
# Output: tcp:127.0.0.1:6653

# Provjera je li povezan
mininet> sh ovs-vsctl show
# Tražite "is_connected: true"
```

---

### Problem: hping3 ne radi

**Simptomi:**
```bash
mininet> h1 hping3 -S -p 80 10.0.0.2
bash: hping3: command not found
```

**Rješenje:**
```bash
# Izađite iz Minineta
mininet> exit

# Instalirajte hping3
sudo apt install hping3

# Ponovno pokrenite Mininet
sudo python3 src/mininet/topo_microseg.py
```

---

### Česte greške

| Greška | Uzrok | Rješenje |
|--------|-------|----------|
| `RTNETLINK answers: File exists` | Mininet nije pravilno očišćen | `sudo mn -c` |
| `Cannot connect to controller` | Kontroler nije pokrenut | Pokrenite Ryu kontroler prvo |
| `Protocol not supported` | OVS ne podržava OpenFlow 1.3 | `sudo ovs-vsctl set bridge s1 protocols=OpenFlow13` |
| `Address already in use` | Port 6653 zauzet | `sudo lsof -ti:6653 \| xargs kill -9` |
| Flowovi se brišu | Timeout postavljen | Uklonite `hard_timeout` i `idle_timeout` |

---

## 📝 Struktura projekta

```
SDN-security-aspects/
│
├── src/
│   ├── controller/
│   │   ├── __init__.py
│   │   └── sdn_security_app.py      # Glavni SDN kontroler
│   │       ├── SDNSecurityApp       # Glavna klasa
│   │       ├── switch_features_handler()
│   │       ├── packet_in_handler()
│   │       ├── check_acl()          # ACL provjera
│   │       ├── check_flow_rate()    # DoS detekcija
│   │       └── add_flow()           # OpenFlow flow instalacija
│   │
│   ├── mininet/
│   │   └── topo_microseg.py          # Mininet topologija
│   │       ├── MicroSegTopo         # Custom topologija klasa
│   │       └── run_topology()       # Pokretanje
│   │
│   └── tests/
│       ├── run_ping.sh               # Osnovni ping testovi
│       └── ddos_simulation.sh        # DoS napad simulacija
│
├── run_controller.py                 # Ryu launcher script
├── .gitignore
└── README.md
```

---

## 📚 Dokumentacija i reference

### Korištene tehnologije
- [Ryu SDN Framework](https://ryu.readthedocs.io/)
- [OpenFlow 1.3 Specification](https://www.opennetworking.org/software-defined-standards/specifications/)
- [Mininet Documentation](http://mininet.org/)
- [Open vSwitch Manual](https://www.openvswitch.org/)

### Preporučena literatura
- "Software Defined Networks: A Comprehensive Approach" - Paul Goransson
- "SDN: Software Defined Networks" - Thomas D. Nadeau

### Korisni resursi
- [Ryu Book](https://osrg.github.io/ryu-book/en/html/)
- [OpenFlow Tutorial](https://github.com/mininet)
- [Mininet Walkthrough](http://mininet.org/walkthrough/)
  
---

## 📞 Kontakt i podrška

**Imate pitanja ili probleme?**

- 🐛 [Prijavite bug](https://github.com/jagarkarlo/SDN-security-aspects/issues)
- 💡 [Predložite feature](https://github.com/jagarkarlo/SDN-security-aspects/issues/new?labels=enhancement)

---

<div align="center">

[⬆ Povratak na vrh](#top)

</div>
