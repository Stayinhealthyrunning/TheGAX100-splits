# GAX100 – verifierbar granskning och skyddad publicering

## Vad som flyttats till nya repot

Den granskade GAX100/Sätila-frontendens HTML, åtta CSS/JavaScript-resurser, samtliga 14 GAX-upplagor som aggregerade metadata, individdata-tomma JSON-filer och reproducerbara UI-/säkerhetstester.

Utgångsversion: gamla GAX-repot `gax100-analys`, källa **`8bf5fe6f610fda43cb92ac450dd4cf3a3e1f629d`**. Här har **inget gammalt Git-träd, refs, releases eller historik** kopierats över.

## Syftet med GitHub Pages

Här publiceras enbart en **demonstrationsversion**. En enda HTML med **945 fiktiva namn, fiktiva tider och fiktiva kontroller** genereras från syntetiskt testskript. Antalet verkliga GAX-upplagor samt aggregerade resultatantal kommer däremot från kontrollerade källsummor. Den uttryckliga design-demovarningen ska alltid visas.

Första aktivering av Pages måste ske av repoägaren via `Settings → Pages → Source: GitHub Actions`. Det automatiska flödet `.github/workflows/pages.yml` skapar sidan endast efter automatiskt godkänt källskydd.

## Designgranskning och tid-/GPX-proveniens

Efter genomgången den 10 november har sidan ett kortare analysflöde: fyra naturskildringar samt stationer öppnas i pop-up, alla större sektioner har metodinformation, klassfördelningen ligger under Start till mål, och Delsträckor + Personlig loppplan delar en sektion med två lägen. Starkaste avslutningen accepterar GAX-målets namn, och demoversionens könsserie visar uttryckligen **syntetisk**, inte historisk verklig demografi.

Bankartan använder Sätilas OpenStreetMap-rendering. `docs/data/course-display.json` innehåller visningsgeometri från användarens Garmin-export för 2026 och tre återfunna historiska GPX-filer. Kontrollsummor och källor följer med. Exporten innehåller koordinater, höjd och geometriskt beräknad längd. Råa GPX-filer, tidsstämplar, GPX-waypointmetadata och deltagardata ingår inte i den publika byggnaden.

När en årsfil saknas väljs närmaste år, med äldre år vid lika avstånd. AllTrails-spåret har obekräftat år och visas endast i lagerjämförelsen. Plotaroute-spåret från 2021 visas som kandidat för båda 2021-upplagorna, med dokumenterade avbrott som separata delar. 2018-filen och den andra 2021-filen saknas fortfarande bland återfunna original. Identifierade historiska kandidater och årsstatus finns i `docs/data/route-candidates.json`.

2026-exporten har 2 916 punkter i ett sammanhängande GPX-segment. Längsta steget mellan två källpunkter är 1,878 km. Kartan återger arrangörens punktföljd och geometriskt avstånd, med samma förenkling mellan källpunkterna som en vanlig GPX-visare. Referensgeometrin ger inga verifierade historiska stationer eller passager.

Kartduellen knyter manuellt importerad GPX till det valda tävlingsåret och håller den i webbläsarens arbetsminne. De fiktiva löparnas positioner beräknas från simulerade tider.

Verifiering: `tests/test_gax_full_ux_review.py`, `tests/test_gax_gpx_local.py`, `tests/test_synthetic_data.py` och `tests/test_blueprint_contract.py`.

## Verkliga resultat och publiceringsbeslut

Privat källa: `Stayinhealthyrunning/loppanalys-private-data/main:gax100/fresh/gax100.sqlite`. De riktiga **945 posterna**, **651 målgångarna** och **1 838 originalpassagerna** är kvar där.

Viktig kontroll: 2023 års **officiella resultattabell 90 poster / 70 målgångar** gäller.

Innan verkliga deltagaruppgifter kan införas i en senare publik release behövs ett separat beslut och verifierad export via `gax100/privacy_release_gate.py` och `shared_privacy.py` i det privata repot. GAX:s ägarintyg att deltagarna är vuxna är registrerat som ägaruppgift men **är inte en generellt godkänd rättslig grund** för offentlig vidarepublicering. Spärrregister, opt-outs, skyddade identiteter, borttagning av tillhörande observationer och källa/rättighetsfrågor kvarstår.

Det gamla repots historiska GitHub-kopior ligger utanför denna migrering och hanteras separat inklusive supportärende **#4858695**. Radera inte gamla repot innan migrering, test och backups har granskats.

## Manuell verifiering

- `python3 -B tests/test_blueprint_contract.py` kontrollerar alla 14 resultatfiler samt aggregerade numerärer.
- `python3 -B scripts/build_offline_preview.py --docs docs --out preview/index.html` gör ett komplett fristående UI-demosystem.
- `python3 -B tests/test_offline_preview_browser.py --file preview/index.html` provar verklig interaktion i Chromium (Playwright).
- `.github/workflows/quality.yml` kör samtliga bygg-/browser-/privacykontroller vid PR.

Ingen extern lokalkarta eller uppgiven kontrollkilometer ska räknas som verifierad GAX-geometri utan rättigheter och källdata.
