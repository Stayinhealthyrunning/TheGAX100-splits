# Gax100 Splits 1.1

**Datum:** 20 november 2026  
**Granskningsadress:** https://stayinhealthyrunning.github.io/TheGAX100-splits/  
**Publiceringsmodell:** GitHub Pages på separat granskningsadress, utan länk på loppanalys.se:s startsida.

## Implementerat

1. Ny egenritad Österlenidentitet med kust, Ales stenar och Ystad, mer samlad typografi och responsiv stationsöversikt.
2. Rubrik och delningsmetadata: **Gax100 Splits**.
3. Arrangörens 2027-information visar **Start · Ystad · 0 km · 10.00** samt stationer och mål; detta är uttryckligen inte historisk kontrollbevisning.
4. Innerpadding och vertikalt avstånd i officiella kontrollpassager.
5. **Nominell snittfart för fullföljare** utifrån officiell sluttid och 160,9344 km. Segmentbaserad fysisk fart är fortfarande spärrad utan verifierade historiska distanser.
6. Gemensam, lätt utbytbar ljudkonfiguration, spelarstyrning med volym och diskret credit `Aleh Mikalayeu / AudioERA · Pixabay`. **Öppen begränsning:** binär MP3 finns inte i GitHub; låtknappen är avaktiverad när filen saknas. Den exakta användarbifogade MP3-filen har SHA-256 `ed089921eb56654ab4c97025c5ceebd057e6c739a9d3f15328033dc909d09e49`; servering kräver exakt denna fil. Försök till direkt import från upphovskällan avvisades (HTTP-fel), och varken Google Drive eller annan mellanlagring används.
7. Start och kontrollpassager särskiljs i historisk källvy; för år med mål som enda offentlig passage står tydligt att mellanpassager inte finns, och Start→Mål analyseras.
8. Prestations- och placeringsanalysens tomlägen förklarar dataförutsättningar; snabbaste registrerade målgångar visas när segmentjämförelser inte kan göras.

## Käll- och kvalitetsspärrar

- 14 publicerade upplagor, 945 resultat, 651 fullföljande, 2 482 offentligexporterade tidsposter. Dessa är redan privacy-filtrerade; manifestkontroll skyddar de 16 källfilerna.
- 2025–2026 innehåller i nuvarande publika export endast målpassage, medan vissa äldre upplagor har mellantider.
- Ingen syntetisk mellantid eller individuellt GPS-spår presenteras som uppmätt; karta och replay använder märkta referensbanor.
- `noindex`, `robots.txt`, befintlig GDPR/opt-out-kedja och separat granskningspublicering bibehålls.
- `tests/test_production_browser.py` kontrollerar rubrik, start, nominell snittfart, källtäckning, mobil/desktop samt jämförelser.

**Status:** 1.1 kod och statistik kan publiceras och granskas. Full ljudfunktion väntar på att exakt MP3 når `docs/assets/audio/` i GitHub och ska inte beskrivas som levererad innan dess.
