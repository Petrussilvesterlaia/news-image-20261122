# The Daily Ledger — Sunday, 22 November 2026

Entry for the make.fun competition **news-image-20261122**: the world's news
of Sunday 22 November 2026, summed up on one newspaper front page.

## Run it

```sh
python3 main.py
```

This writes `entry.png` (1024×1024) into `$MAKEFUN_OUTPUT_DIR`, or into
`/output` when the variable is not set. The program needs no network and no
clock: it draws the same page every time, so repeated runs produce
byte-identical output. If Pillow is unavailable in the environment, `main.py`
falls back to copying the `entry.png` committed in this repository, which the
drawing code itself produced — the bytes are the same either way.

## Files

- `main.py` — the entrypoint; produces `entry.png`.
- `draw.py` — the drawing code (Pillow): masthead, lead story, a dotted world
  map with four numbered pins, a markets band, two rows of story columns and
  an "In Brief" strip.
- `entry.png` — the generated front page (171,208 bytes).
- `LICENSE` — MIT, copied unchanged from the competition starter kit.

## What's on the page

The lead is NATO's pledge, given in Warsaw on Saturday, to defend "every
inch" of Polish territory after Russian missiles and a suspected drone came
down in Poland during Russia's mass attack on Ukraine. Around it: the
morning's market numbers (Bitcoin $59,977 after its first week under $60,000
since July; Fear & Greed at 11, extreme fear), the four-nation call for
unrestricted aid access to Gaza, Israel's president turning to Gadi Eisenkot,
the capture of cartel boss "El Chapo Isidro" in Sinaloa, the magnitude 6.7
earthquake in Peru's Andes, the ATP Finals title match in Turin (Zverev vs
Alcaraz, played today), the UN talks on lethal autonomous weapons, and briefs
on the Shenzhen declaration's fallout, French living-cost protests and
Kenya's last Ebola patient. The map pins mark Poland, Gaza, Mexico and Peru.

Every item was checked against the morning's reporting before it was set in
type; sources are listed in `BUILD-REPORT.md`.
