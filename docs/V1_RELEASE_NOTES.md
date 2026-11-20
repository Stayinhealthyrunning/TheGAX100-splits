# GAX100 Analys – versionsanteckningar 1.0

**Datum:** 20 november 2026  
**Granskningsadress:** https://stayinhealthyrunning.github.io/TheGAX100-splits/  
**Publiceringsmål:** GitHub Pages för separat granskning; ingen post på loppanalys.se:s startsida.

## Omfattning

14 officiella upplagor (2014–2026; 2021-A/B separat), 945 resultat, 651
fullföljande. Publik release innehåller 2 482 tidsposter i 14 årsfiler.
Detta ska skiljas från 1 838 ursprungliga källobservationer i det privata
källarkivet: offentlig export representerar även vissa officiella sluttider
som målkontrollpassager. För 2025 och 2026 publiceras endast målkontroller,
inte uppfunna mellankontroller.

## Funktioner i 1.0

- Sök- och resultatarkiv, profiler, officiella källpassager, resultatstatistik,
  historik och två-löparjämförelse där tidsunderlaget medger det.
- Delsträckelabb samt personlig loppplan i ett gemensamt avsnitt.
- Tillgänglig popup för fyra orienterande banavsnitt och stationer.
- Bankartor med närmaste dokumenterade år som tydligt märkt *referens*,
  zoom, individuell replay och Kartduell med modellberäknade positioner.
- Integritetstext och tillgänglig kontaktväg enligt Loppanalys.se.

## Hårda releasevillkor

1. Ett exakt 16-filigt SHA-256-manifest (14 loppfiler + bootstrap och
   coverage) ska överensstämma med samtliga publicerade resultatfiler.
2. Årsnycklar, statusar, namn på tillåtna publicerade rader, unika
   result-ID:n, mål- och passertider samt alla referenser ska valideras.
3. Källidentifierare/åldrar får inte följa med; privata källor,
   rå-GPX och GDPR-register får inte ingå i det publika byggsteget.
   Officiellt rättighets- och opt-out-beslut ligger uppströms i den
   privata exportprocessen, inte i det publika repot.
4. `noindex,nofollow`, `robots.txt` och kontakt till integritetssidan
   ska bevaras.
5. Både kvalitetsworkflow och publiceringsworkflow ska köra skarp
   Chromium-granskning av de **stegade produktionsfilerna**, inklusive
   mobil/desktop, löparprofil och jämförelse, innan Pages kan distribuera.

## Metodgränser som kvarstår efter 1.0

- Historisk fysisk kilometertakt och exakta GPS-löparpositioner stöds
  inte utan verifierat årsunderlag. Banöverlagringarna är märkta
  referenser, inte deltagarnas GPS-spår.
- Officiell timingtäckning varierar avsevärt per år.
- Årsvisa könsdiagram visas endast när källan har tillräcklig täckning.
- Detta är en separat, offentlig granskningssida; den är inte
  länkad från Loppanalys.se:s startsida.
- Ett `noindex`-direktiv minskar sökindexering men skyddar inte
  mot direktåtkomst till offentliga resultatfiler.

## För verifiering

`python3 -B tests/test_production_contract.py`  
`python3 -B scripts/build_pages.py --docs docs --out production-check`  
`python3 -B tests/test_production_browser.py --site production-check`

Dessa utförs av GitHub Actions i releaseflödet. De ger aggregerad
teststatus och skriver inte deltagaridentiteter i loggar.

Tidigare saneringsärende för `gax100-analys` och GitHub Support är
separat och ska inte återintroduceras genom historikimport.
