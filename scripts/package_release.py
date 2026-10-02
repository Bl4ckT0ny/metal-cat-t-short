"""Package only current deliverables, never historical iterations or Git data."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]

def package(tag):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}',tag):
        raise ValueError('Tag must contain only letters, digits, dot, underscore or hyphen')
    files=[ROOT/'vector/metal-cat-master.svg',ROOT/'preview/iterations/metal-cat-master.png',ROOT/'docs/HARD_CHECK.md',ROOT/'docs/verification.json',ROOT/'docs/build-statistics.json',ROOT/'docs/geometry-landmarks.json']
    for size in [1254,627,314]:
        files.append(ROOT/f'preview/comparisons/comparison-{size}.png')
    for name in ['hard-check-strings','hard-check-headstock','hard-check-paws','face-reference-vector']:
        files.append(ROOT/f'preview/comparisons/{name}.png')
    for path in files:
        if not path.is_file() or path.stat().st_size==0:
            raise FileNotFoundError(f'Missing deliverable: {path.relative_to(ROOT)}')
    verification=json.loads((ROOT/'docs/verification.json').read_text())
    if not verification.get('xml_checks','').startswith('PASS:'):
        raise ValueError('Run verify_vector.py successfully before packaging')
    for name,digest in verification['source_hashes'].items():
        if hashlib.sha256((ROOT/'master'/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Source changed after verification: {name}')
    dest=ROOT/'dist'/tag
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(files[0],dest/'metal-cat-master.svg')
    manifest={'tag':tag,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'manual_review':'Inspect numbered 7/7/7 and paw previews before publishing a newly rebuilt release.'}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=dest/f'metal-cat-{tag}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files:z.write(path,path.relative_to(ROOT))
        z.write(dest/'manifest.json','manifest.json')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Archive validation failed')
    assets=[dest/'metal-cat-master.svg',archive,dest/'manifest.json']
    (dest/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in assets))
    print(dest)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True)
    package(parser.parse_args().tag)
