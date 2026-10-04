"""Assemble docs/ for GitHub Pages: the viewer, country labels, and the small data
layers (r2, r3, fine) with a meta.json that lists only those layers. About 11 MB.

    uv run python3 src/make_pages.py
"""
from __future__ import annotations

import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
LAYERS = ["r2", "r3", "r3coarse", "fine"]

os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
html = open(os.path.join(ROOT, "viewer", "index.html"), encoding="utf-8").read()
html = html.replace("<script>\nconst {DeckGL, H3HexagonLayer, TextLayer} = deck;",
                    "<script>window.DATA_BASE = 'data/';</script>\n<script>\nconst {DeckGL, H3HexagonLayer, TextLayer} = deck;")
open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(html)
shutil.copy(os.path.join(ROOT, "viewer", "countries.json"), os.path.join(DOCS, "countries.json"))

meta = json.load(open(os.path.join(ROOT, "out", "viewer", "meta.json")))
meta["layers"] = {k: v for k, v in meta["layers"].items() if k in LAYERS}
json.dump(meta, open(os.path.join(DOCS, "data", "meta.json"), "w"), indent=1)
for name in LAYERS:
    shutil.copy(os.path.join(ROOT, "out", "viewer", f"cells_{name}.json"), os.path.join(DOCS, "data", f"cells_{name}.json"))
open(os.path.join(DOCS, ".nojekyll"), "w").close()
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DOCS) for f in fs)
print(f"docs/ ready: {total/1e6:.1f} MB, layers {LAYERS}")
