#!/usr/bin/env bash
# Fetch the raw sources into data/raw/. Each is published by its owner under its own
# terms (see DATA_SOURCES.md). Total about 340 MB.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw && cd data/raw

echo "UCDP GED 25.1"
curl -sSL -o ged251-csv.zip https://ucdp.uu.se/downloads/ged/ged251-csv.zip
unzip -o -q ged251-csv.zip            # -> GEDEvent_v25_1.csv

echo "Natural Earth"
curl -sSL -o ne_10m_admin_1.zip https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip
mkdir -p ne_admin1 && unzip -o -q ne_10m_admin_1.zip -d ne_admin1
curl -sSL -o ne_110m_countries.zip https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip
mkdir -p ne_countries && unzip -o -q ne_110m_countries.zip -d ne_countries

echo "SlaveVoyages 2019 export"
curl -sSL -o tastdb-exp-2019.csv https://www.slavevoyages.org/documents/download/tastdb-exp-2019.csv
# tast_place_codes.json (port code -> name, parsed from the SPSS codebook) ships in the repo
cp ../tast_place_codes.json . 2>/dev/null || true

echo "Seguin & Rigby lynching inventory (OSF)"
curl -sSL -o lynching_seguin_rigby.csv https://osf.io/download/tvf53/

echo "Census 2023 county gazetteer"
curl -sSL -o gaz_counties_2023.zip https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteers/2023_Gaz_counties_national.zip
unzip -o -q gaz_counties_2023.zip     # -> 2023_Gaz_counties_national.txt

echo "Colonial Frontier Massacres (TLCMap layer 1336)"
curl -sSL -o colonial_frontier_massacres_tlcmap.csv https://tlcmap.org/layers/1336/csv

echo "Wikidata camps"
curl -s -G https://query.wikidata.org/sparql -H "Accept: text/csv" -H "User-Agent: karmic-map/0.1" \
  --data-urlencode 'query=SELECT ?camp ?campLabel ?typeLabel ?coord ?deaths ?inception ?dissolved ?countryLabel WHERE {
  ?camp wdt:P31 ?type . ?type wdt:P279* wd:Q152081 .
  ?camp wdt:P625 ?coord .
  OPTIONAL { ?camp wdt:P1120 ?deaths } OPTIONAL { ?camp wdt:P571 ?inception }
  OPTIONAL { ?camp wdt:P576 ?dissolved } OPTIONAL { ?camp wdt:P17 ?country }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }' -o wikidata_camps.csv

echo "done:"; ls -la
