# Metal Cat T-Shirt Print

Production repository for the approved metal Maine Coon T-shirt artwork.

## Goal

Prepare the fixed artwork for screen printing without changing the approved composition or character.

Target production setup:

- black T-shirt used as the base / negative space
- 5 spot colors
- halftones where needed to preserve fur, face and shading
- transparent background outside the print
- separate color separations
- editable vector master
- print-ready PDF
- preview mockup
- master production area: **44 × 55 cm** for the intended size 52 shirt

The artwork is authored at the largest intended print size and scaled down from the vector master when a printer or garment requires a smaller area.

## Repository structure

- `master/` — approved raster master
- `separations/` — individual spot-color separations
- `vector/` — editable SVG/vector artwork
- `print/` — print-ready production files
- `preview/` — T-shirt mockups and previews
- `docs/` — print specifications and production notes

## Current palette direction

1. Dark gray
2. Beige / cream
3. Brown
4. Orange
5. Red

Black is primarily supplied by the shirt fabric.

## Important

The approved artwork is treated as locked. Further work should be technical only: cleanup, color reduction, separations, halftones, tracing and print preparation. Do not regenerate or redesign the cat, guitar, pose, clothing or composition.

For production details, see `docs/PRINT_SPEC.md`.

## Build and release

Generated SVGs and previews are release assets, not Git history.
The original PNGs stay in `master/`; this branch contains the reproducible
build scripts and a manually triggered GitHub Actions workflow.

See [release instructions](docs/RELEASES.md) for building and publishing.
The final checks and source provenance are documented in
[HARD_CHECK.md](docs/HARD_CHECK.md).

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_vector.py --epsilon .1
.venv/bin/python scripts/verify_vector.py
.venv/bin/python scripts/package_release.py --tag vector-v1
```

The pipeline produces five named ink layers and unscreened vector tones,
with no embedded bitmap. Corrective contours come from the unchanged
reference; the seven-string neck and headstock come from the selected
reconstruction. Historical preview files are optional and are not required
for fresh release builds. Visual review of 7/7/7 and feline paws remains
separate from automated structural checks.
