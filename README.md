# HeadCalc

A free Streamlit tool to calculate the **inside volume of tank heads**.

## Supported heads

**Oval / Ellipsoidal** (elliptical tank cross-section)
- `W` – total internal width of the tank base
- `H` – total internal height of the tank base
- `h_dish` – inside depth of the ellipsoidal dish (tangent line to apex)
- `SF` – straight flange length

**Torispherical** (flanged & dished)
- `D_i` – inside diameter of the shell
- `CR` – crown radius (inside dish radius)
- `KR` – knuckle radius (inside transition radius)
- `SF` – straight flange length

Results are shown in litres, m³, US/Imperial gallons and ft³, with a to-scale profile sketch.
Inputs can be entered in mm, cm, m, in or ft.

## Formulas

- Oval: `V = π·(W/2)·(H/2)·(2/3·h_dish + SF)`
- Torispherical: exact closed-form solid of revolution (knuckle torus section + crown spherical cap) plus `π·(D_i/2)²·SF`.
  Sanity check: an ASME F&D head (CR = D, KR = 0.06·D) gives ≈ 0.0810·D³.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Deploy for free on [Streamlit Community Cloud](https://share.streamlit.io): pick this repo, branch `main`, main file `app.py`.
