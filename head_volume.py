"""Inside-volume calculations for tank heads.

All functions are unit-agnostic: pass every length in the same unit and the
returned volume is in that unit cubed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class HeadResult:
    dish_volume: float        # volume between tangent line and apex
    flange_volume: float      # volume of the straight flange
    dish_depth: float         # tangent line to apex (inside)

    @property
    def total_volume(self) -> float:
        return self.dish_volume + self.flange_volume


def oval_head(W: float, H: float, h_dish: float, SF: float = 0.0) -> HeadResult:
    """Oval / ellipsoidal head on an oval (elliptical) tank cross-section.

    The base is an ellipse with semi-axes a = W/2 and b = H/2; the dish is a
    half-ellipsoid with third semi-axis h_dish.
        V_dish   = (2/3) * pi * a * b * h_dish
        V_flange = pi * a * b * SF
    """
    for name, v in (("W", W), ("H", H), ("h_dish", h_dish)):
        if v <= 0:
            raise ValueError(f"{name} must be greater than zero.")
    if SF < 0:
        raise ValueError("SF cannot be negative.")
    a, b = W / 2.0, H / 2.0
    base_area = math.pi * a * b
    return HeadResult(
        dish_volume=(2.0 / 3.0) * base_area * h_dish,
        flange_volume=base_area * SF,
        dish_depth=h_dish,
    )


def torispherical_geometry(D_i: float, CR: float, KR: float) -> dict:
    """Key axial positions, measured from the crown-radius centre on the axis."""
    if D_i <= 0 or CR <= 0 or KR <= 0:
        raise ValueError("D_i, CR and KR must all be greater than zero.")
    R = D_i / 2.0
    if KR >= R:
        raise ValueError("Knuckle radius KR must be smaller than D_i / 2.")
    if CR <= KR:
        raise ValueError("Crown radius CR must be larger than knuckle radius KR.")
    if CR < R:
        raise ValueError("Crown radius CR must be at least D_i / 2.")
    c = R - KR                                   # radial offset of knuckle centre
    z_k = math.sqrt((CR - KR) ** 2 - c ** 2)     # axial position of knuckle centre / tangent line
    z_t = z_k * CR / (CR - KR)                   # knuckle-to-crown junction
    return {"R": R, "c": c, "z_k": z_k, "z_t": z_t, "dish_depth": CR - z_k}


def torispherical_head(D_i: float, CR: float, KR: float, SF: float = 0.0) -> HeadResult:
    """Exact inside volume of a torispherical (flanged & dished) head.

    Solid of revolution split into the knuckle (torus section) and the crown
    (spherical cap), both integrated in closed form.
    """
    if SF < 0:
        raise ValueError("SF cannot be negative.")
    g = torispherical_geometry(D_i, CR, KR)
    c, z_k, z_t = g["c"], g["z_k"], g["z_t"]

    # Knuckle: r(u) = c + sqrt(KR^2 - u^2), u = z - z_k in [0, u1]
    u1 = z_t - z_k
    root = math.sqrt(max(KR ** 2 - u1 ** 2, 0.0))
    int_sqrt = 0.5 * (u1 * root + KR ** 2 * math.asin(min(u1 / KR, 1.0)))
    v_knuckle = math.pi * (c ** 2 * u1 + 2 * c * int_sqrt + KR ** 2 * u1 - u1 ** 3 / 3.0)

    # Crown: spherical cap of height h_c
    h_c = CR - z_t
    v_crown = math.pi * h_c ** 2 * (3 * CR - h_c) / 3.0

    return HeadResult(
        dish_volume=v_knuckle + v_crown,
        flange_volume=math.pi * g["R"] ** 2 * SF,
        dish_depth=g["dish_depth"],
    )


def torispherical_profile(D_i: float, CR: float, KR: float, SF: float = 0.0, n: int = 60):
    """(radius, height-above-flange-start) points of the inside profile, for plotting."""
    g = torispherical_geometry(D_i, CR, KR)
    c, z_k, z_t, R = g["c"], g["z_k"], g["z_t"], g["R"]
    pts = [(R, 0.0), (R, SF)]
    phi_end = math.asin(min((z_t - z_k) / KR, 1.0))
    for i in range(1, n + 1):
        p = phi_end * i / n
        pts.append((c + KR * math.cos(p), SF + KR * math.sin(p)))
    theta0 = math.acos(z_t / CR)
    for i in range(1, n + 1):
        t = theta0 * (1 - i / n)
        pts.append((CR * math.sin(t), SF + CR * math.cos(t) - z_k))
    return pts


def oval_profile(W: float, h_dish: float, SF: float = 0.0, n: int = 80):
    """Half-profile through the width (W) plane: (half-width, height) points."""
    a = W / 2.0
    pts = [(a, 0.0), (a, SF)]
    for i in range(1, n + 1):
        t = (math.pi / 2) * i / n
        pts.append((a * math.cos(t), SF + h_dish * math.sin(t)))
    return pts
