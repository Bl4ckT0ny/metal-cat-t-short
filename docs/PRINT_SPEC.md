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

## Spot-color palette

1. Dark Gray
2. Beige / Cream
3. Brown
4. Orange
5. Red

Exact Pantone / ink references to be finalized with the print shop.

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
- Halftones should preferably be generated or validated for the **final physical output size** and the print shop's chosen screen mesh and halftone ruling (LPI). Do not assume that an screened halftone pattern can be scaled arbitrarily.
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
