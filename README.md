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
- Den publika webbversionen som GitHub Pages bygger genereras av `scripts/build_offline_preview.py` och använder **945 påhittade demolöpare**.

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
