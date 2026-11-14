# HeadCalc: notes for Claude

A free Streamlit tool that calculates the inside volume of tank heads (oval/ellipsoidal and torispherical F&D).
**Public** repo `Mervinadur/headcalc`. Live URL: not recorded yet, so ask the user. **This repo is public, so keep personal and
project details out of the files here** (they belong in `~/CLAUDE.md` and memory).
See also `~/CLAUDE.md` (targeted edits, pull before push).

## Where things are
- `head_volume.py`: pure math with no Streamlit. Lengths can be in any unit, as long as they all match.
  - `oval_head(W, H, h_dish, SF)`
  - `torispherical_geometry(D_i, CR, KR)`, `torispherical_head(...)`: exact closed form (knuckle torus + crown cap)
  - `*_profile()`: points for the sketch
  - Results come back as `HeadResult(dish_volume, flange_volume, dish_depth, total_volume)`.
- `diagrams.py`: inline SVG dimensioned input diagrams (`oval_svg`, `torispherical_svg`, `svg_html`).
- `app.py`: Streamlit UI. Unit picker (mm/cm/m/in/ft); results in L, m³, US/Imp gal and ft³; to-scale profile (altair).
- `requirements.txt`: streamlit, pandas, altair.

## Rules
- Engineering math is tested Python, never LLM arithmetic. There's no test file yet, so check changes against known values:
  - ASME F&D (CR = D, KR = 0.06·D): dish ≈ 0.0810·D³ (verified 2026-11-14: 0.0810)
  - Oval: V = (2/3)·π·(W/2)·(H/2)·h_dish (verified 2026-11-14)
- Streamlit doesn't run in Termux, but `head_volume.py` does (plain Python): `python3 -c "from head_volume import …"`.

## Status (update this before ending a session)
- 2026-11-06: two commits, the initial app and the input diagrams. It works as far as known. No open work.
- 2026-11-14: CLAUDE.md added. Possible next steps (not started, ask first): a `tests/` file with the checks above,
  2:1 semi-elliptical and hemispherical heads.
