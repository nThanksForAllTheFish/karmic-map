"""Trans-Atlantic Slave Trade Database (2019 export, 36,108 voyages) -> bundles.

Per voyage, up to three bundles (the design's fourth, capture in the interior,
is left out of the prototype because the source does not locate it):

  1. confinement at the embarkation port       point, survived, M=3, t=60 d
  2. the Middle Passage                        route, M=3, t=VOY2IMP days (median if missing)
     deaths at sea = VYMRTIMP, else SLAXIMP-SLAMIMP; under O=1 dead and survivors
     score alike, so the bundle carries SLAXIMP souls and records deaths in the note
  3. lifetime of bondage at the destination    polygon over the landing region,
                                               died, M=3, t=20 years (prototype constant)
                                               temporal footprint year..year+20

Place codes are the SPSS codes of the database. The site's geo API needs a
token, so coordinates come from a curated table below (covering ~97% of souls
at each end); other codes fall back to their region strip or polygon.
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import Geod
from shapely.geometry import Point, LineString, MultiPolygon
from shapely.ops import unary_union

from .core import Bundle

RAW = "data/raw/tastdb-exp-2019.csv"
CODES = "data/raw/tast_place_codes.json"
NE_ADM1 = "data/raw/ne_admin1/ne_10m_admin_1_states_provinces.shp"

# ---- port points: code -> (lon, lat, region_key) --------------------------
PORTS: dict[int, tuple[float, float, str]] = {
    # Senegambia (601)
    60104: (-15.60, 11.86, "601"), 60105: (-16.17, 12.27, "601"), 60108: (-16.60, 13.40, "601"),
    60109: (-17.40, 14.67, "601"), 60114: (-15.60, 11.86, "601"), 60118: (-16.50, 16.03, "601"),
    60126: (-23.51, 14.92, "cv"), 60199: (0, 0, "601"),
    # Sierra Leone (602)
    60202: (-13.05, 8.57, "602"), 60207: (-13.23, 8.48, "602"), 60208: (-11.60, 7.00, "602"),
    60210: (-13.80, 9.50, "602"), 60213: (-14.05, 10.05, "602"), 60220: (-13.20, 8.50, "602"), 60299: (0, 0, "602"),
    # Windward Coast (603)
    60302: (-10.05, 5.87, "603"), 60306: (-11.37, 6.75, "603"), 60309: (-5.02, 5.13, "603"), 60399: (0, 0, "603"),
    # Gold Coast (604)
    60404: (-0.20, 5.55, "604"), 60408: (-1.12, 5.17, "604"), 60412: (-1.25, 5.10, "604"),
    60414: (-0.18, 5.55, "604"), 60415: (-1.35, 5.08, "604"), 60499: (0, 0, "604"),
    # Bight of Benin (605)
    60501: (5.60, 6.30, "605"), 60502: (2.10, 6.35, "605"), 60506: (2.60, 6.50, "605"), 60507: (2.88, 6.42, "605"),
    60509: (3.98, 6.58, "605"), 60510: (1.82, 6.28, "605"), 60511: (1.60, 6.23, "605"), 60514: (2.05, 6.35, "605"),
    60515: (2.09, 6.36, "605"), 60517: (3.39, 6.45, "605"), 60523: (2.60, 6.50, "605"), 60599: (0, 0, "605"),
    # Bight of Biafra (606)
    60605: (7.17, 4.43, "606"), 60608: (8.32, 4.95, "606"), 60609: (9.70, 4.05, "606"), 60620: (9.45, 0.39, "606"),
    60622: (7.03, 4.57, "606"), 60668: (7.40, 1.61, "st"), 60673: (6.73, 0.34, "st"), 60676: (7.0, 1.0, "st"), 60699: (0, 0, "606"),
    # West Central Africa (607)
    60703: (13.10, -7.85, "607"), 60707: (13.40, -12.58, "607"), 60711: (12.19, -5.55, "607"), 60716: (12.30, -5.90, "607"),
    60717: (12.40, -6.07, "607"), 60724: (11.80, -4.65, "607"), 60725: (12.17, -5.35, "607"), 60734: (13.23, -8.84, "607"),
    60740: (-5.72, -15.94, "sh"), 60799: (0, 0, "607"),
    # Southeast Africa (608)
    60811: (47.5, -19.0, "mg"), 60820: (40.73, -15.03, "608"), 60822: (36.89, -17.88, "608"), 60899: (0, 0, "608"),
    # Africa other (609)
    60912: (0, 0, "603"), 60916: (0, 0, "602"), 60917: (0, 0, "604"), 60999: (0, 0, "609"),
    # Brazil
    50102: (-44.30, -2.53, "br_ma"), 50103: (-48.50, -1.46, "br_pa"), 50199: (-44.30, -2.53, "br_ma"),
    50299: (-38.51, -12.97, "br_ba"), 50399: (-34.88, -8.05, "br_pe"),
    50406: (-41.33, -21.75, "br_rj"), 50412: (-44.23, -23.15, "br_rj"), 50416: (-41.78, -22.37, "br_rj"),
    50422: (-43.17, -22.91, "br_rj"), 50423: (-43.17, -22.91, "br_rj"), 50424: (-44.5, -23.0, "br_rj"),
    50430: (-45.41, -23.80, "br_sp"), 50499: (-43.17, -22.91, "br_rj"),
    # Caribbean and mainland Spanish America
    31299: (-66.11, 18.47, "pr"), 31306: (-81.20, 23.04, "cu"), 31312: (-82.38, 23.13, "cu"), 31316: (-81.58, 23.05, "cu"),
    31323: (-75.82, 20.02, "cu"), 31324: (-79.98, 21.80, "cu"), 31399: (-82.38, 23.13, "cu"),
    32110: (-68.93, 12.11, "cw"), 32150: (-62.98, 17.48, "se"), 32240: (-55.20, 5.85, "sr"),
    33401: (-61.85, 17.12, "ag"), 33599: (-62.73, 17.30, "kn"), 33601: (-62.58, 17.15, "kn"), 33899: (-61.39, 15.30, "dm"),
    34299: (-59.62, 13.10, "bb"), 34399: (-61.22, 13.16, "vc"), 34499: (-61.75, 12.05, "gd"), 34599: (-61.52, 10.65, "tt"),
    35107: (-77.92, 18.47, "jm"), 35114: (-76.79, 17.97, "jm"), 35199: (-76.79, 17.97, "jm"),
    35304: (-58.16, 6.80, "gy"), 35599: (-76.79, 17.97, "wi"),
    36199: (-61.18, 14.74, "mq"), 36201: (-61.73, 16.00, "gp"), 36301: (-52.33, 4.93, "gf"),
    36403: (-72.20, 19.76, "ht"), 36404: (-73.75, 18.19, "ht"), 36409: (-72.63, 18.51, "ht"), 36412: (-72.34, 18.54, "ht"),
    36414: (-72.70, 19.11, "ht"), 36499: (-72.34, 18.54, "ht"),
    37010: (-64.75, 17.75, "vi"), 37020: (-64.93, 18.34, "vi"), 37099: (-64.93, 18.34, "vi"),
    39002: (-76.79, 17.97, "wi"), 39099: (-76.79, 17.97, "wi"),
    41201: (-96.14, 19.19, "mx"), 41203: (-96.14, 19.19, "mx"), 41207: (-75.51, 10.40, "co"), 41299: (-75.51, 10.40, "sp_cc"),
    42001: (-58.38, -34.60, "rp"), 42002: (-56.19, -34.90, "rp"), 42099: (-58.38, -34.60, "rp"),
    # North America
    21111: (-76.50, 37.24, "us_va"), 21199: (-76.50, 37.24, "us_va"), 21302: (-79.93, 32.78, "us_sc"), 21399: (-79.93, 32.78, "us_sc"),
    # unspecified Americas
    80299: (-70.0, 15.0, "wi"), 80499: (-75.51, 10.40, "sp_cc"),
    # additions after first unplaced-code audit
    32150: (-62.98, 17.48, "se"), 33299: (-64.62, 18.43, "vg"), 21401: (-81.09, 32.08, "us_ga"), 21499: (-81.09, 32.08, "us_ga"),
    31199: (-70.5, 18.9, "hisp"), 31106: (-69.90, 18.47, "do"), 31107: (-70.50, 18.35, "do"), 36599: (-61.5, 15.5, "fr_c"),
    34601: (-60.74, 11.18, "tt"), 34699: (-60.74, 11.18, "tt"), 33799: (-62.20, 16.75, "ms"),
    21099: (-76.49, 38.98, "us_md"), 21006: (-76.50, 38.50, "us_md"), 21001: (-76.49, 38.98, "us_md"), 21003: (-76.90, 38.40, "us_md"), 21013: (-76.55, 38.93, "us_md"),
    35299: (-77.35, 25.08, "bs"), 35203: (-77.35, 25.08, "bs"), 34199: (-60.99, 14.01, "lc"), 20699: (-74.01, 40.71, "us_ny"),
    31499: (-78.0, 21.0, "sp_car"), 21601: (-90.07, 29.95, "us_la"), 21602: (-89.40, 29.10, "us_la"), 21603: (-90.07, 29.95, "us_la"),
    21604: (-88.89, 30.40, "us_ms"), 21605: (-88.89, 30.40, "us_ms"), 10203: (-9.14, 38.72, "pt"), 10104: (-6.29, 36.53, "es"),
    20404: (-71.06, 42.36, "us_ma"), 20199: (-71.31, 41.49, "us_ri"), 21599: (-81.31, 29.90, "us_fl"), 21504: (-81.78, 24.56, "us_fl"),
    21501: (-81.31, 29.90, "us_fl"), 21999: (-79.0, 35.0, "us_all"), 21299: (-76.70, 34.70, "us_nc"), 38199: (-62.83, 17.90, "bl"),
    20902: (-75.17, 39.95, "us_pa"), 80599: (-70.0, 15.0, "wi"), 80399: (0, 0, "609"),
}

# ---- African coastal strips: region key -> waypoints (lon, lat) -----------
STRIPS = {
    "601": [(-16.5, 16.0), (-17.4, 14.7), (-16.6, 13.4), (-16.7, 12.6), (-15.6, 11.9)],
    "602": [(-14.6, 10.6), (-13.8, 9.5), (-13.2, 8.5), (-12.5, 7.5), (-11.6, 7.0)],
    "603": [(-11.4, 6.7), (-10.8, 6.3), (-10.0, 5.9), (-7.7, 4.4), (-5.0, 5.1), (-3.3, 5.1)],
    "604": [(-2.2, 4.9), (-1.35, 5.08), (-1.1, 5.2), (-0.2, 5.55), (1.0, 5.9)],
    "605": [(1.6, 6.2), (2.1, 6.35), (2.6, 6.5), (3.4, 6.45), (5.0, 5.7)],
    "606": [(6.2, 4.3), (7.2, 4.4), (8.3, 4.95), (9.7, 4.0), (9.45, 0.4), (8.7, -0.6)],
    "607": [(11.8, -4.65), (12.2, -5.55), (12.4, -6.05), (13.1, -7.85), (13.2, -8.8), (13.4, -12.6)],
    "608": [(40.7, -15.0), (36.9, -17.9), (35.4, -23.9)],
}
STRIP_ISLANDS = {"cv": (-23.51, 14.92), "st": (6.73, 0.34), "sh": (-5.72, -15.94), "mg": (47.5, -19.0),
                 "se": (-62.98, 17.48), "vg": (-64.62, 18.43), "ms": (-62.20, 16.75), "bl": (-62.83, 17.90),
                 "pt": (-9.14, 38.72), "es": (-6.29, 36.53)}

# ---- destination regions from Natural Earth admin-1: key -> (admin, name or None)
REGIONS = {
    "br_ma": ("Brazil", ["Maranhão"]), "br_pa": ("Brazil", ["Pará"]), "br_ba": ("Brazil", ["Bahia"]),
    "br_pe": ("Brazil", ["Pernambuco"]), "br_rj": ("Brazil", ["Rio de Janeiro"]), "br_sp": ("Brazil", ["São Paulo"]),
    "pr": ("Puerto Rico", None), "cu": ("Cuba", None), "cw": ("Curaçao", None),     "sr": ("Suriname", None), "ag": ("Antigua and Barbuda", None), "kn": ("Saint Kitts and Nevis", None),
    "dm": ("Dominica", None), "bb": ("Barbados", None), "vc": ("Saint Vincent and the Grenadines", None),
    "gd": ("Grenada", None), "tt": ("Trinidad and Tobago", None), "jm": ("Jamaica", None), "gy": ("Guyana", None),
    "mq": ("France", ["Martinique"]), "gp": ("France", ["Guadeloupe"]), "gf": ("France", ["Guyane française"]),
    "ht": ("Haiti", None), "vi": ("United States Virgin Islands", None), "mx": ("Mexico", ["Veracruz"]),
    "co": ("Colombia", ["Bolívar", "Atlántico"]), "rp": ("Argentina", ["Ciudad de Buenos Aires", "Buenos Aires"]),
    "us_va": ("United States of America", ["Virginia"]), "us_sc": ("United States of America", ["South Carolina"]),
    "us_ga": ("United States of America", ["Georgia"]), "us_md": ("United States of America", ["Maryland"]),
    "us_ny": ("United States of America", ["New York"]), "us_la": ("United States of America", ["Louisiana"]),
    "us_ms": ("United States of America", ["Mississippi"]), "us_ma": ("United States of America", ["Massachusetts"]),
    "us_ri": ("United States of America", ["Rhode Island"]), "us_fl": ("United States of America", ["Florida"]),
    "us_nc": ("United States of America", ["North Carolina"]), "us_pa": ("United States of America", ["Pennsylvania"]),
    "do": ("Dominican Republic", None), "bs": ("The Bahamas", None), "lc": ("Saint Lucia", None),
}
REGION_UNIONS = {"wi": ["jm", "bb", "ag", "kn", "dm", "vc", "gd", "mq", "gp", "ht", "cu"], "sp_cc": ["co", "mx", "cu", "pr"],
                 "hisp": ["ht", "do"], "fr_c": ["mq", "gp", "ht"], "sp_car": ["cu", "pr", "do"],
                 "us_all": ["us_va", "us_sc", "us_ga", "us_md", "us_ny", "us_la", "us_nc"]}

geod = Geod(ellps="WGS84")


def _region_shapes():
    adm1 = gpd.read_file(NE_ADM1)[["name", "name_en", "admin", "geometry"]]
    shapes = {}
    for k, (admin, names) in REGIONS.items():
        sel = adm1[adm1.admin == admin]
        if names:
            sel = sel[sel.name.isin(names) | sel.name_en.isin(names)]
        if len(sel) == 0:
            print("  region missing in Natural Earth:", k, admin, names)
            continue
        shapes[k] = unary_union(sel.geometry.values)
    for k, parts in REGION_UNIONS.items():
        shapes[k] = unary_union([shapes[p] for p in parts if p in shapes])
    for k, wps in STRIPS.items():
        shapes[k] = LineString(wps).buffer(0.35)
    shapes["609"] = unary_union([shapes[k] for k in ["601", "602", "603", "604", "605", "606", "607"]])
    for k, (lon, lat) in STRIP_ISLANDS.items():
        shapes[k] = Point(lon, lat).buffer(0.3)
    return shapes


def _port_point(code: int, shapes) -> tuple[Point | None, str | None]:
    """Point for a port code; region-strip representative point for unspecified codes."""
    rec = PORTS.get(code)
    if rec is None:
        # fall back to region by prefix (first three digits), then to broad Africa/Americas
        pref = str(code)[:3]
        if pref in STRIPS or pref == "609":
            return None, pref
        for k in PORTS:
            if str(k)[:3] == pref:
                lon, lat, rk = PORTS[k]
                return (Point(lon, lat) if lon or lat else None), rk
        return None, None
    lon, lat, rk = rec
    return (Point(lon, lat) if (lon or lat) else None), rk


def _route(p0: Point, p1: Point, via_cape: bool) -> LineString:
    pts = [(p0.x, p0.y)]
    if via_cape:
        pts.append((18.0, -36.0))
    pts.append((p1.x, p1.y))
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = geod.npts(x0, y0, x1, y1, 40)
        out.extend([(x0, y0)] + seg)
    out.append(pts[-1])
    return LineString(out)


def run() -> list[Bundle]:
    df = pd.read_csv(RAW, low_memory=False).copy()
    import warnings; warnings.simplefilter("ignore", pd.errors.PerformanceWarning)
    shapes = _region_shapes()
    names = json.load(open(CODES))
    med_voy = float(df.VOY2IMP.median())
    bundles: list[Bundle] = []
    un_emb = un_dis = 0.0

    # aggregate voyages by (embark code, disembark code, 5-year bin) to keep bundle count sane
    df["bin"] = (df.YEARAM // 5) * 5
    df["emb"] = df.MJBYPTIMP.fillna(60999).astype(int)
    df["dis"] = df.MJSLPTIMP.fillna(80299).astype(int)
    df["deaths"] = df.VYMRTIMP.where(df.VYMRTIMP.notna(), (df.SLAXIMP - df.SLAMIMP).clip(lower=0))
    df["voy"] = df.VOY2IMP.fillna(med_voy)
    g = df.groupby(["emb", "dis", "bin"], as_index=False).agg(
        embarked=("SLAXIMP", "sum"), landed=("SLAMIMP", "sum"), deaths=("deaths", "sum"),
        voy=("voy", "mean"), n=("VOYAGEID", "size"), y0=("YEARAM", "min"), y1=("YEARAM", "max"))

    for r in g.itertuples(index=False):
        emb_pt, emb_reg = _port_point(r.emb, shapes)
        dis_pt, dis_reg = _port_point(r.dis, shapes)
        emb_name = names.get(str(r.emb), str(r.emb))
        dis_name = names.get(str(r.dis), str(r.dis))
        label = f"{emb_name} -> {dis_name}, {int(r.y0)}-{int(r.y1)} ({r.n} voyages)"
        y0, y1 = float(r.y0), float(r.y1) + 1.0
        # 1. confinement at embarkation
        if r.embarked > 0:
            if emb_pt is not None:
                bundles.append(Bundle("slavevoyages_2019", f"sv:emb:{r.emb}:{r.bin}", f"Embarkation at {emb_name}: {label}",
                                      "structural", "survived", 3, 60.0, r.embarked, r.embarked * 0.9, r.embarked * 1.1,
                                      y0, y1, "point", emb_pt))
            elif emb_reg in shapes:
                bundles.append(Bundle("slavevoyages_2019", f"sv:emb:{r.emb}:{r.bin}", f"Embarkation, {emb_name}: {label}",
                                      "structural", "survived", 3, 60.0, r.embarked, r.embarked * 0.9, r.embarked * 1.1,
                                      y0, y1, "polygon", shapes[emb_reg]))
            else:
                un_emb += r.embarked
        # 2. Middle Passage
        p0 = emb_pt or (shapes[emb_reg].centroid if emb_reg in shapes else None)
        p1 = dis_pt or (shapes[dis_reg].centroid if dis_reg in shapes else None)
        if r.embarked > 0 and p0 is not None and p1 is not None:
            via_cape = emb_reg in ("608", "mg")
            bundles.append(Bundle("slavevoyages_2019", f"sv:voy:{r.emb}:{r.dis}:{r.bin}", f"Middle Passage: {label}",
                                  "structural", "died" if r.deaths > 0 else "survived", 3, float(r.voy),
                                  r.embarked, r.embarked * 0.9, r.embarked * 1.1, y0, y1, "route", _route(p0, p1, via_cape),
                                  note=f"{r.deaths:.0f} died at sea"))
        # 3. lifetime bondage at destination
        if r.landed > 0:
            if dis_reg in shapes:
                bundles.append(Bundle("slavevoyages_2019", f"sv:bond:{r.dis}:{r.bin}", f"Bondage after landing at {dis_name}: {label}",
                                      "structural", "died", 3, 20 * 365.25, r.landed, r.landed * 0.9, r.landed * 1.1,
                                      y0, y1 + 20.0, "polygon", shapes[dis_reg]))
            elif dis_pt is not None:
                bundles.append(Bundle("slavevoyages_2019", f"sv:bond:{r.dis}:{r.bin}", f"Bondage after landing at {dis_name}: {label}",
                                      "structural", "died", 3, 20 * 365.25, r.landed, r.landed * 0.9, r.landed * 1.1,
                                      y0, y1 + 20.0, "polygon", dis_pt.buffer(0.5)))
            else:
                un_dis += r.landed
    print(f"slavevoyages: {len(bundles)} bundles from {len(g)} port-pair bins; embarked {df.SLAXIMP.sum():.0f}, "
          f"landed {df.SLAMIMP.sum():.0f}; unplaced embarked {un_emb:.0f}, unplaced landed {un_dis:.0f}")
    return bundles
