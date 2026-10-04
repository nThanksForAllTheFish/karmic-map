# Handoff: state of the karmic map, 4 October 2026

Written for whoever picks this up next, human or assistant. It records what was decided,
what is built, what is draft, and what should happen next. The design document is the
authority on the rules; this file is the authority on the state.

## Decisions taken by the author

The unit of account is one person, at "the resolution of a human soul". Human means the
genus Homo, so Neanderthals and Homo antecessor count. Karma attaches to the ground where
the act happened, not to the capital that ordered it or the victims' homeland. The score is
s = O × D × M with O = 1 for death and survival alike (the measure is accumulated suffering,
and death ends it), D = 1 + log10(1 + t / 1 day), and a four-step manner scale. No time
decay. No offset for mercy or rescue. Categories in scope: mass killing of noncombatants,
structural cruelty (slavery, forced labour, engineered famine), state punishment and
individual crime. Battlefield deaths between combatants are out. Ocean cells show by
default with a toggle. The modeled layer, for inferred souls such as demographic collapse,
is an optional overlay, not yet built. Skeletal evidence is a third confidence class,
forensic, with a contested flag. Time is a two-handled window on a log axis in years before
present, and every soul has a temporal footprint discretised to adaptive bins.

## What is built

A uv Python project. `src/build.py` runs seven ingestion modules, scores and places about
84,000 bundles into an H3 cell table (Parquet) and writes per-resolution JSON for a
deck.gl viewer. The viewer has the time window, low/central/high estimate toggle, presets
from prehistory to 1989 onward, ocean-transit and country-label toggles, hover readouts
and URL parameters. `docs/` is a GitHub Pages copy with the small layers. Build takes
about forty seconds on an M-series Mac. Totals in the current build: about 36 million
soul-episodes and a summed score of 333 million, dominated by the slave trade because
twenty years of bondage scores about 15 per person against about 2 for a shooting.

## What is draft and must not be published as fact

`ingest_archaeology.py` (50 sites) and `ingest_nz.py` (19 events) were compiled from memory
of the literature by the assistant during the design sessions. Each entry names its
principal publication, but none has been checked against the source. Counts for Herxheim,
Tell Brak, Anyang, Cahokia Mound 72 and all four Musket Wars pā sieges have low-to-high
ranges of a factor of three or more. Nataruk's coordinates are approximate. A citation pass
is the first job before anything leaves the prototype.

The manner factors for the sacrifice sites (3 for bound or cut victims, 4 where mutilation
or torture is documented) and the Australian rule (3 where poison, burning, chaining or
infants appear in the record) are the assistant's judgment, not the author's, and should be
reviewed.

## Known substitutions

Wikidata camps stand in for the USHMM Encyclopedia of Camps and Ghettos (not published as
data). The Seguin–Rigby file is the 1,328-victim supplement; the Tolnay–Beck Southern core
is not openly downloadable, so the US South is under-represented. Walder's Cultural
Revolution county data, named in the design, is not public and was never ingested.
SlaveVoyages port coordinates are a hand table because the site's geo API needs a token.

## Known gaps, in rough order of what they would change on the map

Yad Vashem names (about 4.9 million, the largest name list; would turn the camp points into
people). Census-based slavery polygons for the Americas, which the design scores by
person-years. The Soviet, Chinese and Cambodian events, which are the largest twentieth-
century totals and are currently absent except where Wikidata has a camp. Pre-1500 Eurasia
beyond the archaeological table. The modeled overlay for demographic collapse (the Americas
after 1492, Australia after 1788), which is an order of magnitude larger than anything
recorded body by body. The documentation-density layer. The per-cell click-through to
events and names, which the design calls a requirement rather than a nicety.

## Publishing plan

GitHub: `git init` in this folder, commit, push to a public repo, enable Pages from the
`docs/` folder on the default branch. The `.gitignore` keeps raw data and large outputs
out. Licences: MIT for code, CC BY-NC-SA 4.0 for curated tables and derived data (the
Australian frontier data is CC BY-NC 4.0 and asks for respectful re-use; carry that notice).
Medium: the draft is `Karmic-Map-Medium-Draft.md`; figures are in `out/snapshots/`. Both
the article and the README say plainly that the two curated tables are unverified drafts.

## Tooling notes from the original machine

The project was built on a Mac where bare `python3` is broken; use `uv run`. The viewer
needs an HTTP server because it fetches JSON; `python3 -m http.server` from the repo root
is enough. Headless Chrome renders the snapshots but hangs on exit; background it and kill
it after thirty seconds, the PNG is already complete. `src/make_standalone.py` produces a
single HTML file with embedded data and libraries, parked at the author's request.
