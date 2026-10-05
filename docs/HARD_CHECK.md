# Vector master verification


## SVG

- File: `vector/metal-cat-master.svg`, 440 × 550 mm.
- Ink layers: DARK_GRAY / CREAM / BROWN / ORANGE / RED.
- Separate regions: face, four paws, guitar body, neck, headstock and tuning hardware.
- Geometry source for the neck and headstock: `master/reconstruction_reference.png`; for the remaining contours: `master/reference.png`.
- Transparent background. Tones use opacity; the screen-printing halftone has not been generated.
- No embedded raster images or filters.

## Required checks

Strings, tuners and paws were visually checked on the final SVG rasterization.

| Check | Result | Evidence |
|---|---|---|
| Strings | PASS — exactly 7 | `hard-check-strings.png` |
| Tuner posts | PASS — exactly 7 | `hard-check-headstock.png` |
| Tuner knobs | PASS — exactly 7 | `hard-check-headstock.png` |
| Feline paws | PASS — two front and two hind paws | `hard-check-paws.png` |
| SVG structure: five layers, separate regions, no embedded raster images or filters | PASS — XML check | `docs/verification.json` |

Evidence PNGs are in `preview/comparisons/`.

## Reference comparison

Normalization: fixed crops with aspect-preserving fit on a black 4:5 canvas.
Reference crop: `[363,271,944,1001]`; final crop: `[31,17,1095,1354]`.

| Canvas height | Final RGB MAE against the reference (0–255) |
|---|---:|
| 1254 px | 13.241 |
| 627 px | 12.837 |
| 314 px | 12.077 |

Comparisons: `preview/comparisons/comparison-{1254,627,314}.png`.
Metrics and source SHA-256 hashes: `docs/verification.json`.
