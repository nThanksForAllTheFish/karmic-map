"""UCDP Georeferenced Event Dataset 25.1 -> soul bundles.

Scope: mass killing of noncombatants. One-sided violence (type 3) counts in
full; for state-based and non-state conflict (types 1, 2) only the
deaths_civilians column counts. Combatant deaths are excluded by design.

Footprint by UCDP where_prec:
  1 exact location            -> point
  2 within ~25 km             -> disk, 25 km
  3 second-order admin unit   -> disk, 50 km (adm2 polygons not shipped here)
  4 first-order admin unit    -> Natural Earth admin-1 polygon (fallback disk 100 km)
  5 country (adm0 known only) -> country polygon
  6 country, stated as such   -> country polygon
  7 international waters / unclear -> dropped
Temporal footprint: date_start .. date_end, uniform.
Manner: 2 (deliberate killing, no additional degradation coded). Duration: 0.
"""
from __future__ import annotations

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from .core import Bundle

RAW = "data/raw/GEDEvent_v25_1.csv"
NE_ADM1 = "data/raw/ne_admin1/ne_10m_admin_1_states_provinces.shp"
NE_ADM0 = "data/raw/ne_countries/ne_110m_admin_0_countries.shp"


def _disk(lon: float, lat: float, km: float):
    # geodesic-ish disk: degrees per km scaled by latitude
    dlat = km / 111.0
    dlon = km / (111.0 * max(np.cos(np.radians(lat)), 0.2))
    from shapely.affinity import scale
    return scale(Point(lon, lat).buffer(1.0, 16), dlon, dlat, origin=(lon, lat))


def _norm(s: str) -> str:
    import unicodedata, re
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = s.lower()
    for w in [" governorate", " oblast", " province", " region", " state", " district", " department", " county", " prefecture", " division", " territory", " krai", " republic"]:
        s = s.replace(w, "")
    return re.sub(r"[^a-z]", "", s)


def load_events() -> pd.DataFrame:
    con = duckdb.connect()
    q = f"""
    SELECT id, type_of_violence, where_prec, latitude, longitude, adm_1, country,
           date_start, date_end,
           CASE WHEN type_of_violence = 3 THEN best ELSE deaths_civilians END AS souls,
           CASE WHEN type_of_violence = 3 THEN low
                ELSE deaths_civilians * (CASE WHEN best > 0 THEN low * 1.0 / best ELSE 1 END) END AS souls_low,
           CASE WHEN type_of_violence = 3 THEN high
                ELSE deaths_civilians * (CASE WHEN best > 0 THEN high * 1.0 / best ELSE 1 END) END AS souls_high,
           conflict_name, side_a, side_b
    FROM read_csv('{RAW}', header=true, sample_size=-1)
    WHERE where_prec BETWEEN 1 AND 6
      AND (CASE WHEN type_of_violence = 3 THEN best ELSE deaths_civilians END) > 0
    """
    df = con.execute(q).df()
    df["date_start"] = pd.to_datetime(df.date_start)
    df["date_end"] = pd.to_datetime(df.date_end)
    df["y0"] = df.date_start.dt.year + (df.date_start.dt.dayofyear - 1) / 365.25
    df["y1"] = df.date_end.dt.year + (df.date_end.dt.dayofyear) / 365.25
    return df


def build_bundles(df: pd.DataFrame) -> list[Bundle]:
    adm1 = gpd.read_file(NE_ADM1)[["name", "name_en", "admin", "geometry"]]
    adm1["key"] = adm1.name.map(_norm)
    adm1["key_en"] = adm1.name_en.fillna(adm1.name).map(_norm)
    adm1_by_key = {}
    for _, r in adm1.iterrows():
        adm1_by_key.setdefault(r.key, r.geometry)
        adm1_by_key.setdefault(r.key_en, r.geometry)
    adm0 = gpd.read_file(NE_ADM0)[["NAME", "NAME_LONG", "ADMIN", "geometry"]]
    adm0_by_key = {}
    for _, r in adm0.iterrows():
        for n in (r.NAME, r.NAME_LONG, r.ADMIN):
            adm0_by_key.setdefault(_norm(n), r.geometry)
    # UCDP country names that differ from Natural Earth
    alias = {"dr congo (zaire)": "democraticrepublicofthecongo", "myanmar (burma)": "myanmar",
             "russia (soviet union)": "russia", "yemen (north yemen)": "yemen", "cambodia (kampuchea)": "cambodia",
             "madagascar (malagasy)": "madagascar", "zimbabwe (rhodesia)": "zimbabwe", "ivory coast": "cotedivoire",
             "serbia (yugoslavia)": "republicofserbia", "bosnia-herzegovina": "bosniaandherzegovina",
             "united states of america": "unitedstatesofamerica", "kingdom of eswatini (swaziland)": "eswatini",
             "vietnam (north vietnam)": "vietnam", "macedonia, fyr": "northmacedonia", "tanzania": "unitedrepublicoftanzania",
             "congo": "republicofthecongo", "south sudan": "southsudan", "east timor": "easttimor"}

    # Point-like events: aggregate by (rounded coord, year, prec) to shrink the bundle count.
    pts = df[df.where_prec <= 3].copy()
    polys = df[df.where_prec >= 4].copy()

    bundles: list[Bundle] = []
    # --- points and disks
    pts["lat_r"] = pts.latitude.round(3)
    pts["lon_r"] = pts.longitude.round(3)
    pts["year"] = pts.date_start.dt.year
    g = pts.groupby(["lat_r", "lon_r", "year", "where_prec"], as_index=False).agg(
        souls=("souls", "sum"), souls_low=("souls_low", "sum"), souls_high=("souls_high", "sum"),
        y0=("y0", "min"), y1=("y1", "max"), n=("id", "size"), country=("country", "first"))
    for r in g.itertuples(index=False):
        if r.where_prec == 1:
            geom, kind = Point(r.lon_r, r.lat_r), "point"
        elif r.where_prec == 2:
            geom, kind = _disk(r.lon_r, r.lat_r, 25), "polygon"
        else:
            geom, kind = _disk(r.lon_r, r.lat_r, 50), "polygon"
        bundles.append(Bundle("ucdp_ged_25_1", f"ucdp:{r.lat_r},{r.lon_r},{r.year},{r.where_prec}",
                              f"UCDP one-sided/civilian deaths, {r.country} {r.year} ({r.n} events)",
                              "mass_killing", "died", 2, 0.0, float(r.souls), float(r.souls_low), float(r.souls_high),
                              float(r.y0), float(r.y1), kind, geom))
    # --- admin-1 and country polygons, aggregated by (unit, year)
    polys["year"] = polys.date_start.dt.year
    polys["unit"] = np.where(polys.where_prec == 4, polys.adm_1.fillna(polys.country), polys.country)
    polys["lvl"] = np.where(polys.where_prec == 4, "adm1", "adm0")
    g = polys.groupby(["unit", "lvl", "year", "country"], as_index=False).agg(
        souls=("souls", "sum"), souls_low=("souls_low", "sum"), souls_high=("souls_high", "sum"),
        y0=("y0", "min"), y1=("y1", "max"), n=("id", "size"), lat=("latitude", "mean"), lon=("longitude", "mean"))
    miss = 0
    for r in g.itertuples(index=False):
        geom = None
        if r.lvl == "adm1":
            geom = adm1_by_key.get(_norm(r.unit))
        if geom is None:
            ck = alias.get(str(r.country).lower(), _norm(r.country))
            geom = adm0_by_key.get(ck)
        if geom is None:
            miss += r.souls
            geom = _disk(r.lon, r.lat, 150)
        bundles.append(Bundle("ucdp_ged_25_1", f"ucdp:{r.unit},{r.lvl},{r.year}",
                              f"UCDP one-sided/civilian deaths, {r.unit} ({r.country}) {r.year} ({r.n} events, {r.lvl} precision)",
                              "mass_killing", "died", 2, 0.0, float(r.souls), float(r.souls_low), float(r.souls_high),
                              float(r.y0), float(r.y1), "polygon", geom))
    print(f"ucdp: {len(bundles)} bundles, {df.souls.sum():.0f} souls, {miss:.0f} souls fell back to 150 km disks")
    return bundles


def run() -> list[Bundle]:
    return build_bundles(load_events())
