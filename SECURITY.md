# Sikkerhed og data

## Aktuel app

Den aktuelle app er `dist/PKM-UI-V2.2.html`. Samling og importerede billeder gemmes lokalt i IndexedDB, ikke på GitHub eller i Codex. Samlingsfiler indeholder billeder, beholdning og links. De er ikke krypterede. Gem dem i din egen beskyttede mappe og tag en separat backup.

Før en indlæst fil erstatter samlingen, gemmes den gamle samling og den nye i samme IndexedDB-transaktion. Fejl ruller begge ændringer tilbage. Menuen Samlingsfil kan gendanne den seneste kopi; gendannelse gemmer den aktuelle samling som næste kopi. Kun én gendannelseskopi bevares. Slettede browserdata eller diskfejl kan også slette den.

Importerede samlingsfiler valideres for poster, referencer, beholdning, billedtyper og Cardmarket-adresser. En Content Security Policy tillader kun appens indbyggede script via SHA-256, blokerer andre scripts, plugins, formularafsendelse og netværkskald fra scripts. CSS, indbygget font og billeder er tilladt. Eksterne billedadresser hentes fra deres udbyder; Cardmarket åbnes kun ved brugerens klik. Ingen analyse- eller sporingskode.

Browserlager kan variere mellem filstier og browsere. Eksportér fra gammel app og importér i ny. Brug ikke privat browsing som varigt lager. Gem .pkm efter vigtige ændringer; lager-CSV indeholder ikke hele samlingen.

## Serverprototypen

`npm start` starter en ældre prototype, som ikke deler data med HTML-appen. Den lytter kun på 127.0.0.1 og afviser fremmede Host- og Origin-headere. Der er sikkerhedsheadere og transaktioner ved import. Den har ingen login og må ikke eksponeres direkte på internettet eller via en tunnel. Cloudhosting kræver en særskilt løsning med login, HTTPS og serverbackup.

SQLite-filen ligger i `data/catalog.sqlite` eller PKM_DATA_DIR. Stop serveren før filbackup. Overskriv ikke en eksisterende database ved opsætning.

## Kodearkiv og downloads

GitHub indeholder kildekode, offentligt katalog, app og gennemgåede downloadfiler. `.gitignore` udelukker .pkm, databasefiler, eksport-, backup- og uploadmapper samt almindelige nøgle- og miljøfiler. Dette forhindrer utilsigtet tilføjelse; det kan ikke rense en fil, som allerede er i Git-historikken. Del aldrig private data via en pull request, issue eller tvungen `git add -f`.

CI kontrollerer funktioner og sikkerhed, søger efter almindelige hemmeligheder, bygger appen og sammenligner downloadpakken. Actions er fastlåst til commit-SHA og har kun læseadgang.

GitHub-kontoens 2FA, arkivets synlighed og branch protection kan ikke administreres med denne sessions API-adgang. Disse kontroller er ikke blevet aktiveret eller verificeret. Koden og filerne er versionsstyrede, men dette er ikke automatisk backup af din personlige samling.
