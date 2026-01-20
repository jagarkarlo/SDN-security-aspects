# Plan implementacije (docs/plan.md)

## Cilj projekta
Cilj projekta je demonstrirati sigurnosne aspekte SDN-a kroz praktičnu implementaciju koristeći:
- **Ryu OpenFlow kontroler (OpenFlow 1.3)**
- **Mininet + Open vSwitch (OVS)**
- **Web dashboard** (UI + API) za monitoring

U praktičnom dijelu implementirano je:
- L2 learning switch ponašanje
- ACL filtriranje (blokiranje odabranih tokova)
- heuristika za DDoS (flagging) + logiranje i prikaz na dashboardu

---

## Koraci rada (step-by-step)
1. **Priprema okruženja**
   - Linux (ili VM na Windows/Mac)
   - provjera verzija: Python, Mininet, OVS

2. **Instalacija alata**
   - Python 3 + pip + venv
   - Ryu framework + eventlet
   - Mininet + Open vSwitch
   - testni alati: ping, curl, hping3

3. **Postavljanje topologije u Mininetu**
   - 1 switch (s1)
   - 3 hosta (h1, h2, h3)
   - remote controller na `127.0.0.1:6653`

4. **Implementacija SDN kontrolera (Ryu app)**
   - Table-miss pravilo (PacketIn prema kontroleru)
   - L2 learning (MAC → port učenje)
   - ACL pravila (drop za zabranjeni promet)
   - heuristika DDoS (flag + log)

5. **Implementacija monitoringa (Dashboard)**
   - Thread-safe store (brojači + timeseries + event log)
   - WSGI rute: UI `/dashboard`, API `/api/dashboard`
   - frontend (HTML/JS) koji osvježava podatke svake sekunde i crta graf

6. **Testiranje**
   - osnovna povezivost (pingall)
   - HTTP test (curl)
   - ACL blokada (hping3 prema blokiranom portu)
   - provjera flowova u OVS-u (`ovs-ofctl dump-flows`)

7. **Dokumentiranje rezultata**
   - screenshotovi: dashboard, testovi, dump-flows
   - zapis logova kontrolera i OVS-a
   - zaključak + literatura (Google Scholar)

---

## Očekivani ishod
- mreža funkcionira kao learning switch (ping radi)
- ACL blokira zabranjeni promet (DROP pravilo u flow tablici)
- DDoS heuristika generira “flag” i vidi se u dashboardu
- dashboard prikazuje KPI i grafove u realnom vremenu
