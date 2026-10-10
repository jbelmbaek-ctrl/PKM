# Downloadable PKM v4

Build the single-file app with `python3 standalone/build.py`. Output: `/tmp/PKM-v4.1.html`. Open in a modern browser; no installation is required.

## Japanese set import

The file contains a gzip-compressed snapshot of 128 Japanese sets and 13,765 cards from TCGdex. Choose **Set-import**, search by English name, Japanese name, set code or series, select one or more sets and review before importing. Variant names can be changed before commit. The set and all its cards are imported atomically. Duplicate source sets are blocked. CSV/JSON can import additional custom sets together.

The built-in catalogue works offline. Images are optional external links from TCGdex or local uploads. External image availability has not been verified in this cloud environment; broken images fall back to placeholders. Card-image copyright is not transferred by the dataset license. Some source card names/variants are absent; these are flagged in the preview, with numbered placeholder names or a Normal default. This snapshot does not claim to cover all Japanese sets.

TCGdex source: https://github.com/tcgdex/cards-database at commit `4199850a6af49665db0080fa2bb9ef751750a406`. MIT attribution is included in the HTML and TCGDEX-LICENSE.txt. To reproduce the catalogue, obtain that exact source checkout and its `scripts/utils-data/jp_set_translations.ts`, then run `node standalone/import-data.mjs SOURCE_DIR JP_SET_TRANSLATIONS JP_CARD_TRANSLATIONS standalone/english-species.json`. The card catalogue is not populated in the user's collection until they confirm an import.

## Collection and storage

Data and uploaded images are in IndexedDB, separate from the HTML file. Use **Gem backup** regularly. The existing `pkm-backup-v1` JSON format is supported for restoring earlier collections. Browsers may isolate storage by HTML file path, so save a backup in the old version and restore it in the new version if needed.

Gallery +/− changes only the selected variant, condition and location shown in **Hurtig registrering**. Total ownership/progress is across all conditions and locations. Writes are serialized to prevent lost concurrent increments.

Inventory CSV is semicolon-separated UTF-8 with BOM for Danish Excel, covering set, game, year, card number, name, variant, condition, quantity and location. Formula-like text is escaped. Export all stock or only filtered stock.

Image imports match filename stem to card number, normalizing numeric leading zeros. Ambiguous and duplicate matches are excluded. Images are resized to 700 px maximum and saved as JPEG. Batches commit atomically.

## Validation

`node --check /tmp/pkm-standalone.mjs` checks the combined script after building.

For browser checks, serve `/tmp` locally and run `PKM_TEST_URL=http://127.0.0.1:3403/PKM-v3.html python3 standalone/browser_check_v4.py` (requires Python Playwright and Pillow, system Chromium). Tests exercise actual import, version edits, counters, CSV export, rollback on conflict, multi-set CSV, pictures, backup, persistence and mobile layouts. The cloud browser policy blocks file:// navigation, so automated checks serve the same HTML locally. This does not establish a public preview or deployment.


## Version 4

Names use English (Japanese) where the English name is available. The TCGdex set translations are supplemented by PokéAPI species names, conventional owner/region/edition names and curated trainer translations. The PokéAPI BSD license is included in POKEAPI-LICENSE.txt and the generated HTML. 4,105 of the 13,765 source card records still lack an English translation (including records without a usable Japanese name); these display an explicit untranslated-card label and can be corrected in the import preview. No missing name is silently presented as verified.

Names in older backups are upgraded when a reliable source set/card match is available; internal IDs, images and holdings are preserved. Custom English names are preserved. Set codes are editable on Sets; catalogue imports populate them automatically. The main image import accepts a mixed directory with names such as SV7-001.jpg. It matches set code and normalized number, reports unknown/ambiguous/duplicate entries and confirms overwrites before saving. Single-set image import remains available.

Mass registration saves selected card versions together with shared condition and location, adding quantities to existing stock. Filter changes retain pending quantities. Invalid batches roll back fully.

Separate Duplicate and Missing lists have CSV exports. Missing can mean either an absent unique card or an absent specific version. Duplicate quantities deduct one retained copy per version, preferring the best condition; this is a report calculation and never changes actual stock. The overview shows unique-card completeness and all-version completeness separately.

After set/card/image imports and mass registration, a nonblocking backup reminder offers the existing JSON backup download. Browser checks cover restoration of a legacy Japanese-only backup, identity preservation, cross-set images and ambiguity handling, mass rollback, duplicate and missing reports, backups and mobile layout.

## Image import 4.1

One image import replaces the two different import sections. Set-prefixed filenames auto-match; bare numeric files require an explicitly selected set. Every selected file gets a diagnostic, including unsupported formats and empty MIME metadata. Local raster images use FileReader instead of blob URLs, with 15-second read/decode deadlines. Saving has a transaction deadline. Failed decode batches preserve existing images; no partial image batch is saved. Progress identifies the current file, and errors appear in the import panel. Browser checks in browser_check_images.py validate successful saves and subsequent gallery rendering, blank MIME types, invalid files, a simulated hung decoder and preserved stock/image state. The exact cause on the user's machine was not reproduced; this version hardens the reported hanging save flow.

## Import status 4.2

Metadata imports explicitly report local-image and external-link counts and provide a direct image-import button. The catalogue reports locally stored image counts for the selected set. Image-save confirmation checks IndexedDB contents after the write, before the image-import success result. Local image decode, stored-state verification, gallery rendering and reload were tested in Chromium.

## Version 5

Build with `python3 standalone/build.py`; output: `/tmp/PKM-v5.html`.
The standalone HTML opens directly in a modern browser. No server or installation is required for users.

Five primary workspaces: overview, sets, collection, locations, import. Collection includes stock export, duplicate/missing/wishlist reports, mass registration and history.
Set import stages catalogue data, allows name/version review, then stages local images and commits the whole set package atomically. Image filenames support full Japanese set codes including SV1S and SV1V. Every file has a thumbnail and editable card match. Unsupported files remain unselected; duplicate targets block saving. Existing images require replacement confirmation. Image decoding is bounded, with no writes on decode failure. Writes use IndexedDB; image saves are read back before reporting success.

The `.pkm` collection file contains embedded local images, stock and history. Legacy `pkm-backup-v1` JSON files remain readable. Restore validates IDs and foreign keys and resets the undo stack. Browser storage remains the working copy; keep collection files outside the browser. External image URLs still require internet and are not embedded automatically.

Source names and version suggestions are visibly distinguished from missing data, manual edits and user-checked data. English translations are incomplete in the source. Corrections are protected from catalogue name upgrades. Stock history retains snapshots of the last 20 stock changes for undo; images/catalogue imports are not stock undo operations.

Validation: `python3 standalone/browser_check_v5.py` runs a Chromium end-to-end workflow against a local HTTP server serving `/tmp` on port 3409. Python Playwright, Chromium and Pillow are test dependencies only, not runtime requirements.

### Version 5.1 import completion fix

The builder now writes `/tmp/PKM-v5.1.html`. The staged set import no longer invokes a second browser confirmation after asynchronously decoding images. This confirmation could be suppressed and silently cancel the save. Clicking the finish button now decodes, writes, verifies, and shows a persistent success summary, with separate saving progress and visible failures. Verification reads have a 30-second deadline rather than waiting indefinitely.

The browser regression test serves `/tmp` on port 3410 and explicitly suppresses `window.confirm` during set+image import, checking that the new flow completes and renders saved images. Legacy backup restore, manual image matching, corrupt-image rollback and duplicate-card bundle rollback remain covered.

### Version 5.2 card details

Output: `/tmp/PKM-v5.2.html`. Card details now use an explicitly light dialog, two-column image and metadata layout, version counts and stock placements. Clicking the image opens a separate large viewer fitted to the viewport. Escape closes only the viewer and returns focus to the card details; close buttons and backdrop clicks work on both dialogs. Mobile details stack vertically. Source image data is unchanged.

`browser_check_details.py` covers light appearance with dark OS preference, desktop image enlargement, Escape and close navigation, missing images, mobile overflow and returning to normal registration dialogs. Both browser checks use the local test server on port 3411.

## UI V2

Build: `python3 standalone/build.py` now writes `/tmp/PKM-UI-V2.html`. The application still uses the existing IndexedDB data and accepts both `.pkm` collection files and legacy JSON backups.

The new presentation has a horizontal desktop navigation bar and compact mobile menu, embedded Inter variable font, unified catalogue toolbar with an advanced-filter panel, redesigned card gallery, consistent light dialogs, and responsive set and stock rows. The registration controls show selected location and condition; plus/minus are disabled until a location is selected. Changing the global version filter selects that version for registration. English and Japanese names retain their source data. Stock CSV exports now include the full set code and label filtered versus full exports.

The font is bundled from `@fontsource-variable/inter@5.2.8`, `inter-latin-wght-normal.woff2`, with the SIL Open Font License included in the generated HTML and `INTER-LICENSE.txt`. The UI font does not require a network request. Japanese glyphs use available system fonts. All existing external image links still depend on their source; imported local images remain embedded in collection files.

Tests use a local server serving `/tmp` on port 3412:

- `python3 standalone/browser_check_ui_v2.py`: embedded font, navigation, summary counts, scoped registration, version filters, search, gallery/list, filtered stock CSV, mass registration, move/remove/undo, and responsive sets/cards at 390, 760, 1024 and 1512 px.
- `python3 standalone/browser_check_v5.py`: staged atomic set+image import without browser confirmation, local image rendering/reload, manual name correction, stock history, collection export/restore, old backups, manual image matching and failed-import rollback.
- `python3 standalone/browser_check_details.py`: light details in dark OS mode, enlargement, Escape and close navigation, missing images and mobile fit.

Test data and synthetic card illustrations are created only in isolated browser contexts and are not included in the delivered HTML.

## UI V2.1 — Cardmarket links

The builder now writes `/tmp/PKM-UI-V2.1.html`. Exact product URLs are stored on `versions[].cardmarketUrl`, not on cards, and survive collection-file export/restore. Old collections without these fields need no migration.

Gallery tiles, list rows and card details link either to a saved product page or to an explicitly labelled Cardmarket search. Japanese sets use `language=7` in search URLs and as a default on saved URLs if no language is provided. Card details allow manual editing/removal of each version's link. No guessed product slugs or automatically invented matches are stored.

Import → Cardmarket links accepts UTF-8 comma- or semicolon-separated CSV with columns `setkode,kortnummer,version,cardmarket_url`. Matching uses the full set code, normalised card number, and case-insensitive version name. A missing version is accepted only when exactly one version exists. Unknown/ambiguous matches, invalid URLs and all rows with duplicate targets are excluded and reported. Existing links are preserved by default, with explicit overwrite selection. All selected links are written atomically. URLs must use HTTPS on the exact Cardmarket host and a Pokémon Singles product path; credentials, foreign domains and other routes are rejected. URL validation does not certify the product identity or availability; links should be checked against their physical version.

Run a server serving `/tmp` on port 3413. `browser_check_cardmarket.py` covers fallback links, manual edits and removal, version isolation, CSV preview/overwrite/duplicates/errors, atomic invalid-URL rejection, reload and collection-file roundtrip. The existing UI, details and import regression tests also target the new file on that port.
