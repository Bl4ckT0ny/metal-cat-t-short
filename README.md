# Metal Cat T-Shirt Print

English | [Русский](README.ru.md)

Production repository for the approved metal Maine Coon T-shirt artwork.

## Goal

Prepare the fixed artwork for screen printing without changing the approved composition or character.

Target production setup:

- black T-shirt used as the base / negative space
- 5 spot-color inks
- halftone screening where needed to reproduce fur, facial detail and shading
- transparent background outside the print
- one color separation per ink
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

## Ink palette

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

Source PNGs and build scripts are stored in Git. Generated SVGs and previews
are published as release assets through a manually triggered GitHub Actions workflow.

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

The pipeline produces five named ink layers with opacity-based tones and no
embedded raster images. Screen-printing halftones have not been generated.
Figure contours come from the reference image; the seven-string neck and
headstock come from the selected reconstruction image.

The seven strings, seven tuner posts, seven tuner knobs and feline paws are
checked visually. Automated checks validate SVG structure.
