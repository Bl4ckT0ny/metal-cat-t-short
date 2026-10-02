"""Raster, XML, immutable-source and normalized comparison checks."""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from final_geometry import final_warp as warp

ROOT=Path(__file__).resolve().parents[1]
SVG='{http://www.w3.org/2000/svg}'
BOXES={'reference':[363,271,944,1001], 'reconstruction_reference':[31,5,1095,1365], 'vector':[31,17,1095,1354]}
SIZES=[1254,627,314]

def black(im):
    im=im.convert('RGBA');out=Image.new('RGBA',im.size,(0,0,0,255));out.alpha_composite(im)
    return out.convert('RGB')

def normalized(im,box,size):
    im=black(im).crop(box)
    # Isotropic fit, no stretching. 1254/627/314 denote canvas height.
    width=round(size*.8);scale=min(width/im.width,size/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    out=Image.new('RGB',(width,size));out.paste(im,((width-im.width)//2,(size-im.height)//2))
    return out

def metrics(a,b):
    a=np.array(a).astype('float32');b=np.array(b).astype('float32')
    x=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY);y=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY)
    blur=lambda z:cv2.GaussianBlur(z,(11,11),1.5)
    mx,my=blur(x),blur(y)
    vx,vy=blur(x*x)-mx*mx,blur(y*y)-my*my
    cov=blur(x*y)-mx*my
    ssim=((2*mx*my+6.5025)*(2*cov+58.5225)/((mx*mx+my*my+6.5025)*(vx+vy+58.5225))).mean()
    return {'rgb_mae_0_255':round(float(abs(a-b).mean()),3),'luma_ssim':round(float(ssim),5)}

def run():
    out=ROOT/'preview/comparisons';out.mkdir(exist_ok=True)
    root=ET.parse(ROOT/'vector/metal-cat-master.svg').getroot()
    layers=[g.attrib.get('id') for g in root.findall(SVG+'g')]
    assert layers==['DARK_GRAY','CREAM','BROWN','ORANGE','RED'],layers
    assert not root.findall('.//'+SVG+'image'),'Raster embedding is forbidden'
    assert not root.findall('.//'+SVG+'filter'),'No raster filters'
    for region in ['face','paw_strumming','paw_fretting','paw_left_foot','paw_right_foot','guitar_body','neck','headstock']:
        assert any(g.attrib.get('data-geometry')==region and len(g)>0 for g in root.iter(SVG+'g')),region
    for kind in ['tuner_post','tuner_knob']:
        found={g.attrib['data-geometry'] for g in root.iter(SVG+'g') if g.attrib.get('data-geometry','').startswith(kind+'_') and len(g)>0}
        assert found=={f'{kind}_{i}' for i in range(1,8)},found
    ims={'Reference':Image.open(ROOT/'master/reference.png'),
         'Source':Image.open(ROOT/'master/reconstruction_reference.png'),
         'Vector':Image.open(ROOT/'preview/iterations/metal-cat-master.png')}
    result={'historical_baselines_available': (ROOT/'preview/iterations/iteration-03.png').exists(), 'normalization':{'method':'Saturation-derived fixed crops; aspect-preserving fit on black 4:5 canvas','boxes_xyxy':BOXES,'sizes_are':'canvas height in pixels','crop_detector':'(max-min)/(max+1) > 0.3 and max > 70, RGB in 0..255'},'comparisons':{}}
    for size in SIZES:
        row=[]
        for title,im in ims.items():
            key={'Reference':'reference','Source':'reconstruction_reference','Vector':'vector'}[title]
            n=normalized(im,BOXES[key],size)
            n.save(out/f'{title.lower()}-{size}.png');row.append(n)
        canvas=Image.new('RGB',(row[0].width*3,size+32),(32,32,32));draw=ImageDraw.Draw(canvas)
        for i,(title,n) in enumerate(zip(ims,row)):
            canvas.paste(n,(i*n.width,32));draw.text((i*n.width+8,8),title,fill='white')
        canvas.save(out/f'comparison-{size}.png')
        result['comparisons'][size]={'source_vs_vector':metrics(row[1],row[2]),'reference_vs_source':metrics(row[0],row[1]),'reference_vs_vector':metrics(row[0],row[2])}
        if (ROOT/'preview/iterations/iteration-03.png').exists():
            pre=normalized(Image.open(ROOT/'preview/iterations/iteration-03.png'),BOXES['reconstruction_reference'],size)
            result['comparisons'][size]['source_vs_vector_before_geometry']=metrics(row[1],pre)
        if (ROOT/'preview/iterations/iteration-06-before-contour-correction.png').exists():
            before=normalized(Image.open(ROOT/'preview/iterations/iteration-06-before-contour-correction.png'),BOXES['reconstruction_reference'],size)
            result['comparisons'][size]['reference_vs_previous_master']=metrics(row[0],before)
            review=Image.new('RGB',(row[0].width*3,size+32),(32,32,32));rd=ImageDraw.Draw(review)
            for i,(title,n) in enumerate(zip(['Reference','Previous master','Corrected master'],[row[0],before,row[2]])):
                review.paste(n,(i*n.width,32));rd.text((i*n.width+8,8),title,fill='white')
            review.save(out/f'correction-review-{size}.png')
    v=black(ims['Vector'])
    aligned=Image.new('RGB',v.size)
    aligned.paste(ims['Reference'].convert('RGB').crop(BOXES['reference']).resize((1064,1337),Image.Resampling.LANCZOS),(31,17))
    rois={'face':(350,45,710,405),'guitar_body':(135,565,630,1230),'paw_strumming':(300,700,460,860),'paw_fretting':(705,431,877,605)}
    result['detail_comparisons']={name:metrics(aligned.crop(box),v.crop(box)) for name,box in rois.items()}
    face_review=Image.new('RGB',(720,390),(32,32,32));fd=ImageDraw.Draw(face_review)
    for i,(title,im) in enumerate([('Reference face',aligned),('Vector face',v)]):
        face_review.paste(im.crop(rois['face']),(i*360,30));fd.text((i*360+8,8),title,fill='white')
    face_review.save(out/'face-reference-vector.png')
    head=v.crop((795,185,1065,380)).resize((1080,780))
    draw=ImageDraw.Draw(head)
    from build_vector import POSTS,KNOBS
    for kind,points,color in [('P',POSTS,'#00e5ff'),('K',KNOBS,'#79ff77')]:
        for i,(x,y) in enumerate(warp(points),1):
            x,y=(x-795)*4,(y-185)*4
            draw.ellipse((x-22,y-22,x+22,y+22),outline=color,width=2)
            draw.text((x-4,y-35),f'{kind}{i}',fill=color)
    head.save(out/'hard-check-headstock.png')
    # Seven string crossings, between the two fretboard borders. Borders are
    # explicitly excluded; darker treble strings remain visible in the crop.
    strings=v.crop((530,570,670,710)).resize((840,840))
    draw=ImageDraw.Draw(strings)
    points=[(594.4,621),(600.5,626),(606.5,630.9),(612.8,636),(619,641),(625.4,646.3),(631.6,651.3)]
    for i,(x,y) in enumerate(warp(points),1):
        x,y=(x-530)*6,(y-570)*6
        draw.ellipse((x-9,y-9,x+9,y+9),outline='#00e5ff',width=2)
        draw.text((x-10,y+12),str(i),fill='#00e5ff')
    strings.save(out/'hard-check-strings.png')
    crops=[(300,700,460,860),(705,431,877,605),(40,1225,210,1340),(850,1225,1090,1370)]
    paws=Image.new('RGB',(800,240))
    for i,b in enumerate(crops):
        p=v.crop(b);p.thumbnail((198,215));paws.paste(p,(i*200,22))
        ImageDraw.Draw(paws).text((i*200+5,5),['Strumming','Fretting','Left foot','Right foot'][i],fill='white')
    paws.save(out/'hard-check-paws.png')
    result['xml_checks']='PASS: five ink layers, semantic regions, seven post regions, seven knob regions, no embedded raster or filters'
    result['hardware_count_method']='Manual visual tracing, annotated source-coordinate crossings; XML region counts are secondary evidence, not proof by themselves.'
    result['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'master').glob('*.png')}
    (ROOT/'docs/verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result['comparisons'],indent=2))

if __name__=='__main__':run()
