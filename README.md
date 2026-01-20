<a name="top"></a>
# SDN Security Aspects - Ryu Controller + Real-Time Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Ryu](https://img.shields.io/badge/Ryu-SDN_Framework-green.svg)](https://ryu-sdn.org/)
[![OpenFlow](https://img.shields.io/badge/OpenFlow-1.3-orange.svg)](https://www.opennetworking.org/)
[![Mininet](https://img.shields.io/badge/Mininet-2.3+-red.svg)](http://mininet.org/)

Praktična implementacija sigurnosnih mehanizama u **Software-Defined Networking (SDN)** okruženju koristeći **Ryu OpenFlow kontroler**, **Mininet emulaciju mreže** i **integrirani web dashboard** za vizualizaciju sigurnosnih događaja u stvarnom vremenu.

---

## 📋 Sadržaj

- [Ključne Značajke](#-ključne-značajke)
- [Arhitektura](#-arhitektura)
- [Instalacija](#-instalacija)
- [Pokretanje](#-pokretanje)
- [Testiranje](#-testiranje)
- [Struktura Projekta](#-struktura-projekta)
- [Tehnologije](#-tehnologije)

---

## 🎯 Ključne Značajke

### 🛡️ Sigurnosni Mehanizmi

- **Access Control List (ACL)**
  - Layer-4 filtriranje (IP, protokol, port)
  - Dinamička instalacija DROP pravila
  - Real-time blocking nedozvoljenog prometa

- **DDoS Detekcija**
  - Heuristička detekcija bazirana na port scanning ponašanju
  - Sliding window algoritam (5s prozor, 40 portova prag)
  - Real-time flagging sumnjivog prometa

- **L2 Learning Switch**
  - Automatsko MAC learning
  - Dinamička instalacija forwarding pravila

### 📊 Real-Time Dashboard

- **Live Grafovi** (Canvas API, auto-refresh svaku sekundu)
  - flows/sec, acl drops/sec, ddos flags/sec, allowed/sec
- **KPI Kartice** - Ukupan broj događaja, ACL drops, DDoS flags, Allowed paketi
- **Event Log** - Kronološki prikaz svih događaja (INFO/WARN/ERROR)
- **REST API** - `/api/dashboard` endpoint

---

## 🗃️ Arhitektura

```
┌────────────────────────────────────────────────┐
│            Web Dashboard (Port 8080)           │
│         http://127.0.0.1:8080/dashboard        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ KPI Cards│ │  Charts  │ │Event Log │       │
│  └──────────┘ └──────────┘ └──────────┘       │
└────────────────────┬───────────────────────────┘
                     │ REST API
                     │
┌────────────────────▼───────────────────────────┐
│          Ryu SDN Controller (Port 6653)        │
│    ┌────────┐  ┌──────────┐  ┌──────────┐     │
│    │  ACL   │  │   DDoS   │  │    L2    │     │
│    │ Engine │  │ Detector │  │ Learning │     │
│    └────────┘  └──────────┘  └──────────┘     │
└────────────────────┬───────────────────────────┘
                     │ OpenFlow 1.3
                     │
┌────────────────────▼───────────────────────────┐
│            Open vSwitch (s1)                   │
└──────┬──────────────┬──────────────┬───────────┘
       │              │              │
   ┌───▼───┐      ┌───▼───┐      ┌───▼───┐
   │  h1   │      │  h2   │      │  h3   │
   │10.0.0.1│     │10.0.0.2│     │10.0.0.3│
   └───────┘      └───────┘      └───────┘
```

**Komponente:**
- **Ryu Controller** - SDN kontroler s ACL, DDoS detekcijom
- **Mininet** - Emulacija mreže (3 hosta, 1 switch)
- **Open vSwitch** - OpenFlow 1.3 switch
- **Web Dashboard** - Real-time UI s grafovima

---

## 🚀 Instalacija

### Preduvjeti

- Python 3.9+
- pip 20.0+
- Mininet 2.3+
- Open vSwitch 2.x
- Git

### Ubuntu/Debian Instalacija

```bash
# Ažuriranje sustava
sudo apt update && sudo apt upgrade -y

# Instalacija paketa
sudo apt install -y python3 python3-pip python3-venv mininet \
    openvswitch-switch hping3 curl git net-tools

# Kloniranje projekta
git clone https://github.com/jagarkarlo/SDN-security-aspects.git
cd SDN-security-aspects

# Python virtualno okruženje
python3 -m venv venv
source venv/bin/activate

# Instalacija Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Verifikacija

```bash
ryu --version          # Očekivano: ryu x.x
sudo mn --version      # Očekivano: 2.3.x
sudo ovs-vsctl --version  # Očekivano: 2.x.x
```

---

## ▶️ Pokretanje

Sustav se pokreće u **3 odvojena terminala**.

### Terminal 1️⃣: Ryu Controller + Dashboard

```bash
cd SDN-security-aspects
source venv/bin/activate
export EVENTLET_NO_GREENDNS=yes
PYTHONPATH=. python run_controller.py
```

**Očekivani output:**
```
loading app src.controller.sdn_security_app
UI:  http://127.0.0.1:8080/dashboard
API: http://127.0.0.1:8080/api/dashboard
```

**Otvori u browseru:** `http://127.0.0.1:8080/dashboard`

---

### Terminal 2️⃣: Mininet Topologija

```bash
cd SDN-security-aspects
sudo python3 src/mininet/topo_microseg.py
```

**Očekivani output:**
```
*** Starting controller
*** Starting 1 switches
[+] Topology started.
mininet>
```

---

### Terminal 3️⃣: Monitoring (Opcionalno)

```bash
watch -n 1 'curl -s http://127.0.0.1:8080/api/dashboard | jq ".counters"'
```

---

## 🧪 Testiranje

### Test 1: Osnovna Povezivost

```bash
mininet> pingall
```

**Rezultat:** 100% success, grafovi na dashboardu rastu.

---

### Test 2: ACL - Blokirani SSH Promet

ACL pravilo blokira TCP port 22 između h1 → h2.

```bash
mininet> h1 hping3 -S -c 3 -p 22 10.0.0.2
```

**Rezultat:**
- 100% packet loss
- Dashboard: ACL drop counter raste
- Event log: WARN - ACL DROP

---

### Test 3: ACL - Dozvoljeni HTTP Promet

```bash
# Pokreni HTTP server na h2
mininet> h2 python3 -m http.server 80 &

# Test s h1
mininet> h1 wget -O - -T 3 http://10.0.0.2 | head
```

**Rezultat:**
- Uspješna konekcija
- Dashboard: Allowed counter raste

---

### Test 4: DDoS Simulacija

```bash
mininet> h3 bash src/tests/ddos_simulation.sh 10.0.0.2
```

**Rezultat:**
- Dashboard: DDoS flag counter eksplozivno raste
- Event log: Puno WARN - DDoS flagged događaja
- Graf ddos flags/sec pokazuje veliki spike

**Zaustavi:** Ctrl+C u Mininet CLI-ju

---

### Test 5: REST API

```bash
curl http://127.0.0.1:8080/api/dashboard | jq
```

**Rezultat:** JSON response s counters, timeseries i last_events.

---

### Test 6: OpenFlow Flows

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Rezultat:** Lista instaliranih flow entries s različitim prioritetima (0, 50, 150).

---

## 📂 Struktura Projekta

```
SDN-security-aspects/
│
├── src/
│   ├── controller/
│   │   ├── __init__.py
│   │   └── sdn_security_app.py       # Glavni Ryu kontroler
│   │
│   ├── web/
│   │   ├── __init__.py
│   │   ├── dashboard_wsgi.py         # WSGI routes
│   │   ├── store.py                  # Thread-safe metrics
│   │   └── static/
│   │       ├── index.html            # Dashboard UI
│   │       ├── app.js                # Frontend logika
│   │       └── styles.css            # Stilovi
│   │
│   ├── mininet/
│   │   └── topo_microseg.py          # Mininet topologija
│   │
│   └── tests/
│       ├── ddos_simulation.sh        # DDoS attack simulator
│       └── run_ping_tests.sh         # Connectivity tests
│
├── run_controller.py                 # Ryu launcher
├── requirements.txt                  # Python dependencies
├── .gitignore
└── README.md
```

---

## 🛠 Tehnologije

| Komponenta | Tehnologija | Verzija | Svrha |
|------------|-------------|---------|-------|
| **SDN Kontroler** | Ryu | Latest | OpenFlow kontroler |
| **OpenFlow** | OpenFlow | 1.3 | Switch ↔ Controller protokol |
| **Mrežna Emulacija** | Mininet | 2.3+ | Virtualna mreža |
| **Virtual Switch** | Open vSwitch | 2.x | OpenFlow switch |
| **Backend** | Python | 3.9+ | Logika kontrolera |
| **Web Server** | Ryu WSGI | Built-in | HTTP server |
| **Frontend** | Vanilla JS | ES6 | Dashboard |
| **Charts** | Canvas API | Native | Grafovi |
| **Threading** | threading | Built-in | Thread-safe store |

---

## 🔧 Troubleshooting

### Dashboard ne prikazuje podatke

```bash
# Provjera je li Ryu pokrenut
ps aux | grep ryu

# Provjera API-ja
curl http://127.0.0.1:8080/api/dashboard

# Restart kontrolera
pkill -f run_controller.py
PYTHONPATH=. python run_controller.py
```

### Mininet ne može pokrenuti topologiju

```bash
# Očisti stare procese
sudo mn -c

# Restart Open vSwitch
sudo service openvswitch-switch restart

# Ponovno pokreni
sudo python3 src/mininet/topo_microseg.py
```

### Port 6653 ili 8080 zauzet

```bash
# Nađi i zaustavi proces
sudo lsof -ti:6653 | xargs kill -9
sudo lsof -ti:8080 | xargs kill -9
```

---

## 👥 Autori

**Fakultet organizacije i informatike, Varaždin**

| Ime | Uloga | GitHub |
|-----|-------|--------|
| **Petar Filjak** | Testing & Documentation | [@pfiljak21]() |
| **Karlo Jagar** | Implementation  | [@jagarkarlo](https://github.com/jagarkarlo) |
| **Fran Garafolić** | Testing & Documentation | [@fgarafoli21]() |

**Kolegij:** Sigurnost informacijskih sustava  
**Mentor:** 
**Akademska godina:** 2025/2026

---

<div align="center">

**[⬆ Povratak na vrh](#top)**

</div>
