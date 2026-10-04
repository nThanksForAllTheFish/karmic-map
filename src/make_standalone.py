"""Bundle viewer/index.html, the JS libraries and selected data layers into one
self-contained HTML file that opens from disk in any modern browser. The base
map tiles still come from the internet; without a connection the hexagons draw
on a black background.

    uv run python3 src/make_standalone.py [r2 r3 fine]
"""
from __future__ import annotations

import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "viewer", "lib")
OUT = os.path.expanduser("~/Documents/Karmic-Map-Viewer.html")
LAYERS = sys.argv[1:] or ["r2", "r3", "fine"]


def fetch(url: str, name: str) -> str:
    os.makedirs(LIB, exist_ok=True)
    p = os.path.join(LIB, name)
    if not os.path.exists(p):
        urllib.request.urlretrieve(url, p)
    return open(p, encoding="utf-8").read()


html = open(os.path.join(ROOT, "viewer", "index.html"), encoding="utf-8").read()

# inline the three libraries and the maplibre stylesheet
for url, name in [("https://unpkg.com/h3-js@4.1.0/dist/h3-js.umd.js", "h3-js.umd.js"),
                  ("https://unpkg.com/deck.gl@9.0.35/dist.min.js", "deck.gl.min.js"),
                  ("https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js", "maplibre-gl.js")]:
    js = fetch(url, name).replace("</script>", "<\\/script>")
    html = html.replace(f'<script src="{url}"></script>', f"<script>{js}</script>")
css = fetch("https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css", "maplibre-gl.css")
html = re.sub(r'<link href="https://unpkg.com/maplibre-gl[^"]*\.css" rel="stylesheet">', f"<style>{css}</style>", html)

# embed the data
meta = json.load(open(os.path.join(ROOT, "out", "viewer", "meta.json")))
embedded = {"meta": meta, "countries": json.load(open(os.path.join(ROOT, "viewer", "countries.json"), encoding="utf-8"))}
for name in LAYERS:
    embedded[name] = json.load(open(os.path.join(ROOT, "out", "viewer", f"cells_{name}.json")))
blob = json.dumps(embedded, separators=(",", ":")).replace("</script>", "<\\/script>")
inject = f"<script>window.EMBEDDED={blob};window.AVAILABLE={json.dumps(LAYERS)};</script>\n"
anchor = "<script>\nconst {DeckGL"
assert anchor in html, "viewer script anchor not found"
html = html.replace(anchor, inject + anchor, 1)
html = html.replace("<title>A karmic map of the Earth — prototype</title>",
                    "<title>A karmic map of the Earth — standalone prototype</title>")

open(OUT, "w", encoding="utf-8").write(html)
print(f"wrote {OUT}: {os.path.getsize(OUT)/1e6:.1f} MB with layers {LAYERS}")
