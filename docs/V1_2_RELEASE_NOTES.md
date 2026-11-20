# Gax100 Splits – version 1.2

**Publiceringsmål:** https://stayinhealthyrunning.github.io/TheGAX100-splits/  
**Datum:** 20 november 2026  
**Grund:** integritetsfiltrerad version 1.1, 14 upplagor 2014–2026.

## Bild och design

Ny, originalgenererad 1200×513 WebP (rasterbild med fotografiskt uttryck) visar Ales stenar, kust och tre traillöpare på väg åt höger. Bilden är en artistisk tolkning, **inte ett dokumentärt fotografi** eller en historisk tävlingsbild. Den lagras lokalt i GitHub och kopieras endast när SHA-256 `1df7031ed35634b7170a584d8bdc4c5e77958dceddfc451a830eecd3d9c73070` överensstämmer. Stilmallen använder samma kustfärger, bild- och kontrastsättning i hero och etappsektionen med responsiva format.

## Data utan tomma kort

Dynamiska moduler som saknar verkligt källunderlag döljs helt; syskonkort tar full bredd när endast ett kort kan visas. Reglerna baseras på observerade placeringar, registrerade kontrollpassager och kartstatistik. Även ålder döljs när fältet saknas helt. När endast målpassage finns behålls Start→Mål, sluttider och resultat. Inga mellanpassager eller placeringar uppfinns.

## Historiska km som är källbelagda

| Upplaga | Magleberg | Haväng | Sandhammaren | Typ och källa |
|---|---:|---:|---:|---|
| 2014–2018 | 44 | 80 | 130 | Arrangörens årsspecifika resultatlista |
| 2019 | 43/44 | 79/80 | 130/131 | Motstridiga dam-/herrrubriker; ingen unik årskilometer |
| 2020 | ≈44 | ≈80 | ≈130 | Ej årsverifierad referens från angränsande upplaga |
| 2021-A/B | 43/44 | 79/80 | 130/131 | Motstridiga klassrubriker; ingen unik årskilometer |
| 2022–2023 | 44 | 80 | 130 | Arrangörens årsspecifika resultatlista |
| 2024 | ≈44 | ≈79 | ≈131 | Arrangörens senare stationsreferens, inte verifierade kilometer för 2024 |
| 2025–2026 | – | – | – | Endast målpassager i nuvarande integritetsfiltrerade publicering |

Källor: [2014](https://gax100.se/resultat/resultat-2014/), [2015](https://gax100.se/resultat/resultat-2015/), [2016](https://gax100.se/resultat/resultat-2016/), [2017](https://gax100.se/resultat/resultat-2017/), [2018](https://gax100.se/resultat/resultat-2018/), [2019](https://gax100.se/resultat/resultat-2019/), [2021](https://gax100.se/resultat/resultat-2021/), [2022](https://gax100.se/resultat/resultat-2022/), [2023](https://gax100.se/resultat/resultat-2023/), [2024](https://gax100.se/resultat/resultat-2024/), [arrangörens stationsuppgifter](https://gax100.se/information/). Skillnader mot aktuell reptidstabell och 100 miles nominell distans ska inte tolkas som olika officiellt uppmätta historiska banlängder.

Denna metadata är en **separat läsresurs**. De 14 signerade SHA-256-refererade resultatfilerna har inte ändrats. UI:t visar `årskälla`, `källkonflikt` respektive `referens, ej årsverifierat`. En osäker kilometer används aldrig för kilometerfart, GPX-position eller officiell passage.

## Legends Tracking

Officiell användning bekräftad i arrangörens information och 2024-nyhet. En isolerad Chromium-granskning mot `gax100.legendstracking.com` och `gax100-2026.legendstracking.com` visade HTTP 200 samt webbapplikationsresurser, men **inga publikt verifierbara checkpointnamn eller källrader** vid testtillfället. Resultatet ger inte stöd för att importera ytterligare löparpositioner, checkpoint-tider eller GPS-spår. Separat kontrollscript: `tests/research_legends_public.py`; loggarna innehåller enbart känt kontrollnamn/kategoriflaggor, aldrig personuppgifter.

## Musik och upphov

Lokal MP3 i `docs/assets/audio/audioera-acoustic-guitar-happy-637709.mp3`, 4 065 071 byte. SHA-256 kontrolleras mot `ed089921eb56654ab4c97025c5ceebd057e6c739a9d3f15328033dc909d09e49`. Upphov: Aleh Mikalayeu, AudioERA, via Pixabay. Krediteras diskret i replayvyn. Utbytbart ljud anges endast i `docs/data/replay-audio.json`; vid byte ska en ny licens- och filintegritetsgranskning göras. Browser autoplay före användarklick förekommer inte.

## Publiceringsgrind

`tests/test_production_contract.py` verifierar grundmanifestet, originalbild, exakt MP3 och 14-års metadata. `tests/test_production_browser.py` kontrollerar bildavkodning, HTTP-servat ljud, källtäckning, källkonflikter, kompakt kortlayout, mobil/desktop, profiler och jämförelser. `scripts/build_pages.py` är den enda vägen till Pages. Slå samman och publicera först efter grön CI för exakt commit; kontrollera dessutom att slutlig Pages-körning lyckas.

**Integritet:** noindex/nofollow och opt-out/publiceringsgrind bevaras. Inga skarpa tilläggsdata från Legends utan verifierad rättighets- och datakvalitetsprocess. Sidan finns ännu inte på Loppanalys.se:s startsida.
