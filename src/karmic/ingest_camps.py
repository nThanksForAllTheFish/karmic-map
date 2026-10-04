"""Wikidata camps (instances of concentration camp and subclasses) -> bundles.

Stand-in for the USHMM Encyclopedia of Camps and Ghettos, which is not
published as a dataset. Only camps with a recorded death count (P1120) score;
the remaining sites carry zero souls and exist so the documentation-density
layer can show them.

Duration per soul: extermination camps and known death camps, 1 day; other
camps, 180 days (a coarse prototype constant). Manner 3 (systematic degradation).
Temporal footprint: inception..dissolution where present, else 1939..1945 for
Nazi-era camps in Europe, else the camp's recorded dates or unknown (dropped).
"""
from __future__ import annotations

import re
import pandas as pd
from shapely.geometry import Point

from .core import Bundle

RAW = "data/raw/wikidata_camps.csv"
DEATH_CAMPS = ["auschwitz", "treblinka", "belzec", "bełżec", "sobibor", "sobibór", "chelmno", "chełmno", "kulmhof",
               "majdanek", "maly trostenets", "jasenovac", "janowska"]


def _year(s):
    if isinstance(s, str) and re.match(r"^-?\d{4}", s):
        return int(s[:4]) if not s.startswith("-") else -int(s[1:5])
    return None


def run() -> list[Bundle]:
    df = pd.read_csv(RAW).drop_duplicates("camp")
    m = df.coord.str.extract(r"Point\(([-\d.]+) ([-\d.]+)\)")
    df["lon"], df["lat"] = m[0].astype(float), m[1].astype(float)
    df["y0"], df["y1"] = df.inception.map(_year), df.dissolved.map(_year)
    bundles = []
    for r in df.itertuples(index=False):
        label = str(r.campLabel)
        typ = str(r.typeLabel)
        deaths = float(r.deaths) if pd.notna(r.deaths) else 0.0
        is_death_camp = typ == "extermination camp" or any(k in label.lower() for k in DEATH_CAMPS)
        nazi_era = ("Nazi" in typ or "Nazi" in str(r.countryLabel) or is_death_camp
                    or str(r.countryLabel) in {"Germany", "Poland", "Austria", "Czech Republic", "Netherlands", "France", "Belgium", "Belarus", "Ukraine", "Lithuania", "Latvia", "Estonia", "Croatia", "Serbia", "Hungary", "Slovakia", "Italy", "Norway"})
        y0 = None if pd.isna(r.y0) else int(r.y0)
        y1 = None if pd.isna(r.y1) else int(r.y1)
        if y0 is None and y1 is None:
            if not nazi_era:
                continue
            y0, y1 = 1939, 1945
        y0 = y0 if y0 is not None else max(1933, (y1 or 1945) - 4)
        y1 = y1 if y1 is not None else min(1945, y0 + 4) if nazi_era else y0 + 4
        t_days = 1.0 if is_death_camp else 180.0
        bundles.append(Bundle("wikidata_camps", f"wd:{r.camp.rsplit('/', 1)[-1]}", label, "mass_killing", "died", 3, t_days,
                              deaths, deaths * 0.8, deaths * 1.2, float(y0), float(y1) + 1.0, "point", Point(r.lon, r.lat),
                              note=typ))
    scored = sum(1 for b in bundles if b.count > 0)
    print(f"camps: {len(bundles)} sites, {scored} with death counts, {sum(b.count for b in bundles):.0f} souls")
    return bundles
