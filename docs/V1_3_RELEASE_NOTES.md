# Gax100 Splits 1.3 – källförankrad kartjämförelse

**Granskning:** https://stayinhealthyrunning.github.io/TheGAX100-splits/  
**Datum:** 20 november 2026  
**Underlag:** oförändrade integritetsfiltrerade resultat för 14 upplagor.

## Tidsankare

För varje löpare används Start som tidsnoll, varje faktiskt registrerad kontrolltid (EQ TIME) som ett eget fast tidsankare och officiell måltid för fullföljare. Kontrollerna Magleberg, Haväng och Sandhammaren får årskontrollerade distanser där de finns. När årskilometer saknas använder kartan **44, 80 och 130 km, uttryckligen uppskattade** med utgångspunkt från andra års officiella resultat. Källkonflikter 2019/2021 redovisas som 43/44, 79/80 och 130/131 km i tabeller; kartans visningsankare för dessa år uppskattas konsekvent till 44/80/130.

Kilometeruppskattningen **ger aldrig en uppskattad kontrolltid**. Om en löpare saknar en registrerad passage vid en viss kontroll får den kontrollen inte användas som ett eget tidsankare. Rörelsen mellan närmast föregående och nästa verkliga tid interpoleras endast som en illustrativ position på en tydligt angiven GPX-referensbana, inte som faktisk deltagar-GPS.

År eller löpare utan mellantider använder en separat, tydligt märkt Start–Mål-illustration utifrån officiell sluttid. Den metoden visar inga verifierade mellanplaceringar och får inte beskrivas som checkpointförankrad.

## Funktioner

- Individuell profil: källa, ackumulerad kontrolltid och riktiga segmenttider visas även när kontroll-km saknas i den ursprungliga årsfilsmetadata.
- Replay, direktjämförelse och Kartduell 2–5 löpare: verkliga passertider styr var deltagarna befinner sig vid en gemensam tävlingsklocka; olika löpare kan ha olika antal faktiska passager.
- Jämförelser mellan år: separata årsvisningsrutter, endast deltagarnas verkliga tidpunkter och källmärkta referens-km.
- Ingen ändring i publicerade resultat- eller GDPR-filer; original MP3 och fotorealistiska huvudbilden från version 1.2 är oförändrade.

## Årsmatris

| År | Kartans kontroll-km | Tidskälla |
| --- | --- | --- |
| 2014–2018 | 44 / 80 / 130, årskälla | Verkliga passager |
| 2019 | ≈44 / ≈80 / ≈130, uppskattat; källkonflikt separat | Verkliga passager |
| 2020 | ≈44 / ≈80 / ≈130, uppskattat | Verkliga passager |
| 2021-A och 2021-B | ≈44 / ≈80 / ≈130, uppskattat; källkonflikt separat | Verkliga passager |
| 2022–2023 | 44 / 80 / 130, årskälla | Verkliga passager |
| 2024 | ≈44 / ≈80 / ≈130, uppskattat; banförändringsreservation | Verkliga passager |
| 2025–2026 | Ingen känd mellankontrollposition i publik timing | Endast måltid |

## Verifiering

GitHub Actions kvalitetsgrind kör både datakontraktet och Chromium-test av faktiskt stegade GitHub Pages-filer. Testerna ska säkerställa att 2021/2024:s kontrollpassager åter visas, att uppskattade km inte förväxlas med källverifierade km och att åren 2025/2026 aldrig får fiktiva kontrollankare. Release godkänns först efter grön CI och godkänd Pages-driftsättning.

**Integritet:** nuvarande källmanifest, personuppgiftsfilter, noindex och separat granskningsadress bibehålls.
