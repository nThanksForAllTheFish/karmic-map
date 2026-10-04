"""Core schema, scoring and placement for the karmic map prototype.

A *soul bundle* is one row describing N people who share an episode of cruelty,
a spatial footprint and a temporal footprint. N is 1 for a documented individual.
Expanding a bundle to N identical soul rows would give exactly the same map, so
bundles are the storage unit and souls are the unit of account.

Score per soul (design document, "Scoring a single soul"):

    s = O * D * M
    D = 1 + log10(1 + t / t0),   t0 = 1 day

with O = 1 for death and survival alike (revision 2), M in {1,2,3,4}.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Iterable

import h3
import numpy as np
import pandas as pd
from shapely.geometry import shape, mapping, Point, LineString, Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry

RES = 8              # H3 resolution of the base grid (~0.74 km^2)
T0_DAYS = 1.0
OUTCOME_FACTOR = {"died": 1.0, "survived": 1.0}
MANNER = {1: "negligent", 2: "deliberate", 3: "degrading", 4: "suffering as purpose"}


def duration_factor(t_days: float) -> float:
    """D = 1 + log10(1 + t/t0). t_days may be 0."""
    return 1.0 + math.log10(1.0 + max(t_days, 0.0) / T0_DAYS)


def soul_score(outcome: str, t_days: float, manner: int) -> float:
    return OUTCOME_FACTOR[outcome] * duration_factor(t_days) * float(manner)


@dataclass
class Bundle:
    source: str                 # dataset key
    event_id: str               # source-native identifier
    label: str                  # human-readable event or person name
    category: str               # mass_killing | structural | punishment_crime
    outcome: str                # died | survived
    manner: int                 # 1..4
    t_days: float               # duration of the episode for each soul
    count: float                # souls in bundle (central estimate)
    count_low: float
    count_high: float
    year_start: float           # temporal footprint, uniform between start and end
    year_end: float
    footprint_kind: str         # point | polygon | route | city
    geometry: BaseGeometry      # shapely geometry, WGS84
    confidence: str = "recorded"  # recorded | modeled
    named: bool = False
    note: str = ""

    @property
    def score_each(self) -> float:
        return soul_score(self.outcome, self.t_days, self.manner)


# ---------------------------------------------------------------------------
# Spatial footprints -> cell weights
# ---------------------------------------------------------------------------

def _cells_point(pt: Point, res: int) -> dict[str, float]:
    return {h3.latlng_to_cell(pt.y, pt.x, res): 1.0}


def _cells_polygon(geom: Polygon | MultiPolygon, res: int, max_cells: int = 60000) -> dict[str, float]:
    """Uniform density over the polygon. Coarsens resolution if the polygon
    would produce too many cells, then returns children-weighted parents, so
    every result is still a set of resolution-`res` *parents* recorded at the
    coarser level. Callers aggregate by cell id, so mixing resolutions in the
    output table is avoided by expanding parents back to `res` only when small."""
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    r = res
    while True:
        cells: list[str] = []
        for p in polys:
            if p.is_empty:
                continue
            cells.extend(h3.polygon_to_cells(h3.geo_to_h3shape(mapping(p)), r))
        if len(cells) <= max_cells or r <= 3:
            break
        r -= 1
    if not cells:
        c = geom.representative_point()
        return _cells_point(c, res)
    w = 1.0 / len(cells)
    return {c: w for c in cells}


def _cells_route(line: LineString, res: int, profile: str = "rising") -> dict[str, float]:
    """Sample the line at ~1 cell spacing at the chosen resolution and weight
    samples by a mortality profile. 'rising' puts more weight late in the voyage."""
    length_deg = line.length
    n = max(int(length_deg / 0.25), 20)          # sample every ~0.25 deg
    ts = np.linspace(0, 1, n)
    if profile == "rising":
        w = 0.5 + ts                              # linear rise, 0.5 -> 1.5
    else:
        w = np.ones_like(ts)
    w = w / w.sum()
    out: dict[str, float] = {}
    for t, wi in zip(ts, w):
        p = line.interpolate(t, normalized=True)
        c = h3.latlng_to_cell(p.y, p.x, res)
        out[c] = out.get(c, 0.0) + float(wi)
    return out


def footprint_cells(b: Bundle, res: int = RES) -> dict[str, float]:
    g = b.geometry
    if b.footprint_kind == "point" or isinstance(g, Point):
        return _cells_point(g if isinstance(g, Point) else g.centroid, res)
    if b.footprint_kind == "route":
        return _cells_route(g, res)
    return _cells_polygon(g, res)


# ---------------------------------------------------------------------------
# Temporal footprints -> year-bin weights
# ---------------------------------------------------------------------------

def bin_width(span_years: float) -> int:
    """Adaptive temporal bin width: 1 year for spans up to 50 years, then 5, 50, 500,
    5000. Keeps deep-time footprints (a site dated to a 40,000-year range) to a few
    dozen rows instead of tens of thousands."""
    for lim, w in ((50, 1), (500, 5), (5000, 50), (50000, 500)):
        if span_years <= lim:
            return w
    return 5000


def year_bins(b: Bundle) -> dict[tuple[int, int], float]:
    """Uniform over [year_start, year_end], discretised to bins of adaptive width.
    Keys are (bin_start, bin_width); weights sum to 1."""
    y0, y1 = b.year_start, b.year_end
    if y1 < y0:
        y0, y1 = y1, y0
    w = bin_width(y1 - y0)
    a = int(math.floor(y0 / w)) * w
    z = int(math.floor(y1 / w)) * w
    if a == z or y1 - y0 <= 0:
        return {(a, w): 1.0}
    total = y1 - y0
    out = {}
    for y in range(a, z + 1, w):
        lo, hi = max(y, y0), min(y + w, y1)
        if hi > lo:
            out[(y, w)] = (hi - lo) / total
    return out


# ---------------------------------------------------------------------------
# Bundle -> contributions table
# ---------------------------------------------------------------------------

def bundle_contributions(b: Bundle, res: int = RES, source_id: int = 0) -> pd.DataFrame:
    """Rows of (cell, year, score, souls) for one bundle. Sum of score over rows
    equals count * score_each; sum of souls equals count."""
    cells = footprint_cells(b, res)
    years = year_bins(b)
    s_total = b.count * b.score_each
    rows = []
    for c, wc in cells.items():
        for (y, dy), wy in years.items():
            w = wc * wy
            rows.append((c, y, dy, s_total * w, b.count * w, b.count_low * w, b.count_high * w, source_id))
    return pd.DataFrame(rows, columns=["cell", "year", "dy", "score", "souls", "souls_low", "souls_high", "src"])


def bundles_to_frame(bundles: Iterable[Bundle]) -> pd.DataFrame:
    recs = []
    for b in bundles:
        d = asdict(b)
        d["geometry"] = b.geometry.wkt
        d["score_each"] = b.score_each
        recs.append(d)
    return pd.DataFrame(recs)
