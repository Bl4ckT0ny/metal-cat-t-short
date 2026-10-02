# Release workflow

Keep source PNGs, scripts and documentation in Git. Store generated SVG,
current raster comparisons and reports in GitHub Releases. Old iterations
remain in the local reconstruction branch and are not needed to build releases.

This lightweight branch starts at the existing repository main commit, not
at the end of the large local artifact history. Merely deleting old files
from the latter would not remove them from the history that must be pushed.

## Run on GitHub

After the workflow has been added to the repository default branch:

1. Open Actions → Build vector release → Run workflow.
2. Enter a fresh tag, for example `vector-v1`.
3. Leave `publish` off to build and download the output for inspection, or turn
   it on to publish a Release after the automated checks finish.

GitHub builds directly from the PNGs already in this repository. The build
job has read-only repository access. Only the release job has contents:write,
using its temporary GITHUB_TOKEN; no personal token or local SSH key is needed.

Assets: `metal-cat-master.svg`, a ZIP containing only the current deliverables,
`manifest.json` with source commit and file hashes, and `SHA256SUMS`.
An existing release is not overwritten. If upload fails, a draft may remain;
inspect it before manually removing it or choosing a new tag for a retry.

Automated XML checks do not replace visual inspection of the numbered strings,
posts, knobs and feline paws on a new build. The original manual review is in
HARD_CHECK.md. Historical before/after metrics are omitted when their local
baseline PNGs are absent; current reference/source/vector comparisons still run.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_vector.py --epsilon .1
.venv/bin/python scripts/verify_vector.py
.venv/bin/python scripts/package_release.py --tag vector-v1
```

The packager performs no network access or authentication. Publishing is a
separate GitHub Actions step. The available chat GitHub integration does not
expose release-asset upload or workflow dispatch, so those are not claimed
to have run merely because these scripts are present.
