# GAX100 Analys 1.0

Webbaserad analys av **The GAX 100 miles**, byggd på samma grund som Loppanalys.se:s Sätila-analys.

**Öppna v1.0 för granskning:** https://stayinhealthyrunning.github.io/TheGAX100-splits/

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

Version **1.0 (20 november 2026)** sammanfattar den verkligt publicerade, filtrerade datamängden och de tidigare färdigbyggda funktionerna. Den kompletterar tidigare utveckling med särskild QA för skarpa data, enhetlig versions-/metodinformation och kontroll av att produktionsflödet inte oavsiktligt återgår till demonstration.

GAX100 ligger tills vidare **utanför startsidans lopplista på Loppanalys.se** under granskningen. Det äldre `gax100-analys` bevaras för historik och separat GitHub Support-sanering; dess äldre persondatahistorik ska aldrig återintroduceras i detta rena repo.

Mer detaljer: [Granskning och release](docs/REVIEW_AND_RELEASE.md) · [V1 release notes](docs/V1_RELEASE_NOTES.md).
