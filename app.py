import altair as alt
import pandas as pd
import streamlit as st

from diagrams import oval_svg, svg_html, torispherical_svg
from head_volume import oval_head, oval_profile, torispherical_head, torispherical_profile

st.set_page_config(page_title="HeadCalc – Tank Head Volume", page_icon="🛢️", layout="centered")

# length unit -> (factor to metres, label)
UNITS = {"mm": 1e-3, "cm": 1e-2, "m": 1.0, "in": 0.0254, "ft": 0.3048}

st.title("🛢️ HeadCalc")
st.caption("Inside volume of a tank head – oval/ellipsoidal or torispherical.")

c1, c2 = st.columns(2)
head_type = c1.radio("Head type", ["Oval / Ellipsoidal", "Torispherical"], horizontal=True)
unit = c2.selectbox("Length unit", list(UNITS), index=0)
f = UNITS[unit]
step = {"mm": 10.0, "cm": 1.0, "m": 0.01, "in": 0.5, "ft": 0.05}[unit]

def num(label, default_m, help_):
    return st.number_input(f"{label} ({unit})", min_value=0.0, value=round(default_m / f, 4),
                           step=step, format="%.4f", help=help_)

try:
    if head_type == "Oval / Ellipsoidal":
        st.subheader("Oval / Ellipsoidal head inputs")
        st.markdown(svg_html(oval_svg(), 640), unsafe_allow_html=True)
        st.caption("Schematic – not to scale.")
        a, b = st.columns(2)
        with a:
            W = num("W – Total internal width", 2.4, "Total internal width of the tank base (major axis).")
            h_dish = num("h_dish – Inside dish depth", 0.4, "Inside depth of the ellipsoidal dish, tangent line to apex.")
        with b:
            H = num("H – Total internal height", 1.6, "Total internal height of the tank base (minor axis).")
            SF = num("SF – Straight flange", 0.05, "Length of the straight flange.")
        res = oval_head(W, H, h_dish, SF)
        profile = oval_profile(W, h_dish, SF)
        formula = r"""
**Base:** ellipse with semi-axes $a = W/2,\; b = H/2$

$$V_{dish} = \tfrac{2}{3}\,\pi\, a\, b\, h_{dish}$$
$$V_{SF} = \pi\, a\, b\, SF$$
"""
    else:
        st.subheader("Torispherical head inputs")
        st.markdown(svg_html(torispherical_svg(), 420), unsafe_allow_html=True)
        st.caption("Schematic – not to scale. Dish depth h is calculated from D_i, CR and KR.")
        a, b = st.columns(2)
        with a:
            D_i = num("D_i – Inside diameter", 2.0, "Inside diameter of the tank shell.")
            KR = num("KR – Knuckle radius", 0.12, "Knuckle (inside transition) radius.")
        with b:
            CR = num("CR – Crown radius", 2.0, "Crown radius (inside dish radius).")
            SF = num("SF – Straight flange", 0.05, "Length of the straight flange.")
        res = torispherical_head(D_i, CR, KR, SF)
        profile = torispherical_profile(D_i, CR, KR, SF)
        formula = r"""
Exact solid of revolution (knuckle torus section + crown spherical cap).

With $c = D_i/2 - KR$, the knuckle centre sits $z_k = \sqrt{(CR-KR)^2 - c^2}$ above the crown centre.
Dish depth $h = CR - z_k$. The knuckle runs to $z_t = z_k \cdot CR/(CR-KR)$, then the crown cap of height $CR - z_t$.

$$V_{knuckle} = \pi\!\int_0^{u_1}\!\big(c + \sqrt{KR^2-u^2}\big)^2 du,\quad u_1 = z_t - z_k$$
$$V_{crown} = \tfrac{\pi}{3} h_c^2 (3CR - h_c),\quad h_c = CR - z_t$$
$$V_{SF} = \pi (D_i/2)^2\, SF$$
"""
except ValueError as e:
    st.error(f"⚠️ {e}")
    st.stop()

# ---- results --------------------------------------------------------------
m3 = f ** 3
V_dish, V_sf, V_tot = res.dish_volume * m3, res.flange_volume * m3, res.total_volume * m3

st.divider()
st.subheader("Results")
k1, k2, k3 = st.columns(3)
k1.metric("Total inside volume", f"{V_tot * 1000:,.2f} L")
k2.metric("Dish volume", f"{V_dish * 1000:,.2f} L")
k3.metric("Straight flange volume", f"{V_sf * 1000:,.2f} L")
st.caption(f"Dish depth (tangent line to apex): **{res.dish_depth:,.4f} {unit}**")

table = pd.DataFrame(
    {
        "Litres": [V_dish * 1000, V_sf * 1000, V_tot * 1000],
        "m³": [V_dish, V_sf, V_tot],
        "US gal": [v * 264.172052 for v in (V_dish, V_sf, V_tot)],
        "Imp gal": [v * 219.969248 for v in (V_dish, V_sf, V_tot)],
        "ft³": [v * 35.3146667 for v in (V_dish, V_sf, V_tot)],
    },
    index=["Dish", "Straight flange", "Total"],
)
st.dataframe(table.style.format("{:,.4f}"), use_container_width=True)

# ---- profile sketch -------------------------------------------------------
half = pd.DataFrame(profile, columns=["r", "z"])
full = pd.concat([half.assign(r=-half["r"]).iloc[::-1], half], ignore_index=True)
full["order"] = range(len(full))
span = max(full["r"].abs().max(), full["z"].max()) * 1.1
chart = (
    alt.Chart(full)
    .mark_line(strokeWidth=3)
    .encode(
        x=alt.X("r:Q", title=f"Radius ({unit})" + (" – width plane" if head_type.startswith("Oval") else ""),
                scale=alt.Scale(domain=[-span, span])),
        y=alt.Y("z:Q", title=f"Height ({unit})", scale=alt.Scale(domain=[0, span])),
        order="order:Q",
    )
    .properties(height=320, title="Inside profile (to scale, SF shown at bottom)")
)
st.altair_chart(chart, use_container_width=True)

with st.expander("Formulas & assumptions"):
    st.markdown(formula)
    st.markdown(
        "- All dimensions are **inside** dimensions.\n"
        "- Dish volume is measured from the tangent line to the apex; the straight flange is added separately.\n"
        "- The oval head assumes an elliptical tank cross-section (W × H) with a half-ellipsoid dish."
    )

st.caption("HeadCalc · free public tool · verify critical results against your design code.")
