"""Deterministic, non-generative reconstruction of the selected raster.

Five named ink layers with continuous-tone opacity, not final screen separations.
Run from repository root.
"""
from pathlib import Path
import json, hashlib
import numpy as np
import cv2
from PIL import Image, ImageDraw
import cairosvg
from align_geometry import warp, record
from reference_tone import corrected_source
from final_geometry import prepare

ROOT = Path(__file__).resolve().parents[1]
INKS = {'DARK_GRAY':'#626466', 'CREAM':'#fff6e5', 'BROWN':'#b78659',
        'ORANGE':'#ff831f', 'RED':'#ff1608'}
# Region polygons use source coordinates; raster pixels define their contours.
REGIONS = {
 'guitar_body': [(136,990),(423,728),(541,570),(579,552),(546,628),(541,678),(578,679),(649,777),(635,831),(586,875),(501,1020),(366,1208),(354,1040),(309,959),(260,955)],
 'neck': [(339,916),(847,323),(890,369),(402,965)],
 'headstock': [(842,338),(852,300),(869,274),(1001,209),(1074,221),(939,362),(896,374)],
 'face': [(350,11),(416,82),(530,131),(627,117),(703,8),(725,78),(673,188),(742,307),(727,364),(660,435),(562,510),(425,492),(301,418),(326,295),(388,172)],
 'paw_strumming': [(309,711),(351,700),(406,724),(451,767),(457,820),(416,856),(365,842),(319,801)],
 'paw_fretting': [(709,470),(747,440),(788,433),(827,457),(860,508),(867,548),(844,590),(804,596),(753,568),(723,521)],
 'paw_left_foot': [(48,1280),(78,1244),(129,1236),(194,1262),(204,1309),(171,1331),(94,1337),(45,1321)],
 'paw_right_foot': [(855,1280),(900,1234),(967,1235),(1026,1258),(1076,1291),(1080,1350),(1040,1362),(939,1354),(877,1333)]
}
POSTS = [(880,301),(903,290),(924,280),(943,271),(962,261),(986,250),(1009,239)]
KNOBS = [(877,283),(898,272),(919,262),(940,251),(962,240),(983,231),(1007,222)]

def contours(mask, epsilon):
    # Upsampling places contour edges on half-pixel boundaries and preserves
    # isolated one-pixel details which ordinary contourArea filtering loses.
    large = cv2.resize(mask.astype('uint8'), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    cc, hh = cv2.findContours(large, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out=[]
    for c in cc:
        c=cv2.approxPolyDP(c, epsilon*2, True).reshape(-1,2)/2
        if len(c)<3: continue
        out.append('M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in c)+'Z')
    return ''.join(out)

def build(epsilon=.18, name='metal-cat-master'):
    for folder in ["vector","preview/iterations","docs"]:
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    record()
    src=np.array(Image.open(ROOT/'master/reconstruction_reference.png').convert('RGB'))
    h,w=src.shape[:2]
    areas=np.zeros((h,w), np.uint8)
    names=['background_clothing_tail']+list(REGIONS)
    for i,(key,pts) in enumerate(REGIONS.items(),1):
        cv2.fillPoly(areas,[np.array(pts,np.int32)],i)
    # Separate traced hardware into individually named regions.
    for typ,points,radius in [('tuner_post',POSTS,8),('tuner_knob',KNOBS,11)]:
        for i,p in enumerate(points,1):
            names.append(f'{typ}_{i}')
            cv2.circle(areas,p,radius,len(names)-1,-1)
    rgb,areas,visible=prepare(src,areas,names)
    palette=np.array([[int(v[i:i+2],16) for i in (1,3,5)] for v in INKS.values()],np.float32)
    # Fit convex combinations of two inks plus black using overlapping opacities.
    best=np.full((h,w),np.inf,np.float32)
    weights=np.zeros((h,w,5),np.float32)
    for i in range(5):
        for j in range(i+1,5):
            p,q=palette[i],palette[j]
            pp,qq,pq=p@p,q@q,p@q
            rp,rq=rgb@p,rgb@q
            wi=(rp*qq-rq*pq)/(pp*qq-pq*pq)
            wj=(rq*pp-rp*pq)/(pp*qq-pq*pq)
            candidates=[(wi,wj),(np.clip(rp/pp,0,1),np.zeros((h,w))),
                        (np.zeros((h,w)),np.clip(rq/qq,0,1))]
            edge=np.clip(((rgb-q)@(p-q))/((p-q)@(p-q)),0,1)
            candidates.append((edge,1-edge))
            for a,b in candidates:
                valid=(a>=0)&(b>=0)&(a+b<=1.00001)
                err=((rgb-a[:,:,None]*p-b[:,:,None]*q)**2).sum(2)
                update=valid&(err<best)
                best[update]=err[update];weights[update]=0
                weights[:,:,i][update]=a[update];weights[:,:,j][update]=b[update]
    alpha=np.zeros_like(weights)
    remaining=np.ones((h,w),np.float32)
    for i in reversed(range(5)):
        alpha[:,:,i]=np.clip(weights[:,:,i]/np.maximum(remaining,.00001),0,1)
        remaining-=weights[:,:,i]
    alpha=np.round(alpha*32)/32
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="440mm" height="550mm" viewBox="0 0 {w} {h}">',
           '<title>Metal Cat — five ink continuous-tone reconstruction</title>',
           '<desc>Reconstruction source: reconstruction_reference.png, retained for seven-string neck and headstock. Corrective face, fur, body and splash contours: immutable reference.png. Transparent black negative space. Unscreened vector tones; see docs/HARD_CHECK.md.</desc>']
    stats={}
    for k,(ink,color) in enumerate(INKS.items()):
        parts.append(f'<g id="{ink}" data-ink="{ink}" inkscape:groupmode="layer" inkscape:label="{ink}" fill="{color}">')
        stats[ink]=0
        for a,region in enumerate(names):
            parts.append(f'<g id="{ink}__{region}" data-geometry="{region}">')
            tones=alpha[:,:,k]
            for tone in sorted(np.unique(tones[(areas==a)&visible])):
                if tone==0:continue
                d=contours((areas==a)&visible&(tones==tone),epsilon)
                if d:
                    parts.append(f'<path opacity="{tone:.5f}" fill-rule="evenodd" stroke="{color}" stroke-width="0.5" stroke-linejoin="round" d="{d}"/>')
                    stats[ink]+=d.count('M')
            parts.append('</g>')
        parts.append('</g>')
    parts.append('</svg>')
    path=ROOT/'vector'/f'{name}.svg';path.write_text('\n'.join(parts))
    cairosvg.svg2png(url=str(path),write_to=str(ROOT/'preview/iterations'/f'{name}.png'),output_width=w,output_height=h)
    (ROOT/'docs/build-statistics.json').write_text(json.dumps({'epsilon_source_px':epsilon,'tonal_levels':32,'contours':stats,'source_sha256':hashlib.sha256((ROOT/'master/reconstruction_reference.png').read_bytes()).hexdigest(),'regions':names},indent=2))
    print(path, path.stat().st_size,stats,flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--epsilon',type=float,default=.18);p.add_argument('--name',default='metal-cat-master');a=p.parse_args()
    build(a.epsilon,a.name)
