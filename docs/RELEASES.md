# Release workflow


## Run on GitHub

The workflow must be present on the repository default branch.

1. Open Actions → Build vector release → Run workflow.
2. Enter an unused tag, for example `vector-v1`.
3. Leave `publish` off to download the build as an Actions artifact, or turn
   it on to publish a GitHub Release after automated checks pass.

The workflow builds the SVG from the source PNGs, runs verification and
packages the output. Actions artifacts are retained for 14 days.

Publishing verifies asset checksums, creates a draft Release, uploads the
assets and publishes the Release. Existing tags are rejected. If an upload
fails, check for a remaining draft before retrying.

The release job uses the workflow's temporary `GITHUB_TOKEN` with
`contents: write` permission.

## Output

- `metal-cat-master.svg`: five-layer vector master.
- `manifest.json`: release tag and source commit.
- `metal-cat-<tag>.zip`: SVG, raster preview, comparisons at 1254 / 627 / 314 px,
  hard-check previews, reports and `manifest.json` with the release tag and source commit.
- Each file has a separate checksum file: `metal-cat-master.svg.sha256`,
  `manifest.json.sha256` and `metal-cat-<tag>.zip.sha256`.

Download individual files or the complete ZIP. To verify a downloaded file,
place its `.sha256` file in the same directory and run
`sha256sum -c <filename>.sha256`.

Visually check the seven strings, seven tuner posts, seven tuner knobs and
feline paws in the generated previews before publishing a new build.
XML checks validate structure; the visual check results are recorded in
`HARD_CHECK.md`.

## Run locally

Requires Python 3 with venv support and the Cairo runtime library.

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_vector.py --epsilon .1
.venv/bin/python scripts/verify_vector.py
.venv/bin/python scripts/package_release.py --tag vector-v1
```

Output is written to `dist/vector-v1/`. Local packaging does not publish a Release.
