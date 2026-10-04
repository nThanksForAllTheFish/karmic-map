---
name: project-karmic-map
description: "A \"karmic map of the Earth\" — soul-level scoring of recorded human cruelty rendered on an H3 hex grid with a time window; design doc + working prototype in ~/Documents/karmic-map (2026-09-28)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 40959932-8f43-4265-bb39-08b26ffaaed6
  modified: 2026-09-29T12:00:15.098Z
---

Personal project. The author wants a world map colouring every ~1 km cell by the
accumulated "karma" of recorded human-on-human cruelty, from genocide down to individual crimes.
The unit of account is one person ("resolution of a human soul"), not an event.

Decisions he made (2026-09-28): score per soul s = O × D × M with O = 1 for death and survival
alike (the measure is accumulated suffering; death ends it), D = 1 + log10(1 + t/1 day),
M a four-step manner scale (1 negligent … 4 suffering as purpose). Karma attaches to the site of
the act only. No time decay, no mercy offset. Ocean cells shown by default. Modeled (inferred)
souls are an optional overlay, off by default. Two-handled time window on a log years-before-present
axis; each soul has a temporal footprint like its spatial one. Categories in scope: mass killing
of noncombatants, structural cruelty (slavery, famine), punishment and individual crime.
Battlefield deaths excluded. 2026-09-29: "human" means genus Homo (Neanderthals, H. antecessor
count); skeletal/bioarchaeological evidence is a third confidence class "forensic" (with a
contested flag), and a hand-curated table of ~50 sites from Gran Dolina (~800 kya) onward is in the
build; time axis runs to 1 Mya with adaptive bins. Viewer has an ocean-transit toggle, present-day country labels (sans-serif bold), controlled view state.
Added Ryan et al. Colonial Frontier Massacres AU (TLCMap layer 1336 CSV, 438 sites) and a DRAFT hand-curated
NZ table (Musket Wars pa sieges contested, Moriori, NZ Wars prisoner killings, Parihaka) — the author asked for both
after noticing AU/NZ were blank. Standalone single-file viewer is on hold at his request.

Artifacts: design doc `~/Documents/Karmic-Map-Design-Document.{md,html,pdf}` (revision 2);
prototype in `~/Documents/karmic-map/` (uv project; `src/build.py` builds Parquet + viewer JSON,
`viewer/index.html` is a deck.gl H3 viewer served by `python -m http.server 8765 --directory ~/Documents/karmic-map`,
launch config in `~/.claude/launch.json`). Prototype sources: UCDP GED 25.1, Trans-Atlantic Slave
Trade Database 2019 export (place codes geocoded by a hand table; the site's geo API needs a token),
Wikidata camps with P1120 death counts (stand-in for USHMM encyclopedia), Seguin–Rigby 2019 lynching
supplement (1,328 victims; Tolnay–Beck core not openly downloadable). Walder's Cultural Revolution
county data is not public; not ingested.

**Why:** He framed it as a memorial that happens to be quantitative, not a ranking; wants honesty
about recording bias.
**How to apply:** Keep the per-soul arithmetic transparent and parameters separate from data. Next
steps he has not yet approved: Yad Vashem names, census-based slavery polygons, per-cell event
click-through, modeled overlay.
