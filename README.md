# PKM · Samlingskartotek

[**Download app og Cardmarket-fil**](DOWNLOADS.md) · [Sikkerhed og backup](SECURITY.md)

Projektet udvikles i Codex og er knyttet til GitHub-repositoriet `jbelmbaek-ctrl/PKM`. Koden i arbejdsområdet og filer på GitHub er forskellige ting: kun en Git-push overfører ændringer til GitHub.

## Aktuel app: UI V2.3

Den aktuelle app er en enkelt HTML-fil med topnavigation, japansk setbibliotek, fælles billeder pr. kort, beholdning pr. version/stand/lokation, lager-CSV, historik, fortrydelse og Cardmarket-links.

Byg fra projektmappen:

```sh
python3 standalone/build.py
```

Den færdige fil gemmes i `dist/PKM-UI-V2.3.html`. Byggeren laver også en kopi i `/tmp` til chatlevering. Åbn HTML-filen i en almindelig browser på din egen computer; appen kræver ingen installation eller server. Font og setbibliotek følger med filen.

## Projektets mapper

- `standalone/`: kildekode, katalogdata, font, licenser og browsertests til den aktuelle app.
- `dist/`: færdige appfiler, som kan gemmes og distribueres sammen med projektet.
- `exports/`: lokale eksportfiler, der er lavet til brugeren. De uploades ikke automatisk til GitHub.
- `public/`, `server.js`, `test/`: den tidligere serverprototype og dens tests. Den har separat SQLite-lager og er ikke den aktuelle UI V2-app.

## Hvor gemmes samlingen?

Den aktuelle app gemmer kort, billeder og beholdning i browserens IndexedDB. En samlingsfil (`.pkm`) indeholder alle disse data og kan indlæses på en anden computer. Gamle JSON-backups understøttes også. Browserdata flytter ikke automatisk med kode eller nye HTML-filer.

Codex-arbejdsområdet er udviklingsmiljøet. GitHub er til kode og versionshistorik. Ingen af delene er automatisk et fælles online lager til din beholdning. Gem samlingsfiler uden for Git; `.pkm`-filer er ignoreret af projektet.

## Senere cloudhosting

En fælles app til computer og telefon kræver login, en fælles database og et billedlager med backup. Den nuværende HTML-fil kan hostes statisk, men det synkroniserer ikke dens browserdata. Cloudversionen er endnu ikke implementeret eller deployet.

## Kontrol

Byg appen og kør de dokumenterede Playwright-browsertests mod en lokal testserver; se `standalone/README.md`. De kontrollerer import, billeder, Cardmarket, lagerarbejde, samlingsfiler og responsiv UI. Syntetiske testdata indgår ikke i den leverede HTML.

Den tidligere serverprototype kræver Node.js 24 og kan separat startes/testes med `npm start` og `npm test`. Dens database gemmes i `data/catalog.sqlite` og ignoreres af Git.

## Kontrol og pakning

Node.js 24+ og Python 3.12+ kræves til udvikling. Appen har ingen npm-afhængigheder.

```sh
python3 -m pip install -r standalone/requirements-test.txt
python3 -m playwright install chromium
python3 standalone/build.py
npm test
python3 standalone/run_browser_checks.py
python3 scripts/audit_project.py
python3 scripts/package_release.py
```

`downloads/` indeholder kun gennemgåede udgivelsesfiler; `exports/`, `private/`, `backups/` og `data/` må ikke uploades. GitHub-workflowet gentager kontrollerne og verificerer, at downloadpakken svarer til koden.

Setimport opretter først data på det femte trin: vælg sets, kontrollér kort, tilføj billeder, tilføj Cardmarket-links, kontrollér og gem. CSV matches mod de endnu ikke oprettede kort og deres versioner. Rækker med fejl kræver rettelse eller et udtrykkeligt valg om at springe dem over. Sets, billeder og links gemmes samlet.

## PKM 2.3: katalog og lager

- **Import → Opdatér eksisterende sets** eller **Sets → Opdatér katalog** viser ændringer før gemning. Manglende oplysninger udfyldes; nye kort og versioner tilføjes. Brugerrettede kortnavne og beholdning bevares. Erstatning af billeder eller links vælges særskilt.
- **Fortsæt kladde** genoptager bibliotekvalg, egne filer, billedmatches og rettede CSV-rækker efter navigation eller genåbning i samme browserlager. Kladden er adskilt fra samlingen.
- **Katalogkontrol** åbnes fra setstatus eller overblikket. Filtrér manglende billeder, versionslinks, usikre navne/versioner og kortnummerkonflikter.
- **Samlemål** vælges som standard og kan ændres pr. set: ét af hvert kort eller ét af hver version. Mangler, dubletter og målets fremdrift følger valget. Kort, versioner og fysiske eksemplarer vises særskilt.
- **Lager** samler ens kombinationer af version, stand og lokation. Søg på tværs af kort, setkode, version, stand og lokation. Flyt/fjern flere grupper eller redigér et samlet antal, med fortrydelse.
- **Lokationer** viser antal eksemplarer, kort, versioner og grupper. Åbn indhold eller omdøb uden at ændre lokations-ID.
- **Registrér antal** åbner en formular med senest anvendt lokation/stand og tastaturstøtte.
- **Eksport** af lager, mangler og dubletter medtager setkode og gemte Cardmarket-links. Lager-CSV grupperer på samme måde som skærmen. Samlingsfiler indeholder også mål og registreringsvalg.

De nye integrationstests dækker genåbning af kladder, rettelse af linkfejl, databevarelse ved opdatering, eksplicit erstatning, gentaget import, lager/CSV-antal, gruppeændringer/fortrydelse, globale og individuelle mål samt backup med billeder og indstillinger.
