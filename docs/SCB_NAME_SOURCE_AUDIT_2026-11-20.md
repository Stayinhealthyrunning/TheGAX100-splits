# SCB:s namnstatistik – källgranskning för Gax100 Splits 1.3.2

**Datum:** 20 november 2026. **Omfattning:** 14 integritetsfiltrerade GAX100-upplagor (2014–2026), 945 publicerade resultat.

## Verifierad datakälla

SCB:s sista offentliggjorda **heltäckande** fil över namn med minst två registrerade bärare, [samtliga folkbokförda – förnamn, tilltalsnamn och efternamn](https://www.scb.se/hitta-statistik/statistik-efter-amne/befolkning-och-levnadsforhallanden/ovrigt/namnstatistik/pong/tabell-och-diagram/samtliga-folkbokforda--fornamn-tilltalsnamn-och-efternamn-med-minst-tva-barare-uppdateras-ej/samtliga-folkbokforda--fornamn-tilltalsnamn-och-efternamn-med-minst-tva-barare/), senast publicerad 21 november 2024. Befolkningsreferensen är **31 december 2022**. SCB upphörde därefter att producera och uppdatera namnstatistik (se [Namnstatistik](https://www.scb.se/be0001)).

Webbläsaren läser inte SCB. En isolerad, tillfällig GitHub Actions-körning hämtar filen från **SCB direkt**, utan att skicka GAX100-namn eller persondata. Båda tilltalsnamnstabellerna och båda förnamnstabellerna jämförs med varandra; efternamn ignoreras. Den officiella XLSX-versionen är låst till SHA-256 `b099822f53baf393fc0dba8b2c8665b7475c3b2001b6efbbe1d96525709792e4`.

SCB-tabeller som faktiskt lästs ur filen:
- Tilltalsnamn kvinnor: **57 781** namnrader
- Tilltalsnamn män: **49 400** namnrader
- Förnamn kvinnor: **91 243** namnrader
- Förnamn män: **79 124** namnrader

## Beslut och trösklar

1. **Officiell källa har alltid företräde.** Arrangörens/DUV:s verifierade dam- och herrklasser för 480 fullföljare ändras inte.
2. Statistiken används bara för poster som redan är offentliggjorda och saknar verifierad klass. Det är **kategorin som namnet oftast förekommer i**, inte den individuella löparens kön eller könsidentitet.
3. Minst **30** bärare i den dominerande kategorin samt minst **98 %** konservativ frekvensdominans krävs.
4. SCB publicerar bara namn med minst två bärare. När samma namn inte finns i den andra könstabellen beräknas sannolikheten med **en antagen bärare i den tabellen**, inte noll.
5. Tilltalsnamn används först. Förnamnstabellen är reservkälla. Om uppgifterna ger motstridiga starka signaler klassificeras inte namnet.
6. En namnstatistisk uppskattning som motsäger en explicit verifierad GAX-könsklass för samma förnamn hålls utanför.
7. Inga könsklasser utifrån familjenamn, profilbilder, personliga konton eller associationer. Inga födelseår, medelåldrar, nationella identifikationsnummer eller personliga uppgifter från SCB följer med.
8. Varje uppskattning är märkt `scb_tilltalsnamn_population_2022` eller `scb_fornamn_population_2022` och visas som **namnstatistiskt uppskattad**, aldrig officiellt verifierad.

## Sammanställning

| Resultat | Antal |
|---|---:|
| Tidigare uppskattade poster | 109 |
| Efter SCB-granskning | **219** |
| Ytterligare poster med konservativt namnstöd | **110** |
| Matchade via tilltalsnamn | 217 |
| Matchade via förnamn som reserv | 2 |
| Fortfarande utan säker namnstatistisk uppskattning | **18** |
| Därav ej listade i SCB:s statistik | 4 |
| Därav otillräcklig eller oklar statistisk övervikt | 14 |

*I denna sammanställning avses tidigare oklassificerade offentliga resultat, inklusive DNF/DNS. Officiell könsklass kan saknas för ett resultat även om namnets frekvensfördelning är tydlig. Statistik kan inte fastställa en enskild persons kön.*

## Säkerhet och reproducerbarhet

Analysen ligger i `scripts/enrich_scb_first_names.py`, uppspelad via `.github/workflows/scb-name-aggregate.yml`. Källfilen laddas ned till en temporär plats på GitHub-runnern och **ingår inte i projektets Git-historik**. Endast `docs/data/name-based-classification.json` uppdateras, med samma publicerade resultat-ID, klassificeringens bevismetod och stödantal/sannolikhet. De 16 tidigare GDPR-granskade källfilerna och deras SHA-256-release-manifest är orörda.

En namnstatistisk uppskattning får inte gå före verifierad tävlingsklass, ändra officiell resultatplacering eller användas som grund för faktisk individuell könsidentitet. Återstående fall är avsiktligt okända.

## Regressionskontroller

- `tests/test_scb_name_methodology.py` testar bortfall av motsatt könskategori, jämn fördelning och datakontrakt.
- `tests/test_production_contract.py` samt `scripts/build_pages.py` avvisar oidentifierade publicerings-ID:n, kolliderande officiella klasser och uppskattningar under tröskelvärdena.
- GitHub Actions testar den faktiska publicerade sidan i Chromium efter validerad byggning.
