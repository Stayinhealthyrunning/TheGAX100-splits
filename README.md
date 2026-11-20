# Gax100 Splits – version 1.3.2

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

Version **1.3 (20 november 2026)** sammanfattar den verkligt publicerade, filtrerade datamängden och de tidigare färdigbyggda funktionerna. Den kompletterar tidigare utveckling med särskild QA för skarpa data, enhetlig versions-/metodinformation och kontroll av att produktionsflödet inte oavsiktligt återgår till demonstration.

GAX100 ligger tills vidare **utanför startsidans lopplista på Loppanalys.se** under granskningen. Det äldre `gax100-analys` bevaras för historik och separat GitHub Support-sanering; dess äldre persondatahistorik ska aldrig återintroduceras i detta rena repo.

Mer detaljer: [Granskning och release](docs/REVIEW_AND_RELEASE.md) · [V1 release notes](docs/V1_RELEASE_NOTES.md).

## Version 1.3 – fasta klockpassager i Replay och Kartduell

- **Kontrollens faktiska registrerade passertid är det fasta ankaret** för respektive löpare i individuell Replay, två-löparjämförelse, Kartduell 2–5 deltagare och korsårsreplay.
- Kontrollens kilometerposition hämtas från den aktuella upplagans årsverifierade km, eller **uppskattas till Magleberg 44, Haväng 80 och Sandhammaren 130 km** när årsvärdet saknas. 2019/2021 har olika km i arrangörens klassrubriker; kartan använder samma tydligt uppskattade 44/80/130 som gemensam visualiseringsaxel, medan källkonflikten visas i tabellerna.
- **En uppskattad kilometer är inte en uppskattad passertid.** Utan verklig tid för en löpare vid en kontroll skapas inget kontrollankare. Mellan den löparens två närmaste verkliga passager visas enbart beräknad position på referensbanan.
- Om året eller löparen endast har Start och Mål visas en **statisk referensbana och verkliga sluttider**, utan animerad deltagarposition eller påhittad mellanplacering. Detta gäller både individuell Replay, Kartduell och jämförelser mellan år.
- Den tidigare koden i `gax100-analys` användes som metodreferens för att återskapa riktiga mellantider även när kilometerfältet är tomt. Detta korrigerar den regressionsbugg som dolde tre kontrollpassager i exempelvis 2024.
- Inga resultatposter, privata register, källpassertider eller insamlade GPS-spår har ändrats. Den nya logiken är beräknings- och presentationskod ovanpå de redan godkända offentliga filerna.
- Originalbilden och den originalverifierade AudioERA/Pixabay-MP3:n från 1.2 fortsätter att användas oförändrade.

Se [metod- och versionsanteckning 1.3](docs/V1_3_RELEASE_NOTES.md) för kontrollankare, motstridiga km, villkoren för interpolation och kvalitetstester.

## Version 1.2 – bild, datatäckning, källkilometer och musik

- Den tidigare tecknade Ales stenar-bilden är ersatt med **originalgenererad fotorealistisk kustbild** med tre traillöpare som springer åt höger. Bilden ligger lokalt i repot under `docs/assets/hero-ales-stenar-trail-runners.webp` och kontrolleras med SHA-256 i Pages-bygget.
- Fotobaserad designprofil, uppdaterad färgsättning, responsiva mobilvyer och banavsnittens bildbehandling ger ett gemensamt uttryck.
- **Tomma dynamikkort döljs helt.** Kvarvarande kort expanderar till full bredd utan hål. Gäller bland annat placeringslyft, sista tredjedelen, relativa segmentdiagram och ålderskort utan faktisk källa. Start–Mål och resultat som har data visas fortsatt.
- Källmärkt **historisk kilometeröversikt** i `docs/data/historical-checkpoint-km.json` hjälper läsaren skilja årsverifierade 44/80/130 km från motstridiga rubriker 2019/2021 och referensavstånd utan årsverifiering 2020/2024. Dessa referenser ändrar **aldrig** officiella passertider, personuppgifter, fysisk segmentfart eller distansberäkningar.
- Separat, begränsad Legends Tracking-undersökning av arrangörslänkade webbplatser för 2024 och 2026: de svarar, men den åtkomliga publika vyn gav inga verifierbara nya stationstider/metadata. Inga identifierare, personpositioner eller spekulativa mellantider importeras.
- **Musiken ingår:** `docs/assets/audio/audioera-acoustic-guitar-happy-637709.mp3` (originalfil, kontrollsumma och filstorlek verifieras). Ljudet används i Replay och Kartduell, kan slås av, har volymreglage och kreditering `Aleh Mikalayeu (AudioERA) · Pixabay`. Spelaren hämtar sin konfiguration från `docs/data/replay-audio.json`, vilket gör den utbytbar utan att ändra analyslogik.
- Oförändrat: 14 historiska upplagor, 945 integritetsfiltrerade resultat och 651 fullföljande. Granskningsadressen ligger separat från Loppanalys.se:s startsida.

Se [versionsanteckningar 1.2](docs/V1_2_RELEASE_NOTES.md) och [1.1](docs/V1_1_RELEASE_NOTES.md).


## Version 1.3.2 – SCB:s fullständiga namnstatistik 2022

**SCB:s slutliga publicerade namnregister**, inte bara topp 100, används nu som en statistisk stödkälla för de redan offentliga GAX-resultat som saknar officiell könsklass. Fyra sexuppdelade tabeller läses ur SCB:s officiella XLSX: tilltalsnamn respektive förnamn för kvinnor och män. Källa: [SCB – samtliga folkbokförda, namn med minst två bärare](https://www.scb.se/hitta-statistik/statistik-efter-amne/befolkning-och-levnadsforhallanden/ovrigt/namnstatistik/pong/tabell-och-diagram/samtliga-folkbokforda--fornamn-tilltalsnamn-och-efternamn-med-minst-tva-barare-uppdateras-ej/samtliga-folkbokforda--fornamn-tilltalsnamn-och-efternamn-med-minst-tva-barare/). Underlaget avser **31 december 2022** och publicerades av SCB 21 november 2024.

- Tidigare 109 uppskattade poster har ersatts/kompletterats till **219** med enhetlig SCB-metod. Av 237 hittills oklassificerade poster är **18** fortfarande oklara.
- Krav: minst **30** registrerade bärare i vanligaste könskategorin och minst **98 %** statistisk övervikt. När namnet saknas på andra könets lista räknas konservativt med att det kan finnas **en** bärare där (SCB:s publiceringströskel är två).
- SCB:s **tilltalsnamn** används i första hand, sedan **förnamn**. Om GAX:s uttryckligen verifierade klasser motsäger en skattning används den inte.
- Detta är en **namnstatistisk uppskattning** och **inte en fastställd uppgift om individens kön**. Alla SCB-uppskattningar är tydligt särskiljda från officiella tävlingsklasser i UI, statistik och metodtext. Tvetydiga och mycket sällsynta namn förblir okända.
- Enbart det publika SCB-aggregatet laddas ned temporärt under GitHub Actions; **ingen individdata sänds till SCB**. Den omfattande XLSX-filen lagras inte i GitHub, och ingen av de 14 filtrerade historiska resultatfilerna ändras.
- Källan är SHA-256-pinnad; publicerade uppskattningar i `docs/data/name-based-classification.json` refererar endast till redan integritetsgodkända resultat-ID:n.
- Läs [detaljerad granskning](docs/SCB_NAME_SOURCE_AUDIT_2026-11-20.md).

## Version 1.3.1 – resultat- och klassificeringsgranskning

- Rättade 2024 års pallplatser. De 54 fullföljande fördelas enligt **officiell DUV/arrangörskälla på 18 i damklass och 36 i herrklass**. Ingen uppgift har gissats från namn för detta resultatunderlag.
- Samtliga 14 årgångar granskas systematiskt mot officiella resultat och slutklockor. **480 fullföljare** har entydiga träffar för officiell tävlingsklass från arrangören/DUV i 2014–2024-källmaterialet.
- Separat rapporterad, **namnstatistiskt UPPSKATTAD** klass har skapats för **109 tidigare oklassificerade offentliga resultat**. För 12 av dessa stödjer svenskavgränsad publik förnamnsstatistik en högkonfidensbedömning (minst 99 % vid minst 50 registerobservationer); övriga 97 bygger på enhällig förnamnsgrupp hos minst fyra *olika* redan källverifierade GAX-deltagare. **128 förblir okända**. Uppskattningen är en statistisk grupp, inte en uppgift om personens faktiska kön eller identitet.
- Individuell sexklass tilldelas aldrig som officiellt faktum på grund av ett namn; varje namnuppskattning har en separat datanyckel och visas alltid som uppskattad i resultatlistan och berörda diagram. Anmälan om felaktig klassificering kan göras via <https://www.loppanalys.se/integritet/>.
- Officiella totalplaceringar och klassplaceringar särhålls. Där en officiell totalplacering inte kan härledas ur en källkolumn, beräknas **total ordningsplacering från officiella sluttider** och får metodbeteckning. Detta påverkar profiler, jämförelser och pallplatser konsekvent.
- De 14 integritetsfiltrerade resultatfilernas originalmanifest ändras **inte**; de två nya publicerade överläggen refererar enbart redan publicerade resultat-ID:n. GitHub Pages-bygget avbryts om en klassuppgift skulle gälla en annan löpare eller övertrumfa officiell klass.

Källor och metoder: <https://statistik.d-u-v.org/> · <https://genderize.io/documentation/api/reference> · [Release notes 1.3.1](docs/V1_3_1_RELEASE_NOTES.md).
