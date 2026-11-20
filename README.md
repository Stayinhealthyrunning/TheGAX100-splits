# Gax100 Splits – version 1.2

Webbaserad analys av **The GAX 100 miles**, byggd på samma grund som Loppanalys.se:s Sätila-analys.

**Öppna publicerad version för granskning:** https://stayinhealthyrunning.github.io/TheGAX100-splits/

## Vad som är publicerat

- **14 upplagor (2014–2026)**; 2021-A och 2021-B behandlas som separata lopp.
- **945 officiella resultatposter**, **651 målgångar** och **2 482 publicerade tidsrader**.
- De **1 838 ursprungliga källobservationerna** i det tidigare källarkivet är ett separat källmått. Publicerade tidsrader omfattar också målpassager som representerar officiella sluttider: blanda inte ihop dessa summor.
- Löparsökning och profiler; resultat, placering, klubb/könsklass där källan stöder det; mellantider, historik, jämförelser, personlig loppplan, kartvisning och Kartduell.
- Enbart integritetsfiltrerade offentliga resultatfiler under `docs/data/races/`. Råkällor, privat GDPR-register och personidentifierande käll-ID:n stannar i `Stayinhealthyrunning/loppanalys-private-data`.

**Källbegränsningar:** 2025 och 2026 har enbart officiell målpassage i publicerade timing-stationsdata. Tidigare upplagor har varierande kontrolltäckning. Där källbaserad kilometersträcka eller rättighetsgodkänd historisk bana saknas ska fysisk fart och exakta historiska löparpositioner inte uppges. Kartduellens uppspelning är en modell mot en tydligt märkt banreferens, inte insamlad deltagar-GPS.

**Integritet:** Offentlig webbplats har `noindex, nofollow` och `robots.txt` med `Disallow: /`. Uppgifter som omfattas av opt-out eller andra sekretessspärrar ska filtreras bort i den privata exporten **innan** det SHA-256-kontrollerade publiceringsmanifestet byggs. Detta repo kan kontrollera manifest, dataintegritet och publicerad struktur men har inte tillgång till det privata registret. Full information och kontaktväg: https://www.loppanalys.se/integritet/

## Publik drift

`.github/workflows/pages.yml` bygger exakt `docs/` och publicerar enbart verifierad statisk utgåva efter godkända release- och webbläsartester. På `main` finns ett `docs/data/release-manifest.json` med SHA-256 för alla 16 integritetsfiltrerade resultat- och metadatafiler. `scripts/build_pages.py` stoppar publicering när dessa kontrollsummor inte stämmer eller någon årsfil saknas.

```bash
python3 -B tests/test_production_contract.py
python3 -B scripts/build_pages.py --docs docs --out production-check
python3 -B tests/test_production_browser.py --site production-check
```

Det sista testet kräver Playwright/Chromium; GitHub Actions installerar dessa. Testerna skriver inte ut löparnamn eller identifierare.

Om ett framtida utvecklingsrepo saknar publiceringsmanifest byggs i stället en **separat, tydligt märkt fiktiv demo**. Den är **inte** produktionsutgåvan på länken ovan.

## Versionshistorik och omfattning

Version **1.2 (20 november 2026)** sammanfattar den verkligt publicerade, filtrerade datamängden och de tidigare färdigbyggda funktionerna. Den kompletterar tidigare utveckling med särskild QA för skarpa data, enhetlig versions-/metodinformation och kontroll av att produktionsflödet inte oavsiktligt återgår till demonstration.

GAX100 ligger tills vidare **utanför startsidans lopplista på Loppanalys.se** under granskningen. Det äldre `gax100-analys` bevaras för historik och separat GitHub Support-sanering; dess äldre persondatahistorik ska aldrig återintroduceras i detta rena repo.

Mer detaljer: [Granskning och release](docs/REVIEW_AND_RELEASE.md) · [V1 release notes](docs/V1_RELEASE_NOTES.md).

## Version 1.2 – bild, datatäckning, källkilometer och musik

- Den tidigare tecknade Ales stenar-bilden är ersatt med **originalgenererad fotorealistisk kustbild** med tre traillöpare som springer åt höger. Bilden ligger lokalt i repot under `docs/assets/hero-ales-stenar-trail-runners.webp` och kontrolleras med SHA-256 i Pages-bygget.
- Fotobaserad designprofil, uppdaterad färgsättning, responsiva mobilvyer och banavsnittens bildbehandling ger ett gemensamt uttryck.
- **Tomma dynamikkort döljs helt.** Kvarvarande kort expanderar till full bredd utan hål. Gäller bland annat placeringslyft, sista tredjedelen, relativa segmentdiagram och ålderskort utan faktisk källa. Start–Mål och resultat som har data visas fortsatt.
- Källmärkt **historisk kilometeröversikt** i `docs/data/historical-checkpoint-km.json` hjälper läsaren skilja årsverifierade 44/80/130 km från motstridiga rubriker 2019/2021 och referensavstånd utan årsverifiering 2020/2024. Dessa referenser ändrar **aldrig** officiella passertider, personuppgifter, fysisk segmentfart eller distansberäkningar.
- Separat, begränsad Legends Tracking-undersökning av arrangörslänkade webbplatser för 2024 och 2026: de svarar, men den åtkomliga publika vyn gav inga verifierbara nya stationstider/metadata. Inga identifierare, personpositioner eller spekulativa mellantider importeras.
- **Musiken ingår:** `docs/assets/audio/audioera-acoustic-guitar-happy-637709.mp3` (originalfil, kontrollsumma och filstorlek verifieras). Ljudet används i Replay och Kartduell, kan slås av, har volymreglage och kreditering `Aleh Mikalayeu (AudioERA) · Pixabay`. Spelaren hämtar sin konfiguration från `docs/data/replay-audio.json`, vilket gör den utbytbar utan att ändra analyslogik.
- Oförändrat: 14 historiska upplagor, 945 integritetsfiltrerade resultat och 651 fullföljande. Granskningsadressen ligger separat från Loppanalys.se:s startsida.

Se [versionsanteckningar 1.2](docs/V1_2_RELEASE_NOTES.md) och [1.1](docs/V1_1_RELEASE_NOTES.md).
