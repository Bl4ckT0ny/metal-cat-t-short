# Print specification

English | [Русский](PRINT_SPEC.ru.md)

## Locked artwork

The approved cat/guitar composition is fixed. Do not alter:
- cat identity / Maine Coon appearance
- feline paws
- pose
- guitar silhouette / 7-string concept
- clothing
- overall composition

## Intended production method

- Screen printing on black T-shirt
- 5 spot-color inks
- Black shirt fabric used as base / negative space where possible
- Halftone screening is used to reproduce tonal detail in fur and shadows

## Spot-color targets

The following values are the solid fills defined in `scripts/build_vector.py`.
They identify the five ink layers and provide numerical starting points for matching.

| Layer | sRGB HEX | sRGB R / G / B | CIELAB L* / a* / b* (D65, 2°) |
|---|---|---|---|
| DARK_GRAY | `#626466` | 98 / 100 / 102 | 42.3 / −0.4 / −1.4 |
| CREAM | `#FFF6E5` | 255 / 246 / 229 | 97.2 / 0.2 / 9.2 |
| BROWN | `#B78659` | 183 / 134 / 89 | 59.7 / 13.4 / 31.5 |
| ORANGE | `#FF831F` | 255 / 131 / 31 | 67.7 / 41.7 / 68.5 |
| RED | `#FF1608` | 255 / 22 / 8 | 53.9 / 78.4 / 65.5 |

Lab values are calculated from sRGB with a D65 white point and the 2° observer, rounded to one decimal. They are digital design targets, not measurements of printed ink or Pantone equivalents. When using a D50 measurement workflow, convert to the same reference white before comparing values.

### Ink matching and approval

1. Match each layer to a physical Pantone Solid Coated swatch or a physical swatch from the print shop's textile-ink system. Record the exact code and guide edition, or the ink manufacturer, series and mixing recipe.
2. Print solid patches and tonal steps on the actual black garment fabric. Include representative overlapping colors from the artwork. Assess the sample after curing.
3. Agree whether an underbase is required. The artwork has five color layers; an additional white underbase requires a separate production decision and may add a screen.
4. Approve the physical sample as the production color reference. Record the fabric, ink recipe, underbase, print order and curing conditions. If instrumental acceptance is required, agree the measurement settings and ΔE00 tolerance against that approved sample.

Pantone codes and ink recipes are **not yet approved**. Pantone C/U suffixes describe the paper used for the reference swatch, not a textile specification; see [Pantone's explanation](https://support.pantone.com/en/what-does-the-terms-coated-and-uncoated-mean-in-the-pantone-graphics-system).

SVG opacity describes screen appearance. Printed halftone coverage and ink overlap must be proofed; opacity percentages are not ink mixing ratios. These are five spot-color inks, so generic CMYK conversions are not production recipes.

## Master artwork size

Design the production master for the largest intended print area rather than for a smaller default print.

- Target print area for the size 52 T-shirt: **44 × 55 cm**
- Intended placement: large front print, close to the usable shirt panel width
- Bottom clearance: approximately **10 cm above the bottom hem**
- Top placement: approximately **5–6 cm below the collar**, adjusted to the actual garment
- Final dimensions remain constrained by the real garment measurements and the printer's platen / frame limits

The master should preserve enough detail for the 44 × 55 cm version. Smaller production sizes should be derived by scaling the vector master down, not by rebuilding the artwork from a smaller raster source.

## Scaling rules

- Vector geometry may be scaled down without resolution loss.
- Do not upscale a reduced raster master to create larger print sizes.
- Keep the editable master in vector form at the largest intended production size.
- Fine details must still respect the printer's minimum printable line / gap / dot size.
- Halftones should preferably be generated or validated for the **final physical output size** and the print shop's chosen screen mesh and halftone ruling (LPI). Do not assume that a screened halftone pattern can be scaled arbitrarily.
- If the printer's maximum area is smaller than 44 × 55 cm, reduce the vector artwork proportionally to fit.

## Deliverables

- transparent high-resolution raster reference
- 5 color separations
- editable SVG vector master
- print-ready PDF
- shirt preview
- color registration and trapping adjustments as required by the print shop

## Production principle

Work from the largest, most detailed master and derive smaller variants from it. Do not sacrifice source detail merely because a particular print shop may require a smaller output size.
