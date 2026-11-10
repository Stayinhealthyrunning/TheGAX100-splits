# TheGAX100-splits

GAX100 – loppanalys med resultat, kontrolltider, löparprofiler, statistik och interaktiva jämförelser. Bygger på samma visuella gränssnitt som Sätila Trail.

## Granska webbplatsen

**GitHub Pages:** https://stayinhealthyrunning.github.io/TheGAX100-splits/

Detta är en **design- och funktionstestversion med fiktiva deltagare, tider och kontrollpassager**. Den innehåller 14 korrekta GAX-upplagor med officiellt verifierade aggregerade resultatantal. Den återskapar GAX-anpassningen av Sätilas analysgränssnitt. Ingen verklig deltagarpost exponeras i detta offentliga repo.

För att aktivera webbsidan första gången: `Settings → Pages → Build and deployment → Source: GitHub Actions`, därefter `Actions → GAX100 safe Pages preview → Run workflow`. Pages är offentlig även om adressen inte finns på loppanalys.se.

## Färdigflyttad kod

- Design, CSS, JavaScript, profiler och löparjämförelser från den granskade GAX100-Sätila-varianten.
- 14 upplagor 2014–2026, inklusive två separata lopp 2021-A och 2021-B.
- **945** officiella resultatposter, **651** målgångar och **1 838** källregistrerade kontrollobservationer i aggregat.
- För **2023** gäller den officiella resultattabellen: **90 resultatposter och 70 målgångar**.
- `docs/data/races/*.json`: alla deltagar- och kontrollistor är avsiktligt tomma och markerade `PRIVATE_DATA_WITHHELD`.
- Den publika webbversionen som GitHub Pages bygger genereras av `scripts/build_offline_preview.py` och använder **945 påhittade svenska löparnamn**.

## Nytt design- och datautkast – 10 november 2026

Österlendesignen har ersatt den tidigare stora hero-/rubrikytan med en kompakt introduktion, originalillustrerad kustvy, varma fält-/sandtoner, salvia och havsblå accenter. Direkt under toppen finns årsväljaren och sökverktyget. Till detta har vi lagt två källstödda informationssektioner:

- **Fyra delar:** Ystad–Magleberg, Magleberg–Haväng, Haväng–Sandhammaren och Sandhammaren–Ystad, baserade på arrangörens banbeskrivning på https://gax100.se/bana-karta/.
- **Stationer och reptider:** arrangörens aktuella information på https://gax100.se/information/ (2027). Aid-stationernas kilometer och reptidstabellens kilometer skiljer sig åt vid vissa punkter och hålls avsiktligt åtskilda.

`scripts/build_offline_preview.py` skapar numera **945 unika påhittade svenska namn**, fiktiva klubbar, kön, realistiskt spridda sluttider, placeringar, DNF/DNS och **tio modellerade passertider per fullföljande demolöpare**. Sluttidernas grova spann och 2026 års anonymiserade köns-/statusfördelning har kalibrerats mot https://gax100.se/resultat/ – inga verkliga namn, klubbkopplingar, startnummer eller individsplittider kopieras därifrån. Andra års könsfördelningar är enbart modellantaganden.

**Demografiska egenskaper, alla tider och alla splits är uttryckligen fiktiva.** Stationernas modell baseras på 2027 års kända banbeskrivning och påstår inte att samma kontrollpunkter användes för samtliga historiska upplagor. Analysmotorn kan beräkna modelltempo enbart i demo-versionen; riktiga historiska GAX-resultat har fortsatt spärr för overifierad GPS-/distansbaserad fart.

Kontrollerna ligger i `tests/test_synthetic_data.py`, `tests/test_offline_preview_browser.py` och `.github/workflows/quality.yml`, inklusive 390px/1440px visningsprov och aktiva profil-/jämförelsedialoger.

## Kartduell med 2026 års GPX – lokalt och utan uppladdning

**Ja, arrangörens officiella 2026-GPX finns som navigationsunderlag:** https://gax100.se/bana-karta/ hänvisar till Garmin-kursen https://connect.garmin.com/app/course/484861455 (GAX100M-2026). Tidigare arkivinventering kunde verifiera kursen men Garmin-proxy gav enbart tomma svar; den fullständiga 2026-koordinatfilen hade därför inte importerats till det nya repot.

För att prova Kartduellen utan att publicera arrangörens GPX:

1. Öppna GitHub Pages-versionen, välj **2026** under Loppår.
2. Öppna arrangörens Garmin-länk ovan och ladda ned GPX-filen med Garmin Connects exportfunktion (Garmin kan kräva inloggning).
3. På GAX-sidan, under **Löparjämförelse**, välj **Välj GPX-fil för 2026**.
4. Välj 2–5 fiktiva löpare, klicka **Öppna Kartduell**, spela eller dra tävlingsklockan.

GPX läses **uteslutande i webbläsarens arbetsminne** och skickas inte till GitHub Pages eller något GAX-API. Den försvinner vid omladdning; byter du år till annat än 2026 är Kartduellen för banan spärrad. Inga ruttpunkter lagras som publika filer. Rättighet att ladda ned för privat navigering är inte liktydigt med licens för webbåterpublicering.

Det **är 2026 års bangeometri, inte löparnas GPS-loggar**. Demoversionens namn, passertider och rörelser är fiktiva och beräknas genom tidsinterpolation mellan modellkontroller. En karta med en rörlig markör är därför inte bevis för en faktiskt uppmätt position. De verkliga löparresultaten berörs inte.

Kontrolleras automatiskt av `tests/test_gax_gpx_local.py` med en syntetisk 152 km-testbana som skapas i testminnet. Testet provar inläsning, 2 löpare, SVG-kartuppspelning, att årsvalet begränsar routen till 2026 samt att GPX aldrig laddas upp eller sparas efter omladdning. **Testbanan följer inte GAX och publiceras aldrig.**

## Privat resultatdatabas och GDPR

De faktiska 945 deltagarposterna och verkliga kontrolltiderna ligger **endast** i det privata repot `Stayinhealthyrunning/loppanalys-private-data`, i `gax100/fresh/gax100.sqlite`. Dit hör även `gax100/satila_blueprint_adapter.py` och den privata GDPR-publiceringsgrinden `gax100/privacy_release_gate.py`, med Sätilas gemensamma spärrregister samt GAX-ägarintyget om vuxna deltagare.

Det finns **ingen automatisk import av verkliga deltagare till GitHub Pages**. Riktiga, identifierbara resultat kan publiceras först efter separat dokumenterat publiceringsbeslut och godkända GDPR-kontroller. GPS/geografi framställs inte som verifierat utan kontrollerat källunderlag.

## Testa och bygga förhandsgranskningen

```bash
python3 -B tests/test_blueprint_contract.py
python3 -B scripts/build_offline_preview.py --docs docs --out public-preview/index.html
```

Öppna den genererade `public-preview/index.html` lokalt direkt i en webbläsare. GitHub Actions publicerar **endast den genererade demofilen**, aldrig `docs/data/races` eller privata källfiler.

## Ren historik

Denna kod har kopierats som nya filer från den granskade och anonymiserade kodgrenen i det gamla GAX-repot vid commit `8bf5fe6f610fda43cb92ac450dd4cf3a3e1f629d`. **Inga gamla commits, Git-refs, releaseartefakter eller personuppgiftsfiler har migrerats.**

Det gamla repot ska hållas intakt tills detta nya är verifierat och det separata historikärendet hos GitHub Support har hanterats. Ingen CNAME till loppanalys.se används.
