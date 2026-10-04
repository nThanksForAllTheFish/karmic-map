"""Build the karmic map cell table from all ingestion modules.

Outputs (out/):
  bundles.parquet         one row per soul bundle (event-level provenance)
  contributions.parquet   (cell, res, year, score, souls, souls_low, souls_high, src)
  viewer/*.json           per-resolution, per-5-year-bin aggregates for the web viewer

Polygon and route footprints are placed at a coarser H3 resolution than points
(see PLACE_RES) so the table stays small; the viewer renders whatever resolution
each row carries and rolls fine rows up to the display resolution.
"""
from __future__ import annotations

import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))

import duckdb
import h3
import numpy as np
import pandas as pd

from karmic import core
from karmic import (ingest_ucdp, ingest_camps, ingest_lynching, ingest_slavevoyages, ingest_archaeology,
                    ingest_frontier_au, ingest_nz)
from karmic.core import Bundle, footprint_cells, year_bins, bundles_to_frame

PLACE_RES = {"point": 8, "polygon": 4, "route": 4, "city": 6}
SOURCES = {"ucdp_ged_25_1": 1, "wikidata_camps": 2, "seguin_rigby_2019": 3, "slavevoyages_2019": 4,
           "archaeology_curated": 5, "frontier_massacres_au": 6, "nz_curated": 7}
OUT = "out"
YEAR_BIN = 5
VIEW_RES = [2, 3, 4, 5]     # global display resolutions
FINE_RES = 7                # point-only fine layer


def contributions(bundles: list[Bundle]) -> pd.DataFrame:
    cache: dict[str, dict[str, float]] = {}
    frames = []
    skipped = 0
    for b in bundles:
        if b.count <= 0:
            continue
        if not (np.isfinite(b.year_start) and np.isfinite(b.year_end) and np.isfinite(b.count)):
            skipped += 1
            continue
        res = PLACE_RES[b.footprint_kind]
        key = f"{b.footprint_kind}:{res}:{b.geometry.wkb_hex[:64]}:{hash(b.geometry.wkb)}"
        cells = cache.get(key)
        if cells is None:
            cells = footprint_cells(b, res)
            cache[key] = cells
        years = year_bins(b)
        s_total = b.count * b.score_each
        cs = np.array(list(cells.keys()))
        cw = np.array(list(cells.values()))
        ys = np.array([k[0] for k in years], dtype=np.int64)
        dys = np.array([k[1] for k in years], dtype=np.int64)
        yw = np.array(list(years.values()))
        W = np.outer(cw, yw)
        frames.append(pd.DataFrame({
            "cell": np.repeat(cs, len(ys)), "res": res, "year": np.tile(ys, len(cs)), "dy": np.tile(dys, len(cs)),
            "score": (s_total * W).ravel(), "souls": (b.count * W).ravel(),
            "souls_low": (b.count_low * W).ravel(), "souls_high": (b.count_high * W).ravel(),
            "src": SOURCES[b.source], "route": 1 if b.footprint_kind == "route" else 0}))
    if skipped:
        print(f"  skipped {skipped} bundles with undefined dates or counts")
    df = pd.concat(frames, ignore_index=True)
    return df.groupby(["cell", "res", "year", "dy", "src", "route"], as_index=False).sum()


def viewer_tables(con: duckdb.DuckDBPyConnection):
    os.makedirs(f"{OUT}/viewer", exist_ok=True)
    meta = {"year_bin": YEAR_BIN, "layers": {}}
    # (name, rollup resolution, row filter). 'coarse' keeps polygon/route rows at native
    # resolution for the zoomed-in view, where 'fine' carries the point rows rolled to res 7.
    # 'r3coarse' is the polygon/route rows rolled to r3 with the point rows left out, so a Pages
    # copy that carries only r2/r3/fine can stack 'fine' on it without double counting.
    specs = [(f"r{r}", r, "") for r in VIEW_RES] + [("fine", FINE_RES, "WHERE res >= 7"), ("coarse", 99, "WHERE res <= 6"),
                                                    ("r3coarse", 3, "WHERE res <= 6")]
    for name, r, where in specs:
        q = f"""
        WITH x AS (
          SELECT CASE WHEN res > {r} THEN h3_cell_to_parent(cell, {r}) ELSE cell END AS cell,
                 CASE WHEN res > {r} THEN {r} ELSE res END AS res,
                 CASE WHEN dy <= {YEAR_BIN} THEN (year // {YEAR_BIN}) * {YEAR_BIN} ELSE year END AS bin,
                 CASE WHEN dy <= {YEAR_BIN} THEN {YEAR_BIN} ELSE dy END AS dy,
                 score, souls, souls_low, souls_high, src, route
          FROM contributions {where})
        SELECT cell, res, bin, dy, route, sum(score) AS score, sum(souls) AS souls, sum(souls_low) AS souls_low,
               sum(souls_high) AS souls_high, count(DISTINCT src) AS nsrc
        FROM x GROUP BY 1,2,3,4,5 ORDER BY 1,3,4,5
        """
        df = con.execute(q).df()
        ratio_l = (df.souls_low / df.souls.where(df.souls > 0, 1)).clip(0, 5)
        ratio_h = (df.souls_high / df.souls.where(df.souls > 0, 1)).clip(0, 5)
        cols = {"cell": df.cell.tolist(), "res": df.res.astype(int).tolist(), "bin": df.bin.astype(int).tolist(),
                "dy": df.dy.astype(int).tolist(),
                "score": df.score.round(1).tolist(), "souls": df.souls.round(0).astype(int).tolist(),
                "rl": ratio_l.round(2).tolist(), "rh": ratio_h.round(2).tolist(),
                "nsrc": df.nsrc.astype(int).tolist(), "rt": df.route.astype(int).tolist()}
        path = f"{OUT}/viewer/cells_{name}.json"
        json.dump(cols, open(path, "w"), separators=(",", ":"))
        meta["layers"][name] = {"rows": len(df), "bytes": os.path.getsize(path),
                                "score_max": float(df.score.max()) if len(df) else 0.0}
        print(f"  viewer {name}: {len(df)} rows, {os.path.getsize(path)/1e6:.1f} MB")
    yr = con.execute("SELECT min(year), max(year) FROM contributions").fetchone()
    meta["year_min"], meta["year_max"] = int(yr[0]), int(yr[1])
    json.dump(meta, open(f"{OUT}/viewer/meta.json", "w"), indent=1)


def main():
    os.makedirs(OUT, exist_ok=True)
    t = time.time()
    bundles: list[Bundle] = []
    for mod in (ingest_archaeology, ingest_frontier_au, ingest_nz, ingest_lynching, ingest_camps, ingest_ucdp, ingest_slavevoyages):
        bundles.extend(mod.run())
    print(f"{len(bundles)} bundles in {time.time()-t:.0f}s")
    bf = bundles_to_frame(bundles)
    bf.to_parquet(f"{OUT}/bundles.parquet", index=False)
    t = time.time()
    cf = contributions(bundles)
    cf.to_parquet(f"{OUT}/contributions.parquet", index=False)
    print(f"contributions: {len(cf)} rows in {time.time()-t:.0f}s; total score {cf.score.sum():,.0f}, souls {cf.souls.sum():,.0f}")
    con = duckdb.connect()
    con.execute("INSTALL h3 FROM community; LOAD h3;")
    con.execute(f"CREATE TABLE contributions AS SELECT * FROM '{OUT}/contributions.parquet'")
    print(con.execute("SELECT src, sum(score), sum(souls), count(*) FROM contributions GROUP BY 1 ORDER BY 1").df())
    viewer_tables(con)
    # event index for the click-through (per res-5 cell: top bundles by score)
    bf["score_total"] = bf["count"] * bf["score_each"]
    bf[["source", "event_id", "label", "category", "manner", "t_days", "count", "count_low", "count_high",
        "year_start", "year_end", "footprint_kind", "confidence", "named", "note", "score_total"]
       ].to_parquet(f"{OUT}/events.parquet", index=False)


if __name__ == "__main__":
    main()
