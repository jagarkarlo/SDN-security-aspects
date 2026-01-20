# Završni izvještaj (docs/report.md)

## Sažetak
Projekt demonstrira sigurnosne aspekte Software-Defined Networking (SDN) pristupa kroz implementaciju Ryu kontrolera i Mininet emulacije. Implementirana su tri ključna dijela: L2 learning switch, ACL filtriranje na L4 razini (IP/protokol/port) te heuristička detekcija sumnjivog ponašanja (DDoS flag). Dodatno je izrađen web dashboard (UI + API) za praćenje metrika i događaja u realnom vremenu.

---

## Korištene tehnologije
- Python 3.x
- Ryu SDN framework
- OpenFlow 1.3
- Mininet
- Open vSwitch (OVS)
- curl / ping / hping3 (testiranje)
- WSGI (Ryu app.wsgi) + frontend (HTML/JS/CSS)

---

## Implementirani sustav
### Topologija
Topologija se sastoji od jednog OpenFlow switcha (s1) i tri hosta (h1, h2, h3). Switch je spojen na Ryu kontroler (tcp 127.0.0.1:6653). Hostovi koriste adresni prostor 10.0.0.0/24.

### Kontroler (logika)
Kontroler:
1. postavlja table-miss pravilo (novi tokovi idu na kontroler)
2. uči MAC → port mapiranje (learning switch)
3. provodi ACL logiku:
   - za zabranjeni promet instalira DROP flow
4. provodi DDoS heuristiku:
   - kada detektira sumnjivu aktivnost, generira događaj (flag) i bilježi ga

### Monitoring (Dashboard)
Dashboard koristi “store” koji bilježi:
- broj dopuštenih prosljeđivanja (allowed)
- broj ACL drop odluka
- broj DDoS flag događaja
- listu zadnjih događaja (log)
- timeseries vrijednosti “po sekundi” (graf)

UI osvježava podatke svake sekunde preko `/api/dashboard` i prikazuje KPI, graf i tablicu događaja.

---

## Rezultati i opažanja
- Osnovna povezivost funkcionira (ping između hostova)
- ACL pravila ispravno blokiraju odabrani promet i u OVS-u se vidi instalirano DROP pravilo
- DDoS heuristika se može aktivirati generiranjem prometa koji prelazi zadani prag te se pojavljuje kao “flag” u dashboardu
- Dashboard pruža bolju vidljivost (observability) i olakšava demonstraciju rezultata

---

## Usporedba s postojećim rješenjima (kratko)
Slične funkcionalnosti mogu se pronaći u:
- SDN kontrolerima (Ryu, OpenDaylight, ONOS)
- tradicionalnim firewall/ACL rješenjima na uređajima ili hostovima

Prednost SDN pristupa:
- centralizirana kontrola pravila
- dinamička instalacija flowova (brza reakcija)
- jednostavniji monitoring i prilagodba pravila

---

## Zaključak
Projekt uspješno demonstrira kako se SDN može koristiti za sigurnosne politike i nadzor prometa. Kombinacija Mininet + OVS omogućuje jednostavno testiranje, dok Ryu kontroler omogućuje programabilno upravljanje mrežnim pravilima. Dashboard dodatno olakšava praćenje i prezentaciju sigurnosnih događaja.

---

## Budući rad (moguća poboljšanja)
- proširenje ACL-a na whitelist politiku ili konfiguraciju iz vanjske datoteke (YAML/JSON)
- automatska mitigacija nakon DDoS flag-a (npr. privremeni DROP s timeoutom)
- detaljnija statistika po hostovima (top talkers, per-src/per-dst metrika)
- autentikacija za dashboard/API
