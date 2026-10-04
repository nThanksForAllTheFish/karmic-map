# Data sources and licences

Raw downloads are not in this repository. Run `scripts/fetch_data.sh` to obtain
them from their publishers; the terms below apply to what you download. The
derived cell tables in `out/viewer/` and `docs/data/` aggregate all of these and
are therefore released non-commercially (CC BY-NC-SA 4.0).

## Uppsala Conflict Data Program, Georeferenced Event Dataset 25.1

Davies, S., Pettersson, T., Sollenberg, M. & Öberg, M. (2025). Organized violence 1989–2024,
and the challenges of identifying civilian victims. Journal of Peace Research 62(4).
Sundberg, R. & Melander, E. (2013). Introducing the UCDP Georeferenced Event Dataset.
Journal of Peace Research 50(4). https://ucdp.uu.se/downloads/
Free to use with citation. Used here: one-sided violence in full; civilian deaths from
state-based and non-state conflict; combatant deaths excluded.

## Trans-Atlantic Slave Trade Database (SlaveVoyages), 2019 export

SlaveVoyages Consortium. Trans-Atlantic Slave Trade Database. https://www.slavevoyages.org
Check the current terms on the site's Downloads page before redistributing; this project
does not redistribute the CSV. Place-code coordinates in `ingest_slavevoyages.py` were
compiled by hand from the SPSS codebook and public gazetteers.

## Colonial Frontier Massacres in Australia, 1788–1930

Ryan, L., Richards, J., Pascoe, W., Debenham, J., Gilbert, S., Anders, R. J., Brown, M.,
Smith, R., Price, D. & Newley, J. Colonial Frontier Massacres in Australia, 1788–1930.
Centre for 21st Century Humanities, University of Newcastle, Stage 5.0, 2024.
https://c21ch.newcastle.edu.au/colonialmassacres/ ; archived at the Australian Data Archive,
doi:10.26193/L0WEID ; republished as Time Layered Cultural Map layer 1336.
Licence CC BY-NC 4.0. The project's terms ask that the data be re-used only in a context
respectful to Aboriginal and Torres Strait Islander people. Readers should be aware the
sites and descriptions concern the deaths of named communities' ancestors.

## Seguin & Rigby (2019) lynching inventory

Seguin, C. & Rigby, D. (2019). National Crimes: A New National Data Set of Lynchings in the
United States, 1883 to 1941. Socius 5. Data at https://osf.io/kr8yc/
This is the 1,328-victim supplement outside the Tolnay–Beck South; the Tolnay–Beck core is
not openly downloadable and is not included.

## Wikidata

Items that are instances of concentration camp or its subclasses, with coordinates and,
where present, number of deaths (P1120). CC0. Quality is uneven; this stands in for the
USHMM Encyclopedia of Camps and Ghettos, which is not published as data.

## Natural Earth

Admin-0 countries (110m) and admin-1 states and provinces (10m). Public domain.
Used for footprint polygons and present-day country label points.

## United States Census Bureau, 2023 Gazetteer

County internal points, public domain. Used to place lynching records by county.

## Curated tables in this repository

`ingest_archaeology.py` (bioarchaeological sites, genus Homo, ~800 kya onward) and
`ingest_nz.py` (Aotearoa New Zealand) were compiled from the published literature and each
entry names its principal source. Both are drafts awaiting a citation pass; see HANDOFF.md.
