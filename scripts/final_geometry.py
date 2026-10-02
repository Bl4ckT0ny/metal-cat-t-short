"""Reference-contour correction; selected reconstruction supplies guitar detail.

The photograph stays immutable. Its print contours replace the materially
different reconstructed face, fur and splashes. Only the seven-string neck and
headstock are retained from reconstruction_reference, after alignment.
"""
import numpy as np
import cv2
from PIL import Image
from scipy.interpolate import LinearNDInterpolator
from align_geometry import ROOT, SOURCE, TARGET, warp
from reference_tone import corrected_source

def final_warp(points):
    p=warp(points)
    p[:,1]=17+(p[:,1]-5)*1337/1360
    return p

def prepare(src,areas,names):
    h,w=src.shape[:2]
    yy,xx=np.mgrid[:h,:w]
    dest=TARGET.copy();dest[:,1]=17+(dest[:,1]-5)*1337/1360
    inverse=LinearNDInterpolator(dest,SOURCE)(np.column_stack([xx.ravel(),yy.ravel()])).reshape(h,w,2).astype('float32')
    inverse=np.nan_to_num(inverse,nan=-100)
    maps=(inverse[:,:,0],inverse[:,:,1])
    mapped_areas=cv2.remap(areas,*maps,cv2.INTER_NEAREST)
    guitar=cv2.remap(corrected_source(src),*maps,cv2.INTER_LINEAR)
    photo=Image.open(ROOT/'master/reference.png').convert('RGB').crop((363,271,944,1001))
    reference=np.zeros((h,w,3),np.float32)
    reference[17:1354,31:1095]=np.array(photo.resize((1064,1337),Image.Resampling.LANCZOS),np.float32)
    # Suppress unprinted garment outside the character. Chromatic splashes
    # remain eligible independently of the character silhouette.
    figure=np.zeros((h,w),np.uint8)
    outline=np.array([(380,35),(448,140),(540,155),(620,120),(675,35),(670,210),
      (738,338),(779,385),(841,432),(867,548),(822,625),(834,737),
      (895,715),(966,649),(1074,653),(1092,708),(999,784),(928,911),
      (1010,1110),(1087,1280),(1086,1360),(867,1360),(806,1195),
      (716,1081),(638,996),(542,988),(416,1242),(220,1333),(40,1334),
      (77,1210),(166,1103),(184,955),(259,837),(282,730),(241,672),
      (269,589),(332,470),(320,354),(344,268),(397,183)],np.int32)
    cv2.fillPoly(figure,[outline],1)
    body=(mapped_areas==names.index('guitar_body')).astype('uint8')
    figure|=cv2.dilate(body,np.ones((9,9),np.uint8))
    mx=reference.max(2);mn=reference.min(2)
    saturation=(mx-mn)/np.maximum(mx,1)
    visible=((mx>28)&(saturation>.16))|((figure>0)&(mx>20))
    # Smooth alpha-like falloff near the garment threshold; no hard halo.
    coverage=np.clip((mx-25)/20,0,1)
    coverage=np.where(figure>0,np.clip((mx-16)/8,0,1),coverage)
    reference=np.maximum(reference-8,0)*coverage[:,:,None]
    reference[~visible]=0
    hardware=np.isin(mapped_areas,[i for i,n in enumerate(names) if n in ('neck','headstock') or n.startswith('tuner_')])
    # Original feline paw regions override the neck mask and remain reference-derived.
    rgb=reference.copy();rgb[hardware]=guitar[hardware]
    visible=(rgb.max(2)>9)
    return rgb,mapped_areas,visible
