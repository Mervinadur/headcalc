"""Schematic (not-to-scale) SVG diagrams labelling the input dimensions."""
from __future__ import annotations

import base64
import math

LINE = "#1f4e79"
DIM = "#c0392b"
AUX = "#7f8c8d"
TXT = "#222222"

_DEFS = f"""<defs>
<marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker></defs>"""


def _svg(w: int, h: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="13">{_DEFS}'
            f'<rect width="{w}" height="{h}" rx="10" fill="#ffffff"/>{body}</svg>')


def _dim(x1, y1, x2, y2, label, lx, ly, anchor="middle", both=True):
    start = 'marker-start="url(#a)" ' if both else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{DIM}" '
            f'stroke-width="1.4" {start}marker-end="url(#a)"/>'
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{DIM}" font-weight="bold" text-anchor="{anchor}">{label}</text>')


def _ext(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{AUX}" stroke-width="0.9" stroke-dasharray="3,3"/>')


def _text(x, y, s, anchor="middle", size=13, color=TXT):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{s}</text>'


def oval_svg() -> str:
    # Side view (width plane): flange 200→170, dish apex at 90
    side = (
        f'<path d="M40,200 L40,170 A110,80 0 0 1 260,170 L260,200" fill="#eaf2fb" stroke="{LINE}" stroke-width="2.5"/>'
        + _ext(30, 170, 300, 170) + _text(36, 165, "tangent line", "start", 10, AUX)
        + _ext(150, 90, 300, 90) + _ext(260, 200, 300, 200)
        + _dim(290, 170, 290, 90, "h_dish", 296, 134, "start")
        + _dim(290, 200, 290, 170, "SF", 296, 190, "start")
        + _ext(40, 200, 40, 235) + _ext(260, 200, 260, 235)
        + _dim(40, 228, 260, 228, "W", 150, 222)
        + _text(160, 262, "SIDE VIEW", size=12, color=AUX)
    )
    # End view: ellipse W x H
    cx, cy = 490, 130
    end = (
        f'<ellipse cx="{cx}" cy="{cy}" rx="110" ry="72" fill="#eaf2fb" stroke="{LINE}" stroke-width="2.5"/>'
        + _ext(cx - 110, cy, cx - 110, 235) + _ext(cx + 110, cy, cx + 110, 235)
        + _dim(cx - 110, 228, cx + 110, 228, "W", cx, 222)
        + _ext(cx, cy - 72, cx + 140, cy - 72) + _ext(cx, cy + 72, cx + 140, cy + 72)
        + _dim(cx + 130, cy + 72, cx + 130, cy - 72, "H", cx + 136, cy + 5, "start")
        + _text(cx, 262, "END VIEW", size=12, color=AUX)
    )
    return _svg(660, 275, side + end)


def torispherical_svg() -> str:
    cx, y_tl, y_bot = 170, 190.0, 220.0          # axis x, tangent line y, flange bottom y
    R, CR, KR = 110.0, 176.0, 40.0                # illustrative proportions
    c = R - KR
    z_k = math.sqrt((CR - KR) ** 2 - c ** 2)
    z_t = z_k * CR / (CR - KR)
    depth = CR - z_k
    yc = y_tl + z_k                               # crown centre (below drawing)
    jx, jy = cx + c + math.sqrt(KR ** 2 - (z_t - z_k) ** 2), y_tl - (z_t - z_k)
    xl, xr = cx - R, cx + R
    path = (f'M{xl},{y_bot} L{xl},{y_tl} A{KR},{KR} 0 0 1 {2 * cx - jx:.1f},{jy:.1f} '
            f'A{CR},{CR} 0 0 1 {jx:.1f},{jy:.1f} A{KR},{KR} 0 0 1 {xr},{y_tl} L{xr},{y_bot}')
    # CR radius line to a crown point 18° off-axis; KR line at 35° from horizontal
    t = math.radians(18)
    crx, cry = cx - CR * math.sin(t), yc - CR * math.cos(t)
    kcx, kcy = cx + c, y_tl
    p = math.radians(35)
    krx, kry = kcx + KR * math.cos(p), kcy - KR * math.sin(p)
    apex = y_tl - depth
    body = (
        f'<path d="{path}" fill="#eaf2fb" stroke="{LINE}" stroke-width="2.5"/>'
        + _ext(xl - 15, y_tl, xr + 50, y_tl) + _text(xl - 12, y_tl - 5, "tangent line", "start", 10, AUX)
        + _ext(cx, apex - 10, cx, yc)                             # axis
        + f'<circle cx="{cx}" cy="{yc:.1f}" r="3" fill="{DIM}"/>'
        + _text(cx + 8, yc + 4, "crown centre", "start", 10, AUX)
        + _dim(cx, yc, crx, cry, "", 0, 0, both=False)
        + _text(cx - 16, yc - 30, "CR", "end", 14, DIM).replace("<text", '<text font-weight="bold"')
        + f'<circle cx="{kcx}" cy="{kcy}" r="3" fill="{DIM}"/>'
        + _dim(kcx, kcy, krx, kry, "KR", krx - 26, kry - 4, "end", both=False)
        + _ext(xr, y_bot, xr + 50, y_bot)
        + _dim(xr + 40, y_bot, xr + 40, y_tl, "SF", xr + 46, y_bot - 10, "start")
        + _ext(cx, apex, xr + 50, apex)
        + _dim(xr + 40, y_tl, xr + 40, apex, "h", xr + 46, (y_tl + apex) / 2 + 4, "start")
        + _text(xr + 46, (y_tl + apex) / 2 + 18, "(calculated)", "start", 10, AUX)
        + _ext(xl, y_bot, xl, y_bot + 35) + _ext(xr, y_bot, xr, y_bot + 35)
        + _dim(xl, y_bot + 28, xr, y_bot + 28, "D_i", cx + 45, y_bot + 22)
    )
    return _svg(400, int(yc) + 20, body)


def svg_html(svg: str, max_width: int = 640) -> str:
    b64 = base64.b64encode(svg.encode()).decode()
    return (f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64}" '
            f'style="width:100%;max-width:{max_width}px" alt="Head dimensions diagram"/></div>')
