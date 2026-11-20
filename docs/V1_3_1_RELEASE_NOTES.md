# Gax100 Splits 1.3.1 – resultatkvalitet och könsklassificering

**Datum:** 20 november 2026  
**Syfte:** Rätta tomma pallplatser, återskapa källbelagda könsklasser och granska alla 14 resultatupp­lagor.  
**Granskningsadress:** https://stayinhealthyrunning.github.io/TheGAX100-splits/

## Grundorsak och lösning

I 2024 års publicerade grunddata finns 54 målgångar, men sex/könsklass saknas för samtliga, och `place=1` förekommer hos både dam- och herrvinnare eftersom kolumnen avsåg **klassplacering**, inte gemensam totalplacering. En äldre rapportkomponent tolkade frånvaron av `sex` som att **ingen** verifierad pallprestation fanns, vilket var fel.

En explicit publicerad DUV/arrangörstabell gav 54 entydiga namn-och-måltidsmatchningar: **18 damklass, 36 herrklass**. Detta är källverifierat och används för verkliga könsvisa topp tre, inte namnstatistik.

Hela offentliga historiken granskas därefter med samma metod. Resultatet blir 480 entydiga källträffar för publicerade fullföljare från 2014–2024. Ofullständigt matchade rader lämnas utan källklass, i stället för att tilldelas ett påstått officiellt kön.

## Namnbaserad komplettering på uttrycklig beställning

Säkert källmatchade uppgifter skiljs från **en separat, tydligt märkt namnstatistisk uppskattning**. Programmet undersöker enbart unika **förnamn** – aldrig fullständiga namn, startnummer, klockslag eller resultat-ID:n – hos en namndatabas med Sverige som sökland. Kriterierna för extern källa är **minst 99 % namnassociation** och **minst 50 namnobservationer**. När en sådan källa saknas kan minst **fyra olika namn med redan officiellt verifierade GAX-klasser** ge en uppskattning, men bara om hela den kontrollerade gruppen har samma klass och ingen källa säger motsatsen.

Detta ger **109 namnuppskattade resultat** (12 externa högkonfidensobservationer, 97 styrkta av upprepade officiellt klassade förnamn). **128 resultat har fortsatt okänd grupp**, och uppgifter om faktiskt individuellt kön/könsidentitet har inte infererats som faktum. Uppskattningarna avser bara en **statistisk kategorisering** av förnamn och kan vara fel, särskilt för internationella och könsneutrala namn. Binär namnstatistik täcker inte icke-binära könsidentiteter.

**Förhindrad sammanblandning:**
- Källverifierad sexklass lagras separat från namnuppskattning.
- De 14 integritetsfiltrerade, oförändrade ursprungliga `races/*.json` är fortsatt enda sanningskällan för resultat, tider och deltagar-ID:n.
- Ingen namnuppskattning får ersätta en officiell klass, skapa en ny deltagare, ange ålder, eller introducera ett nytt register-ID.
- Namnuppskattade grupper märks i resultat, profiler, könsfördelningar och procentberäkningar. En uppskattad könsplacering visas `≈#`, inte som officiell klassplacering.
- Rättelse och avpubliceringsprocess enligt Loppanalys integritetssida.

Källor: arrangörens [2024-resultat](https://gax100.se/resultat/resultat-2024/), [DUV-statistik för 2024](https://statistik.d-u-v.org/getresultevent.php?event=104698), [Genderize API-dokumentation](https://genderize.io/documentation/api/reference). Tjänstens sannolikheter gäller förnamnsstatistik, inte personlig könsidentitet.

## Resultat- och placeringsintegritet

- Ursprungliga källplaceringar bevaras som `source_reported_place`.
- `overall_place` beräknas från verkliga sluttider vid behov, med tidslika målgångar hanterade som lika placering när källan inte avgör ordningen.
- `class_place` får en egen metodkod för verifierad DUV-klass, klasskolumn från arrangören eller komplett verifierad klasskohort.
- För rader utan officiell könsklass får ingen namnuppskattning skapa en **officiell** klassplacering.
- Samma funktionalitet konsumeras av pallmodul, profil, filter och historiska diagram.

## Kvalitet och publicering

`scripts/build_pages.py` verifierar 16 oförändrade releasefiler, 14-års källmatchning, alla publikreferenser och felaktigt överskrivande data. `tests/test_production_contract.py` kontrollerar käll- och namnuppskattningsöverläggen. `tests/test_production_browser.py` verifierar att **2024 års båda pallplatser** visas med sex verkliga topp tre-placeringar, rätt 18/36-källantal samt att profilsidan, km-referenser, Replay och Kartduell fortfarande fungerar.

De nya överläggen har enbart opaka resultat-ID:n och metodfält. GDPR-sidans information har kompletterats med rättelse och information om namnstatistik. Live-versionen hålls separat från Loppanalys.se:s startsida.

## Kvarvarande begränsningar

- För 2025–2026 finns endast officiell måltid i det redan publicerade tidtagningsunderlaget: **ingen** animerad kontrollbaserad kartposition uppfinns.
- 128 offentliga resultatrader är fortfarande oklassificerade; det är avsiktligt när namnkällorna är för osäkra.
- Källor kan ha klass- och rankingavvikelser som bara officiell resultatkorrigering kan avgöra.
