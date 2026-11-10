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

Österlendesignen har ersatt den tidigare stora hero-/rubrikytan med en kompakt introduktion, originalillustrerad kustvy, varma fält-/sandtoner, salvia och havsblå accenter. Direkt under toppen finns årsväljaren och sökverktyget. Till detta har vi lagt två källstödda informationsdelar, nu samlade i en **pop-up** som öppnas med knappen *Upptäck de fyra etapperna*:

- **Fyra delar:** Ystad–Magleberg, Magleberg–Haväng, Haväng–Sandhammaren och Sandhammaren–Ystad, baserade på arrangörens banbeskrivning på https://gax100.se/bana-karta/.
- **Stationer och reptider:** arrangörens aktuella information på https://gax100.se/information/ (2027). Aid-stationernas kilometer och reptidstabellens kilometer skiljer sig åt vid vissa punkter och hålls avsiktligt åtskilda.

`scripts/build_offline_preview.py` skapar numera **945 unika påhittade svenska namn**, fiktiva klubbar, kön, realistiskt spridda sluttider, placeringar, DNF/DNS och **tio modellerade passertider per fullföljande demolöpare**. Sluttidernas grova spann och 2026 års anonymiserade köns-/statusfördelning har kalibrerats mot https://gax100.se/resultat/ – inga verkliga namn, klubbkopplingar, startnummer eller individsplittider kopieras därifrån. Andra års könsfördelningar är enbart modellantaganden.

**Demografiska egenskaper, alla tider och alla splits är uttryckligen fiktiva.** Stationernas modell baseras på 2027 års kända banbeskrivning och påstår inte att samma kontrollpunkter användes för samtliga historiska upplagor. Analysmotorn kan beräkna modelltempo enbart i demo-versionen; riktiga historiska GAX-resultat har fortsatt spärr för overifierad GPS-/distansbaserad fart.

Kontrollerna ligger i `tests/test_synthetic_data.py`, `tests/test_offline_preview_browser.py` och `.github/workflows/quality.yml`, inklusive 390px/1440px visningsprov och aktiva profil-/jämförelsedialoger.

## UX- och analysförbättringar, november 2026

- **Fyra banavsnitt samt stationer och reptider** öppnas nu i en tillgänglig pop-up. De tar ingen permanent höjd mellan startsidan och analysen.
- **Infoikoner** finns vid överordnade sektioner och individuella analyskort, med begriplig metodinformation samt tydlig skillnad mellan verklig källa och fiktiv demo.
- **Klasser och kön** ligger kompakt under staplarna i **Start till mål**, i stället för ett separat fullbrett kort.
- **Starkaste avslutningen** fungerar med GAX:s faktiska målkontrollbenämning `Mål · Ystad`, även i syntetiskt testläge.
- **Delsträckor & personlig loppplan** har nu två lägen i en enda sektion. Standardläget är hela loppet; personlig plan börjar med upplagans **medianmåltid** som går att ändra.
- **Banans dimensioner** saknar nu redundant tom arrangörsdistans. Tävlingsdistans, faktiskt GPX-underlag och tidtagningens km-axel redovisas separat.
- **Andel kvinnor och män över tid** ritas från alla 945 fiktiva demolöpares kön (2026 kalibrerat mot offentlig gruppsumma). Detta är **inte** en verifierad historisk könstrend för verkliga deltagare.

## Bankarta, GPX-jämförelse och Kartduell

**Bana & kartor** använder samma OpenStreetMap-rendering som Sätila, med 94 % opacitet för kartplattorna och automatisk zoom för kartans utsnitt. Årsvalet visar närmaste tillgängliga GPX-år. Vid lika avstånd används det äldre året. Båda 2021-upplagorna visar 2021-kandidaten som referens eftersom A/B-kopplingen är oklar.

I **Jämför GPX-spår på samma karta** finns arrangörens Garmin-export för 2026, Plotaroute-kandidaterna för 2021 och 2022, och AllTrails-spåret med obekräftat år. AllTrails-spåret ingår endast i jämförelsevyn. 2021-spårets 58 avbrott ritas som luckor. 2018-spåret och den andra 2021-kandidaten är dokumenterade i källinventeringen, men deras original har inte kunnat återfinnas. De offentliga filerna innehåller kartgeometri med höjd och källhänvisning. Original-GPX, tidsstämplar och deltagaruppgifter ingår inte.

**Individuell Replay** och **Kartduell** använder automatiskt samma inbyggda banreferenser. Källåret visas i kartan. Uppspelningen använder fiktiva passertider, och markören hoppar vid kända spårglapp. Kartorna har zoomknappar och återställning till hela banan. Dubbelklick zoomar mot den valda punkten. På kartor med positionsreglage går det att panorera en inzoomad vy med Skift + dra.

`scripts/build_course_display.py` återskapar kartgeometrin från kontrollsummerade originalfiler. `tests/test_gax_gpx_local.py` provar årsväljaren, zoom, lagerjämförelse och uppspelning.

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
