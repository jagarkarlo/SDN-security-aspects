# Setup i pokretanje projekta (implementation/setup.md)

Ovaj dokument opisuje kako instalirati potrebne alate i pokrenuti projekt:
- Ryu SDN kontroler (OpenFlow 1.3)
- Mininet topologiju (OVS switch + hostovi)
- web dashboard (UI + API)

> Preporučeno okruženje: Linux (Ubuntu/Debian) ili virtualna mašina.

---

## 1) Preduvjeti
Provjerite:
```bash
python3 --version
pip3 --version
sudo mn --version
sudo ovs-vsctl --version


2) Instalacija paketa (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  python3 python3-pip python3-venv \
  mininet openvswitch-switch \
  curl net-tools hping3

3) Kloniranje repozitorija
git clone https://github.com/jagarkarlo/SDN-security-aspects.git
cd SDN-security-aspects

4) Virtualno okruženje
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ryu eventlet


Ako postoji requirements.txt:

pip install -r requirements.txt

5) Pokretanje kontrolera

Terminal 1:

cd SDN-security-aspects
source venv/bin/activate

export EVENTLET_NO_GREENDNS=yes
PYTHONPATH=. python run_controller.py src.controller.sdn_security_app


Dashboard:

http://127.0.0.1:8080/dashboard

API:

http://127.0.0.1:8080/api/dashboard

6) Pokretanje Mininet topologije

Terminal 2:

cd SDN-security-aspects
sudo python3 src/mininet/topo_microseg.py

7) Čišćenje ako zapne
sudo mn -c
sudo ovs-vsctl show

8) Provjera OpenFlow 1.3

U Mininet CLI:

mininet> sh ovs-vsctl get bridge s1 protocols


Ako nije OpenFlow13:

mininet> sh ovs-vsctl set bridge s1 protocols=OpenFlow13


Provjera kontrolera:

mininet> sh ovs-vsctl get-controller s1


Očekivano:

tcp:127.0.0.1:6653


---

# 6) `implementation/tests.md`

```md
# Testiranje funkcionalnosti (implementation/tests.md)

Ovaj dokument sadrži osnovne testove za provjeru:
- povezivosti
- ACL blokiranja
- DDoS flag detekcije
- instalacije flow pravila u OVS-u

---

## 1) Ping svih hostova
U Mininet CLI:
```bash
mininet> pingall


Očekivanje:

svi hostovi se međusobno pingaju

2) Test HTTP prometa (curl)

Pokreni HTTP server na h2:

mininet> h2 python3 -m http.server 80 &


Test s h1:

mininet> h1 curl http://10.0.0.2


Očekivanje:

vraća HTML sadržaj (directory listing ili page)

3) Test ACL blokade (hping3)

Primjer testiranja TCP porta (npr. 22):

mininet> h1 hping3 -S -c 3 -p 22 10.0.0.2


Očekivanje:

packet loss (DROP)

u kontroler logu se vidi ACL DROP

4) Provjera flow pravila u OVS-u

U Mininet CLI:

mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1


Traži DROP pravila (ako ACL blokira):

mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1 | grep drop

5) DDoS flag (simulacija)

Primjer generiranja većeg broja zahtjeva / portova (osnovno):

mininet> h3 bash -c 'for p in $(seq 8000 8050); do hping3 -S -c 1 -p $p 10.0.0.2 >/dev/null 2>&1; done'


Očekivanje:

kontroler log može prikazati "DDoS flagged"

dashboard povećava DDoS flag brojač

Napomena: u ovoj verziji se promet ne blokira, nego se samo označava (flag).

6) Provjera dashboarda

Otvorite UI:

http://127.0.0.1:8080/dashboard

Provjerite:

KPI brojače

graf u realnom vremenu

tablicu zadnjih događaja

API snapshot:

http://127.0.0.1:8080/api/dashboard


---

#  7) `results/findings.md`

```md
# Findings / Rezultati (results/findings.md)

Ovaj dokument sadrži sažetak opažanja i dokaza testiranja.

---

## 1) Funkcionalnost mreže
- Mreža je uspješno pokrenuta u Mininetu.
- Hostovi mogu međusobno komunicirati (pingall uspješan).

---

## 2) ACL pravila
- ACL mehanizam se provodi na kontroleru.
- Zabranjeni promet rezultira instalacijom DROP flow pravila u OVS switchu.
- ACL DROP događaji su vidljivi u kontroler logu i dashboardu.

---

## 3) DDoS flag heuristika
- Heuristika detektira sumnjivu aktivnost prema cilju (dst IP) kada se u kratkom vremenu gađa veliki broj portova.
- DDoS flag se prikazuje u dashboardu kao metrika i event log.

> Napomena: ova verzija projekta ne provodi automatsko blokiranje, nego samo označava (flag) događaje.

---

## 4) Dashboard (monitoring)
- Dashboard UI je dostupan na `/dashboard`.
- API JSON snapshot dostupan je na `/api/dashboard`.
- Prikazuje KPI brojače, grafove po sekundi i zadnje događaje.


