"""Colonial Frontier Massacres in Australia, 1788-1930 (Ryan et al., University of
Newcastle; final Stage 5.0 data as republished on the Time Layered Cultural Map,
layer 1336) -> bundles.

438 sites, each a massacre of six or more, with coordinates, a date or date range,
the number recorded dead, victim and attacker descriptions, motive, weapons and a
one-to-three-star corroboration rating. VictimsDead is the project's minimum
credible figure, so it is used as both the central and the low estimate; the high
estimate is doubled, which is conservative against the project's own view that
recorded massacres are a fraction of the frontier toll.

Manner: 2 (deliberate killing) by default; 3 where the weapons include poison or
the description records bodies burned, victims chained or bound, or infants
killed. Duration 0. Category mass_killing. Colonists killed by Aboriginal attackers
(13 sites) are included on the same terms. Confidence: recorded, or
recorded-contested for one-star corroboration.
"""
from __future__ import annotations

import re
import pandas as pd
from shapely.geometry import Point

from .core import Bundle

RAW = "data/raw/colonial_frontier_massacres_tlcmap.csv"
DEGRADING = re.compile(r"poison|burn(ed|t|ing) (the )?(bodies|alive|them)|chained|tied up|bound|infant|babies|children were|tortur|decapitat|heads were", re.I)


def _year(s: str, fallback: float | None = None) -> float | None:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(s))
    if not m:
        return fallback
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return y + (mo - 1) / 12 + (d - 1) / 365.25


def run() -> list[Bundle]:
    df = pd.read_csv(RAW)
    bundles = []
    for r in df.itertuples(index=False):
        dead = pd.to_numeric(r.VictimsDead, errors="coerce")
        if not dead or dead <= 0:
            continue
        y0 = _year(r.datestart)
        y1 = _year(r.dateend, y0)
        if y0 is None:
            continue
        if y1 < y0:
            y0, y1 = y1, y0
        text = f"{r.WeaponsUsed} {r.description}"
        manner = 3 if DEGRADING.search(str(text)) else 2
        stars = str(r.CorroborationRating).count("*")
        conf = "recorded" if stars >= 2 else "recorded-contested"
        victims = "Aboriginal and Torres Strait Islander people" if str(r.Victims).startswith("Aboriginal") else str(r.Victims)
        lang = f", {r.LanguageGroup}" if isinstance(r.LanguageGroup, str) and r.LanguageGroup.strip() else ""
        label = f"{r.title}, {str(r.datestart)[:4]}: {int(dead)} {victims} killed by {r.AttackerDescription}{lang}"
        bundles.append(Bundle("frontier_massacres_au", f"cfm:{r.ghap_id}", label, "mass_killing", "died", manner, 0.0,
                              float(dead), float(dead), float(dead) * 2.0, y0, y1 + 1 / 365.25, "point",
                              Point(float(r.longitude), float(r.latitude)), confidence=conf,
                              note=f"motive {r.Motive}; weapons {r.WeaponsUsed}; corroboration {r.CorroborationRating}; {r.Colony}"))
    print(f"frontier_au: {len(bundles)} sites, {sum(b.count for b in bundles):.0f} souls, "
          f"{sum(1 for b in bundles if b.manner == 3)} at manner 3, {sum(1 for b in bundles if 'contested' in b.confidence)} one-star")
    return bundles
