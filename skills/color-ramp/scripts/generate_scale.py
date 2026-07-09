#!/usr/bin/env python3
"""Build a dark-to-light OKLCH colour scale through two anchor colours.

Computes a perceptually even lightness scale that passes through two given hex
anchor colours exactly, with chroma tapered at the extremes and lightly boosted
mid-scale so the ends don't go chalky or muddy. Any colour that would fall
outside the sRGB gamut is pulled back in via binary search on chroma, so every
hex returned is renderable.

Usage:  generate_scale.py --a HEX --b HEX [options]
Exit:   0 = ok, 1 = bad arguments or input.

Stdlib only -- no network, no third-party packages.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

TEMPLATE_FILE = Path(__file__).resolve().parent.parent / "assets" / "preview-template.html"

# ---------- hex helpers ----------


def normalize_hex(raw: str) -> str:
    """Return a 6-digit lowercase hex string, expanding 3-digit shorthand."""
    h = raw.lstrip("#").lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-f]{6}", h):
        sys.exit(f"Error: '{raw}' is not a valid hex colour.")
    return h


def clamp8(x: float) -> int:
    """sRGB 0-255 channel: truncate toward zero, then clamp to [0, 255]."""
    n = int(x)
    return 0 if n < 0 else 255 if n > 255 else n


# ---------- colour space maths (sRGB <-> linear <-> OKLab <-> OKLCH) ----------


def srgb_to_linear(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    if c < 0:
        c = 0
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def fmod360(x: float) -> float:
    x = x - 360 * int(x / 360)
    return x + 360 if x < 0 else x


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def hue_lerp_short(h1: float, h2: float, t: float) -> float:
    diff = fmod360(h2 - h1 + 540) - 180
    return fmod360(h1 + diff * t)


def hex_to_oklch(hex6: str) -> tuple[float, float, float]:
    """Convert a 6-digit hex colour to (L, C, H); L in 0-1, H in degrees."""
    r, g, b = (int(hex6[i : i + 2], 16) for i in (0, 2, 4))
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)

    l = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl
    m = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl
    s = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl

    l_, m_, s_ = (v ** (1 / 3) if v > 0 else 0 for v in (l, m, s))

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

    C = math.sqrt(a * a + bb * bb)
    H = math.atan2(bb, a) * 180 / math.pi
    if H < 0:
        H += 360
    return L, C, H


def _oklch_to_linear_rgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    a = C * math.cos(H * math.pi / 180)
    bb = C * math.sin(H * math.pi / 180)
    l_ = L + 0.3963377774 * a + 0.2158037573 * bb
    m_ = L - 0.1055613458 * a - 0.0638541728 * bb
    s_ = L - 0.0894841775 * a - 1.2914855480 * bb
    l, m, s = l_**3, m_**3, s_**3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return r, g, b


def in_gamut(L: float, C: float, H: float) -> bool:
    r, g, b = _oklch_to_linear_rgb(L, C, H)
    return all(-0.001 <= v <= 1.001 for v in (r, g, b))


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Convert OKLCH to hex, pulling chroma back into the sRGB gamut if needed."""
    L = min(1.0, max(0.0, L))
    C = max(0.0, C)
    if not in_gamut(L, C, H):
        lo, hi = 0.0, C
        for _ in range(24):
            mid = (lo + hi) / 2
            if in_gamut(L, mid, H):
                lo = mid
            else:
                hi = mid
        C = lo
    r, g, b = _oklch_to_linear_rgb(L, C, H)
    return "".join(f"{clamp8(linear_to_srgb(v) * 255):02x}" for v in (r, g, b))


# ---------- scale construction ----------


def build_scale(hex_a, hex_b, steps, dark_end, light_end, chroma_boost, hue_tilt):
    """Return a list of step dicts, dark to light, with anchors snapped exactly."""
    a_l, a_c, a_h = hex_to_oklch(hex_a)
    b_l, b_c, b_h = hex_to_oklch(hex_b)

    if a_l <= b_l:
        (d_l, d_c, d_h, d_hex), (l_l, l_c, l_h, l_hex) = (a_l, a_c, a_h, hex_a), (b_l, b_c, b_h, hex_b)
    else:
        (d_l, d_c, d_h, d_hex), (l_l, l_c, l_h, l_hex) = (b_l, b_c, b_h, hex_b), (a_l, a_c, a_h, hex_a)

    scale_dark = min(dark_end, d_l * 100 - 3)
    scale_light = max(light_end, l_l * 100 + 3)
    scale_dark = max(0.0, scale_dark)
    scale_light = min(99.5, scale_light)

    span = scale_light - scale_dark
    pos_a = (d_l * 100 - scale_dark) / span
    pos_b = (l_l * 100 - scale_dark) / span

    c_dark_end = d_c * 0.7
    c_light_end = l_c * 0.18

    n1 = steps - 1
    rows = []
    for i in range(steps):
        p = i / n1 if n1 > 0 else 0
        lpct = lerp(scale_dark, scale_light, p)

        if p <= pos_a:
            t = p / pos_a if pos_a > 0.0001 else 1
            c = lerp(c_dark_end, d_c, t)
            h = d_h
        elif p <= pos_b:
            t = (p - pos_a) / (pos_b - pos_a) if (pos_b - pos_a) > 0.0001 else 1
            c = lerp(d_c, l_c, t)
            h = hue_lerp_short(d_h, l_h, t)
        else:
            t = (p - pos_b) / (1 - pos_b) if (1 - pos_b) > 0.0001 else 1
            c = lerp(l_c, c_light_end, t)
            h = l_h

        c = c * (1 + chroma_boost * math.sin(math.pi * p) * 0.9)
        if c < 0:
            c = 0
        h = fmod360(h - hue_tilt * (p - 0.5) * 2)

        rows.append({"pos": p, "lpct": lpct, "c": c, "h": h, "hex": None, "anchor": "-"})

    # snap the nearest step to each anchor's exact OKLCH values
    idx_a = min(range(steps), key=lambda i: abs(rows[i]["pos"] - pos_a))
    idx_b = min(range(steps), key=lambda i: abs(rows[i]["pos"] - pos_b))
    if idx_a == idx_b:
        if idx_b < steps - 1:
            idx_b += 1
        else:
            idx_a -= 1

    rows[idx_a].update(lpct=d_l * 100, c=d_c, h=d_h, anchor="A", hex=d_hex)
    rows[idx_b].update(lpct=l_l * 100, c=l_c, h=l_h, anchor="B", hex=l_hex)

    for row in rows:
        if row["hex"] is None:
            row["hex"] = oklch_to_hex(row["lpct"] / 100, row["c"], row["h"])
    return rows


def step_labels(steps: int) -> list[int]:
    if steps == 11:
        return [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
    return [(i + 1) * 100 for i in range(steps)]


# ---------- formatters ----------


def to_table(rows, labels):
    out = ["{:<4} {:<8} {:<7} {:<8} {:<7} {:<8} {}".format("step", "label", "L%", "C", "H", "hex", "anchor")]
    for i, row in enumerate(rows):
        out.append(
            "{:<4} {:<8} {:<7.2f} {:<8.4f} {:<7.2f} #{:<7} {}".format(
                i, labels[i], row["lpct"], row["c"], row["h"], row["hex"], row["anchor"]
            )
        )
    return "\n".join(out)


def to_json(rows, labels):
    items = [
        {
            "step": i,
            "label": labels[i],
            "lightness_pct": round(row["lpct"], 2),
            "chroma": round(row["c"], 4),
            "hue": round(row["h"], 2),
            "hex": f"#{row['hex']}",
            "anchor": None if row["anchor"] == "-" else row["anchor"],
        }
        for i, row in enumerate(rows)
    ]
    return json.dumps(items)


def to_css(rows, labels, name):
    lines = [":root {"]
    lines += [f"  --{name}-{labels[i]}: #{row['hex']};" for i, row in enumerate(rows)]
    lines.append("}")
    return "\n".join(lines)


def to_html(rows, labels, name):
    if not TEMPLATE_FILE.is_file():
        sys.exit(f"Error: preview template not found at {TEMPLATE_FILE}")
    swatches = ""
    for i, row in enumerate(rows):
        tag = f'<span class="tag">{row["anchor"]}</span>' if row["anchor"] != "-" else ""
        swatches += (
            f'<div class="step"><div class="chip" style="background:#{row["hex"]}">{tag}</div>'
            f'<div class="meta"><div class="hex">#{row["hex"]}</div>'
            f'<div class="lpct">{labels[i]} &middot; L {row["lpct"]:.2f}%</div></div></div>'
        )
    html = TEMPLATE_FILE.read_text()
    return html.replace("{{NAME}}", name).replace("{{SWATCHES}}", swatches)


# ---------- entry point ----------


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="generate_scale.py",
        description="Build a dark-to-light OKLCH colour scale through two anchor colours.",
    )
    p.add_argument("--a", required=True, metavar="HEX", help='First anchor colour, e.g. "#1e3a8a" or "1e3a8a"')
    p.add_argument("--b", required=True, metavar="HEX", help="Second anchor colour")
    p.add_argument("--steps", type=int, default=9, help="Number of steps in the scale (default: 9, range 3-15)")
    p.add_argument("--dark-end", type=float, default=6, help="Lightness %% of the darkest step (default: 6)")
    p.add_argument("--light-end", type=float, default=97, help="Lightness %% of the lightest step (default: 97)")
    p.add_argument("--chroma-boost", type=float, default=0.45, help="0-1 strength of the mid-scale vividness curve (default: 0.45)")
    p.add_argument("--hue-tilt", type=float, default=8, help="Degrees of hue tilt across the scale (default: 8)")
    p.add_argument("--format", default="table", choices=["table", "json", "css", "html"], help="Output format (default: table)")
    p.add_argument("--name", default="color", help='Token name used for css/html output (default: "color")')
    p.add_argument("--out", metavar="PATH", help="Write output to this file instead of stdout")
    args = p.parse_args(argv)

    if not 3 <= args.steps <= 15:
        sys.exit("Error: --steps must be an integer between 3 and 15.")
    if not 0 <= args.chroma_boost <= 1:
        sys.exit("Error: --chroma-boost must be between 0 and 1.")

    hex_a = normalize_hex(args.a)
    hex_b = normalize_hex(args.b)

    rows = build_scale(hex_a, hex_b, args.steps, args.dark_end, args.light_end, args.chroma_boost, args.hue_tilt)
    labels = step_labels(args.steps)

    formatters = {"table": to_table, "json": to_json, "css": to_css, "html": to_html}
    if args.format in ("table", "json"):
        result = formatters[args.format](rows, labels)
    else:
        result = formatters[args.format](rows, labels, args.name)

    if args.out:
        Path(args.out).write_text(result + "\n")
        print(f"Wrote {args.format} output to {args.out}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
