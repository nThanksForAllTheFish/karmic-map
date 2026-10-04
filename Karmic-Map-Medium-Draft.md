# A map of the Earth at the resolution of a single life

*Draft for Medium. Figures referenced in brackets are in the project's `out/snapshots/` folder.*

I wanted to see where it happened. Not the wars, or not mainly the wars, but the cruelty: the massacres of people who could not fight back, the centuries of slavery, the camps, the lynchings, the pits of bones that are the only record of killings older than writing. I wanted it on a map of the whole Earth, coloured by how much of it had happened at each spot, and I wanted to be able to slide a window through time and watch the colour move.

I am an engineer, not a historian, and this is a personal project built over a few evenings with an AI assistant doing most of the typing. What follows is how it was designed, what it shows, and what it cannot show. The code and the design document are on GitHub, and a live copy of the map is linked at the end.

## One person at a time

The first decision was the unit. Atrocity statistics are usually events: a massacre of four hundred, a famine of three million. I did not want events. I wanted the map built from people, so that a massacre of four hundred is four hundred records that happen to share a place and a date, and so that when a name list is found for an event that was previously only a count, the placeholders are replaced one for one without changing anything else.

Each person gets a score. Written out it is

    s = O × D × M

which reads: s equals O times D times M. O is an outcome factor, D a duration factor and M a manner factor. In words, the weight of one person's suffering is how it ended, times how long it lasted, times how cruel it was.

The outcome factor turned out to be the interesting one. My first instinct was to score a death at 1 and a survivor at a half. Then I thought about what the map is supposed to measure. If it is accumulated pain over time, death is not the worst entry in the ledger; death ends the accumulation. A survivor may suffer for decades afterward, but the records almost never say so, and I did not want to invent it. So death and survival both score 1, and the duration factor carries the whole distinction. That has consequences. A person shot within an hour of capture scores less than a person who survived a year in a ghetto. Twenty years of slavery scores about seven times a shooting. The map says the ghetto outweighs the gas chamber, and the plantation outweighs both. I decided that was what a measure of suffering must say, and left it.

The duration factor is logarithmic, because the difference between an instant and a day matters more than the difference between year nine and year ten. The manner factor is a four-step integer: negligent killing, deliberate killing, deliberate killing or bondage with systematic degradation, and cruelty where the suffering was itself the purpose. Finer gradations would have implied a precision of moral judgment the sources cannot support.

## Where, and when

A person's suffering has a place, but rarely a precise one. A named prisoner at a known camp is a point. A victim of the Bengal famine is a probability distribution over a dozen districts. A person who died in the hold of a slave ship is spread along the ship's route, weighted toward the end of the voyage where mortality was highest. So every record carries a footprint, and a map cell's value is the sum over everyone of their score times the probability their suffering happened in that cell. Uncertainty about place does not lose anything; it only blurs.

Time works the same way. A massacre has a date. A person enslaved from 1820 to 1858 is spread uniformly across thirty-eight years. A Neolithic mass grave dated to a 150-year radiocarbon range is spread across the range. The viewer has a two-handled window, and the colour shows only the part of each life that falls inside it. Drag it to 1939 through 1945 and the slave trade vanishes while the camps light up. Drag it to the fifteenth century and almost everything disappears, which is the point of the next section.

The grid is hexagonal, about three quarters of a square kilometre per cell at the finest level, with the cells rolled up to coarser parents as you zoom out. The colour scale is logarithmic, because the cell containing Auschwitz and the cell containing one recorded murder differ by six orders of magnitude.

## What the map actually shows

[Figure: global view, all years, ocean transits on]

The first thing you see is the Atlantic. The Trans-Atlantic Slave Trade Database records 36,000 voyages with embarkation and landing ports and the numbers who boarded and who survived, which under this scoring produces a glowing band from the Bights of Benin and Biafra and the Angolan coast across to Bahia, Rio de Janeiro and the Caribbean. There is a toggle to turn the sea transits off, and with them off the land pattern reads clearly: the Brazilian and Caribbean plantation regions, the African embarkation coast, the camps across central Europe, and the post-1989 conflict zones from the Sahel through the Great Lakes to Syria and Afghanistan, which come from the Uppsala Conflict Data Program's georeferenced events.

[Figure: Australia, 1788 to 1930]

Australia was blank in the first build, and the reason was not that nothing happened there. None of my sources reached it. Lyndall Ryan and her colleagues at the University of Newcastle spent a decade documenting colonial frontier massacres, 438 sites of six or more killed, each with coordinates, a date, the recorded dead, the attackers, the weapons and a corroboration rating. It is the only dataset of its kind that I know of anywhere in the world, and once it was in, the continent lit up from the Victorian western districts to the Kimberley. New Zealand has nothing comparable, so it has a hand-curated table of nineteen events, and that table is a draft I have not yet verified against the sources.

[Figure: prehistory, before 3000 BCE]

Set the window to before writing and the map is nearly dark, with a few dozen points. These are the sites where bone, not text, is the record: the Homo antecessor children butchered at Gran Dolina some 800,000 years ago, the skull at Sima de los Huesos with two blows above the left eye, the Neanderthals of El Sidrón and Moula-Guercy, Jebel Sahaba, Nataruk, the massacre pits of Neolithic Germany. I decided early that human meant the genus, not the species, so a Neanderthal killed and eaten by other Neanderthals is a soul on this map. Skeletal evidence cannot usually say who did it or why. It can say a great deal from an assemblage: a pit of the old, the women and the children with blows to the back of the head and no defensive wounds is an execution, not a battle.

## What it cannot show

This is a map of recorded cruelty, and recording is uneven. The camps of the Third Reich are documented to the individual. The Mongol destruction of Khwarazm is documented by a handful of chroniclers giving round numbers in the millions. The wars of pre-colonial Africa and the Americas are documented mainly by archaeology and by the people who conquered them. A naive reading would conclude that Europe is the darkest place on Earth and Africa one of the lightest, and that conclusion would be wrong. The design has three answers: a time window, so you can watch the record begin region by region; a confidence class on every record, so that souls inferred from demographic collapse sit in a separate overlay from souls counted in a ledger; and a documentation-density layer, which shows for each cell how many independent sources underlie it. The first exists. The other two are not built yet.

The frontier massacres are a case in point. Ryan's 10,600 recorded dead are a fraction of the frontier toll, because the killings were concealed, and the demographic collapse of Aboriginal Australia, from perhaps 750,000 people in 1788 to under 100,000 by 1900, is mostly disease, dispossession and starvation. That number belongs on the map, but in the modeled overlay with its uncertainty stated, not in the recorded layer.

The biggest holes in the current build are the twentieth century's largest totals. The Soviet, Chinese and Cambodian events are absent except where Wikidata happens to have a camp with a death count. Yad Vashem's 4.9 million names would turn the European camp points into people. Slavery in the Americas should be scored from census data by person-years, not from landings. Each of these is a week's work and a licence to check, and the schema takes all of them without change.

## A memorial that happens to be quantitative

I have come to think of the map as a memorial rather than a ranking. That framing decided several things: keeping names where they exist, refusing to let acts of mercy subtract from a place's score, showing the ocean because the ocean is part of the Earth, and never presenting the result as a contest between peoples' suffering. The viewer's click-through to the events and names behind a cell is not built yet, and the design calls it a requirement rather than a nicety. Until it exists, the colour is an abstraction. When it does, every hexagon opens onto the people it stands for.

The code, the design document and a live copy of the viewer are on GitHub. The two hand-curated tables are marked as drafts, and if you know the literature on any of those sites, corrections are welcome.

Repository: https://github.com/nThanksForAllTheFish/karmic-map
Live viewer: https://nthanksforallthefish.github.io/karmic-map/
