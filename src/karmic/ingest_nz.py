"""Aotearoa New Zealand, hand-curated table -> bundles. DRAFT for review.

No georeferenced dataset exists, so this is a curated list in the manner of the
archaeological table. Three kinds of event are in scope: killing of noncombatants
and prisoners during the Musket Wars (1807-1837, intertribal), noncombatant and
prisoner killings during the New Zealand Wars (1845-1872) by either side, and
structural cruelty such as the Moriori enslavement and the Parihaka detentions.
Battles between armed parties (Moremonui, Ohaeawai, Gate Pa, Orakau and the rest)
are excluded, consistent with the design.

Musket Wars counts are the most uncertain numbers in the whole build: the pa
sieges killed inhabitants of every age after the defences fell, but the sources
are oral tradition, missionary letters and later reconstructions, and the low
and high bounds differ by a factor of three or more. They carry the confidence
'recorded-contested'. Coordinates are to the pa or settlement.

Compiled from memory of the published literature; needs a citation pass before
anything leaves the prototype.
"""
from __future__ import annotations

from shapely.geometry import Point

from .core import Bundle

# name, lat, lon, count, low, high, (y0, y1), manner, outcome, t_days, category, confidence, note
EVENTS = [
    ("Boyd, Whangaroa Harbour", -35.03, 173.75, 66, 60, 70, (1809.95, 1809.96), 3, "died", 0, "mass_killing", "recorded",
     "Crew and passengers killed and eaten by Ngati Uru and Ngati Pou after the flogging of a chief's son aboard. Salmond 1997"),
    ("Te Puna / Rangihoua reprisal", -35.17, 174.10, 60, 20, 60, (1810.2, 1810.3), 2, "died", 0, "mass_killing", "recorded-contested",
     "Whalers' reprisal for the Boyd on the wrong pa; Te Pahi's people killed. Salmond 1997"),
    ("Mauinaina and Mokoia pa, Tamaki", -36.90, 174.85, 1000, 300, 2000, (1821.85, 1821.9), 3, "died", 0, "mass_killing", "recorded-contested",
     "Hongi Hika's Ngapuhi took the Ngati Paoa pa; inhabitants killed, captives eaten or enslaved. Crosby 1999; Ballara 2003"),
    ("Te Totara pa, Thames", -37.15, 175.55, 1000, 300, 1000, (1821.95, 1822.0), 3, "died", 0, "mass_killing", "recorded-contested",
     "Ngati Maru pa taken by night after a feigned peace; inhabitants killed. Crosby 1999"),
    ("Matakitaki pa, Pirongia", -37.98, 175.20, 1000, 300, 1500, (1822.4, 1822.5), 3, "died", 0, "mass_killing", "recorded-contested",
     "Waikato pa stormed; many crushed in the trench in the panic, survivors killed or enslaved. Crosby 1999"),
    ("Mokoia Island, Rotorua", -38.08, 176.28, 300, 200, 500, (1823.1, 1823.2), 3, "died", 0, "mass_killing", "recorded-contested",
     "Te Arawa refuge on the island taken by canoe-borne Ngapuhi; inhabitants killed. Crosby 1999"),
    ("Takapuneke, Akaroa (Elizabeth affair)", -43.82, 172.95, 100, 50, 200, (1830.85, 1830.9), 4, "died", 0, "mass_killing", "recorded",
     "Te Rauparaha, carried by the brig Elizabeth, seized Te Maiharanui by treachery and destroyed the settlement; captives tortured and eaten. Evison 1993"),
    ("Kaiapoi pa", -43.38, 172.65, 200, 100, 500, (1831.9, 1832.1), 3, "died", 0, "mass_killing", "recorded-contested",
     "Ngai Tahu pa fell after a three-month siege and fire; inhabitants killed. Evison 1993"),
    ("Onawe pa, Akaroa Harbour", -43.76, 172.92, 300, 100, 500, (1832.1, 1832.2), 3, "died", 0, "mass_killing", "recorded-contested",
     "Ngai Tahu pa taken by Te Rauparaha; most inhabitants killed after the fall. Evison 1993"),
    ("Moriori, Chatham Islands: killings", -43.90, -176.50, 300, 226, 300, (1835.9, 1836.5), 3, "died", 0, "mass_killing", "recorded",
     "Ngati Mutunga and Ngati Tama invasion; Moriori who had resolved not to fight were killed, some staked out on the beach. King 1989"),
    ("Moriori, Chatham Islands: enslavement", -43.90, -176.50, 1300, 1200, 1400, (1835.9, 1863.0), 3, "survived", 28 * 365.25, "structural", "recorded",
     "Survivors enslaved, forbidden to marry or speak their language; population fell from about 1,600 to 101 by 1862. King 1989"),
    ("Wairau Affray, prisoners killed", -41.49, 173.90, 9, 9, 13, (1843.46, 1843.47), 2, "died", 0, "mass_killing", "recorded",
     "Nelson settlers who surrendered were killed by Te Rangihaeata after his wife was shot. Belich 1986"),
    ("Rangiaowhia", -37.99, 175.36, 12, 12, 30, (1864.14, 1864.15), 3, "died", 0, "mass_killing", "recorded-contested",
     "Colonial cavalry attacked the undefended supply village; people killed, some in a burning whare. O'Malley 2016"),
    ("Matawhero, Poverty Bay", -38.66, 177.95, 54, 54, 70, (1868.86, 1868.87), 3, "died", 0, "mass_killing", "recorded",
     "Te Kooti's followers killed settlers and Maori, including children. Binney 1995"),
    ("Ngatapa, prisoners executed", -38.55, 177.65, 120, 86, 130, (1869.0, 1869.02), 2, "died", 0, "mass_killing", "recorded",
     "Prisoners taken after the siege were shot on the cliff by Ngati Porou and colonial forces. Binney 1995"),
    ("Pukearuhe (White Cliffs)", -38.87, 174.62, 8, 8, 8, (1869.12, 1869.13), 2, "died", 0, "mass_killing", "recorded",
     "The Gascoigne family, two others and the missionary John Whiteley killed by Ngati Maniapoto. Cowan 1923"),
    ("Mohaka", -39.12, 177.19, 64, 57, 64, (1869.27, 1869.28), 3, "died", 0, "mass_killing", "recorded",
     "Te Kooti's raid on Ngati Pahauwera and settlers, including children. Binney 1995"),
    ("Parihaka detainees, Dunedin and Lyttelton", -45.87, 170.50, 400, 400, 420, (1879.5, 1881.5), 2, "survived", 400, "structural", "recorded",
     "Ploughmen and fencers held without trial in South Island gaols, most in Dunedin, for up to eighteen months; several died. Scott 1975; Riseborough 1989"),
    ("Maungapohatu police raid", -38.55, 177.10, 2, 2, 2, (1916.26, 1916.27), 2, "died", 0, "punishment_crime", "recorded",
     "Toko Rua and Te Maipi shot during the armed arrest of Rua Kenana. Binney et al. 1979"),
]


def run() -> list[Bundle]:
    bundles = []
    for (name, lat, lon, n, lo, hi, (y0, y1), manner, outcome, t_days, cat, conf, note) in EVENTS:
        bundles.append(Bundle("nz_curated", f"nz:{name}", name, cat, outcome, manner, float(t_days), float(n), float(lo),
                              float(hi), float(y0), float(y1), "point", Point(lon, lat), confidence=conf, note=note))
    print(f"nz: {len(bundles)} events, {sum(b.count for b in bundles):.0f} souls, "
          f"{sum(1 for b in bundles if 'contested' in b.confidence)} contested")
    return bundles
