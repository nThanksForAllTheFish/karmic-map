"""Seguin & Rigby (2019) 'National Crimes' lynching inventory -> named-soul bundles.

This file is the 1,328-victim supplement that extends Tolnay-Beck beyond the
South to all 48 contiguous states, 1883-1941. The Tolnay-Beck core (~2,800
Southern victims) is not openly downloadable and is NOT included here, so the
South is under-represented in this prototype layer.

Placement: county centroid from the 2023 Census gazetteer (county boundaries
have shifted slightly since 1900; adequate at the display scales used).
Manner: 4 for lynchings recorded as burned, tortured, or mutilated; 3 otherwise
(mob killing as public spectacle). Duration: 1 day. Category: punishment_crime.
"""
from __future__ import annotations

import pandas as pd
from shapely.geometry import Point

from .core import Bundle

RAW = "data/raw/lynching_seguin_rigby.csv"
GAZ = "data/raw/2023_Gaz_counties_national.txt"


def run() -> list[Bundle]:
    df = pd.read_csv(RAW)
    gaz = pd.read_csv(GAZ, sep="\t", dtype={"GEOID": str})
    gaz.columns = [c.strip() for c in gaz.columns]
    cent = {int(g): (float(lon), float(lat)) for g, lat, lon in zip(gaz.GEOID, gaz.INTPTLAT, gaz.INTPTLONG)}
    bundles, miss = [], 0
    for r in df.itertuples(index=False):
        try:
            fips = int(float(r.full_fips))
        except (TypeError, ValueError):
            try:
                fips = int(r.state_fips) * 1000 + int(r.county_fips)
            except (TypeError, ValueError):
                fips = -1
        c = cent.get(fips)
        if c is None:
            miss += 1
            continue
        method = str(r.lynch_method).lower()
        manner = 4 if any(k in method for k in ["burn", "tortur", "mutilat", "dismember"]) else 3
        y = float(r.year) + (float(r.month) - 1) / 12 if pd.notna(r.month) else float(r.year)
        name = str(r.victim) if pd.notna(r.victim) else "Unknown"
        bundles.append(Bundle("seguin_rigby_2019", f"sr:{r.caseid}", f"{name}, lynched {int(r.year)} in {r.county} County, {r.state}",
                              "punishment_crime", "died", manner, 1.0, 1, 1, 1, y, y + 1 / 12, "point", Point(*c),
                              named=(name != "Unknown"), note=str(r.lynch_method)))
    print(f"lynching: {len(bundles)} named/individual souls, {miss} unplaced")
    return bundles
