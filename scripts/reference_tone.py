"""Broad color/illumination correction without importing photographic texture."""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from align_geometry import warp

ROOT=Path(__file__).resolve().parents[1]

def corrected_source(src):
    h,w=src.shape[:2]
    photo=np.array(Image.open(ROOT/'master/reference.png').convert('RGB'),np.float32)
    # Small textile-black allowance, removed only from the measurement used for
    # ink tone. The fixed reference image and comparison remain unmodified.
    photo=np.maximum(photo-np.array([5,5,5],np.float32),0)
    low_reference=cv2.GaussianBlur(photo,(0,0),13)
    yy,xx=np.mgrid[:h,:w]
    target=warp(np.column_stack([xx.ravel(),yy.ravel()])).reshape(h,w,2)
    mx=((target[:,:,0]-31)/1064*581+363).astype('float32')
    my=((target[:,:,1]-5)/1360*730+271).astype('float32')
    wanted=cv2.remap(low_reference,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    low_source=cv2.GaussianBlur(src.astype('float32'),(0,0),24)
    luminance=np.array([.2126,.7152,.0722],np.float32)
    gain=np.clip((wanted@luminance)/np.maximum(low_source@luminance,6),.18,1.35)
    gain=cv2.GaussianBlur(gain,(0,0),10)
    # Scalar gain avoids cyan fringes on neutral metal highlights. The local
    # reference contributes only broad luminance, never its fabric texture.
    bright=np.clip((src@luminance)/np.maximum(low_source@luminance,6)-1,0,1)
    gain=gain**(1-.18*bright)
    toned=np.clip(src.astype('float32')*gain[:,:,None],0,255)
    lab=cv2.cvtColor(toned/255,cv2.COLOR_RGB2LAB)
    red=(src[:,:,0].astype(float)>1.6*src[:,:,1])&(src[:,:,0]>50)
    saturation=np.where(red,.62,.88)
    lab[:,:,1:]*=saturation[:,:,None]
    return np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255)
