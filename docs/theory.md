# Teorijska podloga (Theory)

## 1. Uvod u SDN (Software-Defined Networking)
**Software-Defined Networking (SDN)** je mrežna paradigma koja odvaja:
- **Control plane (upravljanje)** – logika odlučivanja (kontroler)
- **Data plane (prosljeđivanje)** – uređaji koji samo izvršavaju pravila (switch)

U klasičnim mrežama svaki switch/router sam donosi odluke o prosljeđivanju. U SDN-u se kontrola centralizira u **SDN kontroleru**, dok mrežni uređaji postaju programabilni i upravljani pravilima.

Glavne prednosti SDN-a:
- centralizirano upravljanje mrežom
- jednostavnije provođenje sigurnosnih pravila
- fleksibilnost i mogućnost automatizacije
- bolja vidljivost i nadzor prometa

Mogući nedostaci:
- kontroler može postati “single point of failure”
- sigurnost kontrolera je kritična (kompromitacija znači kompromitaciju mreže)
- potrebno je dobro dizajnirati pravila kako se ne bi smanjile performanse

---

## 2. OpenFlow protokol
**OpenFlow** je standardizirani protokol koji omogućuje komunikaciju između:
- SDN kontrolera (npr. Ryu)
- OpenFlow switcha (npr. Open vSwitch)

Kontroler instalira pravila u switch u obliku **flow entries**. Svako pravilo tipično sadrži:
- **match** – koji promet se prepoznaje (npr. IP adresa, TCP port)
- **actions** – što učiniti (npr. output na port, drop)
- **priority** – koji rule je jači ako više njih odgovara

U ovom projektu koristi se **OpenFlow 1.3**, što omogućuje detaljne match opcije (L2/L3/L4) i rad s prioritetima.

---

## 3. Ryu SDN Controller
**Ryu** je open-source SDN kontroler napisan u Pythonu. Omogućuje:
- upravljanje OpenFlow switch uređajima
- pisanje vlastitih aplikacija (packet handlers)
- dinamičku instalaciju flow pravila
- integraciju dodatnih modula (npr. web dashboard)

Ryu radi tako da:
1. switch se spoji na kontroler
2. kontroler instalira početna pravila (npr. table-miss)
3. kada switch ne zna što s paketom, šalje ga kontroleru (**PacketIn**)
4. kontroler odlučuje i eventualno instalira flow pravila (**FlowMod**)

---

## 4. Mininet i Open vSwitch (OVS)
**Mininet** je alat za emulaciju mreža koji pokreće virtualne hostove, switcheve i linkove na jednom računalu.
Koristi Linux network namespaces i virtualne linkove kako bi simulirao realnu mrežu.

**Open vSwitch (OVS)** je virtualni switch koji podržava OpenFlow i može se spojiti na SDN kontroler.

U ovom projektu Mininet se koristi za kreiranje jednostavne topologije:
- 1 switch (s1)
- 3 hosta (h1, h2, h3)

---

## 5. Sigurnosni aspekti u SDN-u
Zbog centralizirane kontrole, SDN omogućuje sigurnosne politike koje je često lakše implementirati nego u tradicionalnim mrežama.

Tipični sigurnosni mehanizmi u SDN-u:
- ACL (Access Control List) filtriranje
- segmentacija mreže i mikrosegmentacija
- detekcija anomalija (npr. DoS/DDoS pokušaji)
- centralno logiranje i monitoring

U ovom projektu fokus je na:
- **ACL filtriranju na Layer-4 razini** (TCP/UDP portovi)
- **heurističkoj detekciji sumnjivog prometa** (DDoS flag)
- **vidljivosti i monitoringu** putem web dashboarda

---

## 6. Access Control List (ACL)
**ACL** je sigurnosni mehanizam koji određuje koji promet je dopušten ili zabranjen.
U SDN-u ACL se može provoditi centralno na kontroleru.

U ovom projektu ACL se provodi na temelju:
- izvorne IP adrese (src IP)
- odredišne IP adrese (dst IP)
- protokola (TCP/UDP)
- odredišnog porta (dst port)

Ako promet nije dopušten, kontroler instalira OpenFlow pravilo koje radi **DROP**.

---

## 7. DDoS / DoS (heuristika detekcije)
**DoS/DDoS napadi** često se manifestiraju kao:
- velik broj novih tokova u kratkom vremenu
- skeniranje portova (mnogi različiti portovi)
- veliki broj zahtjeva prema cilju (dst host)

U projektu je implementirana jednostavna heuristika:
- prati se promet prema odredišnoj IP adresi
- u određenom vremenskom prozoru broji se broj različitih portova
- ako je prag premašen, događaj se označava kao **DDoS flagged**

Ova verzija služi prvenstveno za detekciju i prikaz u dashboardu (bez automatskog blokiranja prometa).

---

## 8. Monitoring i vizualizacija (Dashboard)
Monitoring je ključan dio sigurnosti. Projekt sadrži web dashboard koji prikazuje:
- broj dopuštenih paketa
- broj ACL drop odluka
- broj DDoS flag događaja
- zadnje eventove (INFO/WARN) i detalje

Dashboard dohvaća podatke preko API endpointa:
- `/api/dashboard` (JSON snapshot)
i prikazuje ih na:
- `/dashboard` (UI)

---

## Zaključak teorijskog dijela
Ovaj projekt koristi SDN principe kako bi demonstrirao centralizirano upravljanje i sigurnosne mehanizme.
Ryu i OpenFlow omogućuju dinamičko instaliranje pravila u switchu, dok Mininet/OVS pružaju brzo i praktično testno okruženje.
