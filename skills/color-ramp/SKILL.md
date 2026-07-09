---
name: color-ramp
description: Generates a perceptually even, dark-to-light OKLCH colour scale (palette, ramp, tints/shades, or design tokens) that passes exactly through two hex colours. Use when the user gives two colours and wants a scale between or through both — output as a table, CSS variables, JSON tokens, or a swatch preview — especially when they want to avoid "washed out", "chalky", or "muddy" results.
---

# Two-Colour Ramp

**Always run the script below to compute the scale. Do not calculate OKLCH,
hex conversion, or interpolation by hand — floating-point colour maths
done by hand is inconsistent between runs; the script is not.**

## Requirements

Python 3 standard library only — no third-party packages, no Node.

## Usage

```bash
python3 scripts/generate_scale.py --a HEX --b HEX [options]
```

| Flag | Default | Meaning |
|---|---|---|
| `--a`, `--b` | *(required)* | The two anchor colours, e.g. `#1e3a8a` or `1e3a8a`. Order doesn't matter — the script sorts dark to light automatically. |
| `--steps` | `9` | Number of steps in the scale, 3-15. Use `11` to get standard Tailwind-style labels (`50,100,200...950`); other counts label in multiples of 100. |
| `--dark-end` | `6` | Target lightness % of the darkest step. Auto-extends if a given colour is darker than this. |
| `--light-end` | `97` | Target lightness % of the lightest step. Auto-extends if a given colour is lighter than this. |
| `--chroma-boost` | `0.45` | 0-1. How strongly the middle of the scale is boosted for vividness relative to the tapered ends. Raise this if the result still looks flat; lower it for a muted/desaturated feel. |
| `--hue-tilt` | `8` | Degrees of hue rotation across the scale (cooler near the light end, warmer near the dark end) for a sense of depth. Set to `0` for a perfectly flat hue. |
| `--format` | `table` | `table` (human-readable), `json` (array of step objects), `css` (`:root` custom properties), or `html` (static swatch preview file). |
| `--name` | `color` | Token/title prefix used by `css` and `html` formats, e.g. `--name brand` gives `--brand-500`. |
| `--out` | *(stdout)* | Write the result to a file instead of printing it. |

## Workflow

1. Identify the two hex colours from the user's request. If they gave
   named colours or described colours rather than hex codes, resolve them
   to hex first and confirm with the user if there's any ambiguity.
2. Pick a sensible `--steps` count: `11` if the user wants a full
   Tailwind/Material-style ramp (50-950), `9` for a general-purpose
   scale, fewer for something like a 3-5 step accent ramp.
3. Pick `--format` based on what the user wants to do with the output:
   - Dropping into CSS / a design system → `css`
   - Feeding into other tooling / documenting in JSON → `json`
   - Just wants to see it / sanity-check the result → `html` (then open
     or present the file), or `table` for a quick terminal look.
4. Run the script with the chosen flags.
5. If the user says a result still looks washed out or muddy, increase
   `--chroma-boost` (try `0.6`-`0.8`) and re-run, rather than manually
   editing individual hex values afterwards.
6. If a generated step's hex doesn't visually match the requested vividness,
   note that it may have been gamut-clipped — some highly saturated combinations
   can't be rendered at very light or very dark lightness in sRGB, so the script
   pulls chroma back automatically to stay renderable.

## Example

```bash
python3 scripts/generate_scale.py --a "#1e3a8a" --b "#fbbf24" --steps 11 --format css --name brand
```

```css
:root {
  --brand-50: #010015;
  --brand-100: #050038;
  ...
  --brand-400: #1e3a8a;   /* exact anchor A */
  ...
  --brand-900: #fbbf24;   /* exact anchor B */
  --brand-950: #fff3e2;
}
```
