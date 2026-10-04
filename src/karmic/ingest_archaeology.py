"""Curated bioarchaeological evidence of interpersonal violence -> forensic bundles.

Sites where physical remains, not texts, attest killing, cannibalism, sacrifice or
execution. Scope is the genus Homo (decision 2026-09-29): Homo antecessor,
H. heidelbergensis and Neanderthals count as souls. Battlefield assemblages of
combatants (Tollense, Towton, Visby, Alken Enge, Ribemont) are excluded, matching
the design's exclusion of combat deaths.

Counts are the excavated individuals with evidence of violence (central), with
low/high bounds from the literature; where excavation covered only part of a
site the high bound carries the excavators' estimate. Dates are calibrated
ranges. Confidence is 'forensic', or 'forensic-contested' where the violent
interpretation is disputed (Krapina, Herxheim, Tell Brak, Bodo).

This table was compiled from memory of the published literature and needs a
citation pass before anything is published from it; the 'ref' field names the
principal publication as remembered.
"""
from __future__ import annotations

from shapely.geometry import Point

from .core import Bundle

BP0 = 1950  # radiocarbon 'before present' datum


def bp(older: float, younger: float) -> tuple[float, float]:
    return BP0 - older, BP0 - younger


# name, lat, lon, species, count, low, high, (year_start, year_end), manner, outcome, t_days, category, contested, ref/note
SITES = [
    ("Gran Dolina TD6, Atapuerca", 42.351, -3.520, "Homo antecessor", 11, 8, 11, bp(850000, 780000), 3, "died", 0, "mass_killing", False,
     "Butchery and consumption of at least 11 individuals, mostly children and adolescents. Fernández-Jalvo et al. 1999; Saladié et al. 2012"),
    ("Sima de los Huesos, Cranium 17", 42.351, -3.520, "Homo heidelbergensis (Neanderthal lineage)", 1, 1, 1, bp(450000, 430000), 2, "died", 0, "punishment_crime", False,
     "Two perimortem penetrating fractures above the left orbit from the same implement, two trajectories. Sala et al. 2015"),
    ("Bodo cranium, Middle Awash", 10.62, 40.55, "Homo heidelbergensis / bodoensis", 1, 0, 1, bp(640000, 550000), 1, "died", 0, "punishment_crime", True,
     "Stone-tool defleshing marks on the cranium; mortuary practice or violence undetermined. White 1986"),
    ("Krapina", 46.166, 15.870, "Homo neanderthalensis", 10, 0, 25, bp(130000, 120000), 3, "died", 0, "mass_killing", True,
     "Cut marks and fragmentation on many individuals; cannibalism versus secondary burial disputed. Russell 1987; Frayer 2006"),
    ("Moula-Guercy", 44.75, 4.73, "Homo neanderthalensis", 6, 6, 6, bp(120000, 100000), 3, "died", 0, "mass_killing", False,
     "Six Neanderthals butchered in the same way as the deer in the deposit. Defleur et al. 1999"),
    ("El Sidrón", 43.386, -5.328, "Homo neanderthalensis", 13, 12, 13, bp(50000, 48000), 3, "died", 0, "mass_killing", False,
     "Family group of 13 with cut marks and marrow extraction. Rosas et al. 2006; Lalueza-Fox et al. 2011"),
    ("Goyet, Troisième caverne", 50.447, 5.010, "Homo neanderthalensis", 5, 4, 6, bp(45500, 40500), 3, "died", 0, "mass_killing", False,
     "Butchered Neanderthal remains, some bones used as retouchers. Rougier et al. 2016"),
    ("Shanidar 3", 36.83, 44.22, "Homo neanderthalensis", 1, 1, 1, bp(50000, 45000), 2, "died", 14, "punishment_crime", False,
     "Partially healed rib wound from a thrust or thrown weapon; survived some weeks. Churchill et al. 2009"),
    ("Saint-Césaire 1", 45.75, -0.50, "Homo neanderthalensis", 1, 1, 1, bp(36000, 36000), 2, "survived", 1, "punishment_crime", False,
     "Healed sharp-force cranial injury. Zollikofer et al. 2002"),
    ("Sunghir 1", 56.18, 40.50, "Homo sapiens", 1, 1, 1, bp(34000, 33000), 2, "died", 0, "punishment_crime", False,
     "Projectile wound to the first thoracic vertebra. Trinkaus & Buzhilova 2012"),
    ("Cioclovina", 45.58, 23.13, "Homo sapiens", 1, 1, 1, bp(33000, 33000), 2, "died", 0, "punishment_crime", False,
     "Perimortem blunt-force fractures consistent with a club blow. Kranioti et al. 2019"),
    ("Maszycka Cave", 50.20, 19.82, "Homo sapiens", 10, 10, 10, bp(18000, 18000), 3, "died", 0, "mass_killing", False,
     "Magdalenian cannibalism of at least 10 individuals. Marginedas et al. 2025"),
    ("Gough's Cave", 51.28, -2.77, "Homo sapiens", 6, 5, 7, bp(14700, 14700), 3, "died", 0, "mass_killing", False,
     "Cannibalism with skull-cup manufacture and engraved bone. Bello et al. 2015"),
    ("Jebel Sahaba (Site 117)", 21.95, 31.30, "Homo sapiens", 41, 41, 61, bp(13700, 13000), 2, "died", 0, "mass_killing", False,
     "61 burials; at least 41 with projectile trauma, many with healed earlier wounds: recurrent raiding. Crevecoeur et al. 2021"),
    ("Nataruk", 4.10, 35.85, "Homo sapiens", 27, 10, 27, bp(10500, 9500), 3, "died", 0, "mass_killing", False,
     "27 unburied individuals, 10 with clear lethal trauma, some bound. Mirazón Lahr et al. 2016 (coordinates approximate)"),
    ("Ofnet", 48.82, 10.45, "Homo sapiens", 34, 34, 38, bp(9700, 9300), 3, "died", 0, "mass_killing", False,
     "Two nests of decapitated skulls, many with blunt trauma, mostly women and children. Orschiedt 2005"),
    ("Els Trocs", 42.60, 0.65, "Homo sapiens", 9, 9, 9, (-5300, -5250), 2, "died", 0, "mass_killing", False,
     "Nine individuals shot with arrows and struck; early Neolithic. Alt et al. 2020"),
    ("Herxheim", 49.15, 8.22, "Homo sapiens", 500, 300, 1000, (-5050, -4950), 3, "died", 0, "mass_killing", True,
     "Systematically butchered remains of hundreds in the enclosure ditch; cannibalism versus ritual disputed. Boulestin et al. 2009"),
    ("Talheim", 49.08, 9.04, "Homo sapiens", 34, 34, 34, (-5100, -4950), 2, "died", 0, "mass_killing", False,
     "34 killed by adze blows and arrows, thrown into a pit; young women under-represented. Wahl & König 1987"),
    ("Schletz-Asparn", 48.58, 16.50, "Homo sapiens", 67, 67, 300, (-5100, -4950), 2, "died", 0, "mass_killing", False,
     "67 excavated of an estimated 200-300 in the ditch, cranial trauma, bodies left to scavengers. Teschler-Nicola 2012"),
    ("Schöneck-Kilianstädten", 50.20, 8.85, "Homo sapiens", 26, 26, 26, (-5100, -4950), 4, "died", 0, "mass_killing", False,
     "26 killed, tibiae systematically shattered: torture or mutilation. Meyer et al. 2015"),
    ("Halberstadt", 51.90, 11.05, "Homo sapiens", 9, 9, 9, (-5100, -4950), 2, "died", 0, "mass_killing", False,
     "Nine young men executed by blows to the back of the head. Meyer et al. 2018"),
    ("Achenheim", 48.58, 7.63, "Homo sapiens", 6, 6, 6, (-4400, -4200), 4, "died", 0, "mass_killing", False,
     "Six men with multiple fractures and severed arms in a silo. Chenal et al. 2015"),
    ("Bergheim", 48.20, 7.36, "Homo sapiens", 7, 7, 7, (-4200, -4000), 4, "died", 0, "mass_killing", False,
     "Seven bodies over a layer of severed left arms. Chenal et al. 2015"),
    ("Potočani", 45.50, 17.50, "Homo sapiens", 41, 41, 41, (-4200, -4150), 2, "died", 0, "mass_killing", False,
     "41 unrelated individuals killed by blows to the head, indiscriminate by age and sex. Novak et al. 2021"),
    ("Tell Brak mass graves", 36.67, 41.06, "Homo sapiens", 200, 100, 500, (-3800, -3600), 2, "died", 0, "mass_killing", True,
     "Several hundred young adults in mass deposits; violence probable, cause not demonstrated on bone. McMahon et al. 2011"),
    ("Abydos, tomb of Djer (retainer burials)", 26.185, 31.919, "Homo sapiens", 587, 300, 600, (-3000, -2950), 3, "died", 0, "mass_killing", False,
     "Subsidiary burials around the royal tomb and enclosure, interpreted as retainer sacrifice. Petrie 1901; Bestock 2009"),
    ("Koszyce", 50.20, 20.60, "Homo sapiens", 15, 15, 15, (-2880, -2776), 2, "died", 0, "mass_killing", False,
     "Extended family of 15 killed by cranial blows and buried together by kin. Schroeder et al. 2019"),
    ("Ur, Royal Cemetery death pits", 30.963, 46.103, "Homo sapiens", 137, 137, 300, (-2600, -2450), 2, "died", 0, "mass_killing", False,
     "Attendants killed by blunt force to the head; 74 in the Great Death Pit alone. Woolley 1934; Baadsgaard et al. 2011"),
    ("Wassenaar", 52.15, 4.40, "Homo sapiens", 12, 12, 12, (-1750, -1650), 2, "died", 0, "mass_killing", False,
     "Twelve of both sexes and all ages in one grave, one with an arrowhead in the chest. Louwe Kooijmans 1993"),
    ("Anyang, Xibeigang sacrificial pits", 36.13, 114.32, "Homo sapiens", 3000, 1000, 13000, (-1250, -1050), 3, "died", 0, "mass_killing", False,
     "Thousands of decapitated and dismembered sacrificial victims in pits; oracle-bone texts give the high figure. Institute of Archaeology CASS"),
    ("Tollund Man", 56.16, 9.45, "Homo sapiens", 1, 1, 1, (-405, -380), 2, "died", 0, "punishment_crime", False,
     "Hanged; bog body. Fischer 2012"),
    ("Grauballe Man", 56.15, 9.60, "Homo sapiens", 1, 1, 1, (-400, -290), 2, "died", 0, "punishment_crime", False,
     "Throat cut; bog body. Asingh & Lynnerup 2007"),
    ("Lindow Man", 53.32, -2.28, "Homo sapiens", 1, 1, 1, (-50, 100), 4, "died", 0, "punishment_crime", False,
     "Struck, garrotted and throat cut. Stead et al. 1986"),
    ("Teotihuacan, Feathered Serpent Pyramid", 19.685, -98.845, "Homo sapiens", 200, 200, 260, (150, 250), 3, "died", 0, "mass_killing", False,
     "Sacrificial victims with hands bound behind the back in dedicatory pits. Sugiyama 2005"),
    ("Huaca de la Luna, Plaza 3A", -8.13, -78.99, "Homo sapiens", 70, 70, 100, (300, 800), 4, "died", 0, "mass_killing", False,
     "Moche captives with throats cut, defleshed and dismembered. Verano 2001; Bourget 2016"),
    ("Sandby borg", 56.55, 16.63, "Homo sapiens", 26, 26, 26, (470, 490), 2, "died", 0, "mass_killing", False,
     "Inhabitants killed in their houses and left unburied, including children. Alfsdotter et al. 2018"),
    ("Chichén Itzá, sacred cenote and chultún", 20.683, -88.568, "Homo sapiens", 100, 64, 200, (600, 1100), 3, "died", 0, "mass_killing", False,
     "Sacrificed individuals, many children; 64 boys in the chultún. Barrientos 2024"),
    ("Sacred Ridge", 37.27, -107.90, "Homo sapiens", 33, 33, 35, (800, 810), 4, "died", 0, "mass_killing", False,
     "At least 33 tortured, mutilated and processed. Potter & Chuipka 2010"),
    ("Ridgeway Hill, Weymouth", 50.652, -2.462, "Homo sapiens", 54, 54, 54, (970, 1025), 3, "died", 0, "punishment_crime", False,
     "54 Scandinavian men decapitated and buried in a disused quarry. Loe et al. 2014"),
    ("St John's College, Oxford", 51.755, -1.256, "Homo sapiens", 35, 35, 37, (960, 1020), 3, "died", 0, "mass_killing", False,
     "Young men stabbed, struck and burned, mass grave; St Brice's Day 1002 candidate. Pollard et al. 2012"),
    ("Cahokia, Mound 72", 38.655, -90.062, "Homo sapiens", 118, 53, 270, (1000, 1100), 3, "died", 0, "mass_killing", False,
     "Rows of sacrificed young women and executed men with a high-status burial. Fowler et al. 1999"),
    ("Cowboy Wash", 37.25, -108.70, "Homo sapiens", 7, 7, 7, (1150, 1150), 3, "died", 0, "mass_killing", False,
     "Seven butchered and cooked; human myoglobin in a coprolite. Marlar et al. 2000"),
    ("Punta Lobos", -10.07, -78.17, "Homo sapiens", 200, 178, 200, (1250, 1300), 3, "died", 0, "mass_killing", False,
     "Bound and blindfolded men with throats cut on the beach. Verano & Toyne 2011"),
    ("Castle Rock Pueblo", 37.35, -108.90, "Homo sapiens", 41, 41, 41, (1280, 1285), 2, "died", 0, "mass_killing", False,
     "Village destroyed, at least 41 killed and left unburied. Kuckelman et al. 2002"),
    ("Crow Creek", 43.98, -99.30, "Homo sapiens", 486, 486, 486, (1325, 1325), 3, "died", 0, "mass_killing", False,
     "486 scalped and mutilated villagers in the fortification ditch. Willey 1990"),
    ("Huanchaco, Las Llamas and Pampa la Cruz", -8.08, -79.12, "Homo sapiens", 360, 300, 400, (1400, 1500), 3, "died", 0, "mass_killing", False,
     "Chimú child sacrifices with transverse chest cuts, the largest known. Prieto et al. 2019"),
    ("Polacca Wash", 35.62, -110.10, "Homo sapiens", 30, 30, 30, (1580, 1700), 4, "died", 0, "mass_killing", False,
     "30 individuals killed and mutilated; possibly the Awat'ovi survivors. Turner & Morris 1970"),
]


def run() -> list[Bundle]:
    bundles = []
    for (name, lat, lon, species, n, lo, hi, (y0, y1), manner, outcome, t_days, cat, contested, ref) in SITES:
        conf = "forensic-contested" if contested else "forensic"
        bundles.append(Bundle("archaeology_curated", f"arch:{name}", f"{name} ({species})", cat, outcome, manner,
                              float(t_days), float(n), float(lo), float(hi), float(y0), float(y1) + 1.0, "point",
                              Point(lon, lat), confidence=conf, note=f"{species}. {ref}"))
    print(f"archaeology: {len(bundles)} sites, {sum(b.count for b in bundles):.0f} souls, "
          f"{sum(1 for b in bundles if 'contested' in b.confidence)} contested")
    return bundles
