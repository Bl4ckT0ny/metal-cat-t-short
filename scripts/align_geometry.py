"""Piecewise affine contour correction against immutable photograph landmarks.

Transforms vector coordinates while preserving the reference image.
Identity perimeter anchors preserve the print bounding box.
"""
import json
import numpy as np
from scipy.spatial import Delaunay
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LANDMARKS=[
 ('ear_left',(365,20),(558,290)),('ear_right',(699,25),(710,292)),
 ('eye_left',(526,209),(634,386)),('eye_right',(612,213),(669,386)),
 ('nose',(583,239),(663,410)),('mouth',(558,327),(651,451)),
 ('chin',(556,382),(647,479)),
 ('guitar_upper_horn',(568,566),(625,575)),
 ('guitar_upper_cutaway',(540,678),(599,650)),
 ('guitar_lower_horn',(631,795),(684,695)),
 ('guitar_lower_cutaway',(548,817),(641,718)),
 ('guitar_left_tip',(140,986),(424,814)),
 ('guitar_bottom_tip',(365,1201),(526,928)),
 ('guitar_bridge',(378,943),(553,785)),
 ('headstock_tip',(1066,226),(905,395)),
 ('nut_left',(850,335),(812,437)),('nut_right',(884,366),(834,459)),
 ('paw_strumming',(385,786),(553,698)),('paw_fretting',(789,511),(771,543)),
 ('tail_tip',(1064,665),(929,624)),('tail_base',(855,874),(813,747)),
 ('left_foot',(128,1296),(414,964)),('right_foot',(969,1300),(884,966)),
 ('left_knee',(238,1090),(475,861)),('right_knee',(869,1045),(836,851)),
 ('left_elbow',(280,667),(506,628)),('right_shoulder',(723,387),(735,473)),
]
SOURCE=np.array([p for _,p,_ in LANDMARKS]+[(0,0),(1122,0),(1122,1402),(0,1402),(561,0),(1122,701),(561,1402),(0,701)],float)
TARGET=np.array([((p[0]-363)/581*1064+31,(p[1]-271)/730*1360+5) for _,_,p in LANDMARKS]+[(0,0),(1122,0),(1122,1402),(0,1402),(561,0),(1122,701),(561,1402),(0,701)],float)
# Landmark coordinates measured on the normalized reference grid.
MEASURED=np.array([
 (376,42),(663,42),(536,216),(614,216),(581,251),(562,326),(566,388),
 (570,568),(524,695),(622,804),(548,842),(140,1012),(337,1232),(378,952),
 (1023,231),(840,331),(879,363),(385,790),(779,510),
 (1067,663),(865,886),(124,1296),(985,1300),(236,1104),(884,1070),
 (293,670),(712,381)
],float)
TARGET[:len(MEASURED)]=MEASURED
LANDMARKS=[(n,s,((t[0]-31)/1064*581+363,(t[1]-5)/1360*730+271)) for (n,s,_),t in zip(LANDMARKS,MEASURED)]
# A dense affine strip preserves fretboard straightness during contour alignment.
indices=[15,16,13]
matrix=np.linalg.solve(np.column_stack([SOURCE[indices],np.ones(3)]),TARGET[indices])
strip=[]
for t in np.linspace(.02,.98,20):
    left=(1-t)*np.array([848,326])+t*np.array([342,916])
    right=(1-t)*np.array([888,362])+t*np.array([401,960])
    for f in [0,.5,1]:strip.append(left*(1-f)+right*f)
strip=np.array(strip)
SOURCE=np.vstack([SOURCE,strip])
TARGET=np.vstack([TARGET,np.column_stack([strip,np.ones(len(strip))])@matrix])
TRI=Delaunay(SOURCE)

def warp(points):
    points=np.asarray(points);ids=TRI.find_simplex(points)
    valid=ids>=0;out=points.copy();ix=ids[valid]
    b=np.einsum('nij,nj->ni',TRI.transform[ix,:2],points[valid]-TRI.transform[ix,2])
    b=np.column_stack([b,1-b.sum(1)])
    out[valid]=np.einsum('ni,nij->nj',b,TARGET[TRI.simplices[ix]])
    return out

def record():
    ratios=[]
    for t in TRI.simplices:
        a,b=SOURCE[t],TARGET[t]
        det=lambda x:float(np.linalg.det(np.stack([x[1]-x[0],x[2]-x[0]])))
        ratios.append(det(b)/det(a))
    assert min(ratios)>0,'Mesh foldover'
    (ROOT/'docs/geometry-landmarks.json').write_text(json.dumps({'method':'piecewise affine vector-coordinate correction','landmarks':[{'name':n,'source_xy':s,'reference_photo_xy':r,'target_xy':t.tolist()} for (n,s,r),t in zip(LANDMARKS,TARGET)],'minimum_triangle_area_ratio':min(ratios)},indent=2))
