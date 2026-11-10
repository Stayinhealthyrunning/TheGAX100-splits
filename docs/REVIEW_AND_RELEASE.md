# GAX100 – verifierbar granskning och skyddad publicering

## Vad som flyttats till nya repot

Den granskade GAX100/Sätila-frontendens HTML, åtta CSS/JavaScript-resurser, samtliga 14 GAX-upplagor som aggregerade metadata, individdata-tomma JSON-filer och reproducerbara UI-/säkerhetstester.

Utgångsversion: gamla GAX-repot `gax100-analys`, källa **`8bf5fe6f610fda43cb92ac450dd4cf3a3e1f629d`**. Här har **inget gammalt Git-träd, refs, releases eller historik** kopierats över.

## Syftet med GitHub Pages

Här publiceras enbart en **demonstrationsversion**. En enda HTML med **945 fiktiva namn, fiktiva tider och fiktiva kontroller** genereras från syntetiskt testskript. Antalet verkliga GAX-upplagor samt aggregerade resultatantal kommer däremot från kontrollerade källsummor. Den uttryckliga design-demovarningen ska alltid visas.

Första aktivering av Pages måste ske av repoägaren via `Settings → Pages → Source: GitHub Actions`. Det automatiska flödet `.github/workflows/pages.yml` skapar sidan endast efter automatiskt godkänt källskydd.

## Designgranskning och tid-/GPX-proveniens

Efter genomgången den 10 november har sidan ett kortare analysflöde: fyra naturskildringar samt stationer öppnas i pop-up, alla större sektioner har metodinformation, klassfördelningen ligger under Start till mål, och Delsträckor + Personlig loppplan delar en sektion med två lägen. Starkaste avslutningen accepterar GAX-målets namn, och demoversionens könsserie visar uttryckligen **syntetisk**, inte historisk verklig demografi.

Arrangören länkar från https://gax100.se/bana-karta/ till sin 2026-kurs på Garmin. Detta är en officiell **källhänvisning**, inte en licensierad, kopierad GPX-fil i denna repo.

Det gamla GAX100-projektet dokumenterade fem tekniskt analyserade men *inte publiceringsklara* GPX-filer i `GPX_COVERAGE.md` och `data/gpx-audit.json`. Ursprungliga binära/XML-filer fanns enbart i ett ignorerat lokalt råarkiv. De har **inte** flyttats till detta repo och finns inte heller i det anslutna privata `loppanalys-private-data`. Vi har enbart portat historisk **metadata och källänkar** till `docs/data/route-candidates.json`, inklusive kontinuitetsavbrott och skillnaden mellan officiell 2026-kurs och icke-officiella kandidatspår.

2021-A/B kan ännu inte knytas var för sig till rätt kandidat. 2018 och vissa 2021-filer innehåller stora spårglapp, och den publika GPX-inläsningen avvisar större glapp i stället för att uppfinna geometri.

Kartduellen tillåter tillfällig GPX-inläsning **enbart lokalt** och knyter filen till valt tävlingsår. Inga ruttkoordinater uppladdas, lagras i Pages eller är tillgängliga efter sidomladdning. Kartduellens fiktiva löpare interpoleras längs vald bangeometri, inte utifrån verkliga GPS-loggar.

Verifiering: `tests/test_gax_full_ux_review.py`, `tests/test_gax_gpx_local.py`, `tests/test_synthetic_data.py`, `tests/test_blueprint_contract.py`. Inga skyddade resultat eller tredjeparts-GPX ingår i körningarna.

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
