# A karmic map of the Earth

A world map in which every place carries the accumulated weight of recorded cruelty
inflicted there by people on other people, from the genus Homo's earliest known killings
to the present, at roughly one-kilometre resolution and with a time window.

The unit of account is one person. An event is a bundle of people who share an episode,
a spatial footprint and a temporal footprint. Each person scores

    s = O × D × M

where O is the outcome factor (1 for death and survival alike), D is a duration factor,
1 + log10(1 + t / 1 day), and M is a four-step manner scale from negligent killing to
cruelty where the suffering was the purpose. A map cell's value is the sum over everyone
of their score times the fraction of their footprint that falls in that cell and in the
chosen years. The design document explains every choice: `docs/design/` or
`Karmic-Map-Design-Document.pdf` in the release.

A live copy of the viewer, with the two coarse global layers and the point layer, is in
`docs/` for GitHub Pages.

## Run it

    uv sync
    scripts/fetch_data.sh                 # ~340 MB of raw sources, see DATA_SOURCES.md
    uv run python3 src/build.py           # ~40 s, writes out/
    python3 -m http.server 8765           # from the repo root
    open http://localhost:8765/viewer/index.html

Viewer URL parameters: `lon`, `lat`, `zoom`, `y0`, `y1`, `panel=0`, `ocean=0`, `names=0`.

## Sources in this build

Seven sources, in `src/karmic/ingest_*.py`, one module each. UCDP Georeferenced Event
Dataset 25.1 for 1989 to 2024. The Trans-Atlantic Slave Trade Database for embarkation,
the Middle Passage and twenty years of bondage per landed person. Wikidata camps with a
recorded death count, standing in for the USHMM camp encyclopedia. The Seguin and Rigby
lynching inventory. Ryan's Colonial Frontier Massacres in Australia. Two hand-curated
tables: bioarchaeological sites from about 800,000 years ago, and Aotearoa New Zealand.
Battlefield deaths between combatants are excluded throughout. See `DATA_SOURCES.md` for
citations and licences, and `HANDOFF.md` for what is draft, what is missing and what is next.

## Layout

    src/karmic/core.py         schema, scoring, footprints -> H3 cells and adaptive year bins
    src/karmic/ingest_*.py     one module per source
    src/build.py               runs all ingestion, writes Parquet and viewer JSON
    src/make_pages.py          assembles docs/ for GitHub Pages
    src/make_standalone.py     single-file HTML with embedded data (optional)
    scripts/fetch_data.sh      downloads the raw sources
    viewer/index.html          deck.gl H3 viewer: time window, estimate, ocean and label toggles
    out/viewer/                per-resolution cell tables (r2, r3, fine kept; others regenerated)
    out/snapshots/             rendered PNGs

Points are placed at H3 resolution 8, polygons and routes at resolution 4. Souls are
counted per episode, so one enslaved person can appear in three bundles.

## Licence

Code MIT. Curated tables and derived data CC BY-NC-SA 4.0, because the Australian frontier
data is non-commercial. See `LICENSE`.
