# Run with full-res source PNGs only; no thumbnails. Pillow + NumPy needed.
"""Repair Webbuilder source-generated raster art by reframing full-res PNG crops.

Inputs: three 1536x1024 OpenAI image_gen originals from archived ZIP; generated
site WebP images. No external photography, thumbnails or real customer cases.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
from pathlib import Path
import os
import hashlib, json, math, datetime
import numpy as np

OUT=Path(os.environ.get('WEBBUILDER_IMAGE_OUTPUT', '/mnt/data/webbuilder_visual_fix'));OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(os.environ.get('WEBBUILDER_IMAGE_SOURCE_DIR','/mnt/data'))
A=Image.open(BASE/'a_bright_clean_modern_workspace_scene_a_shallow.png').convert('RGB')
B=Image.open(BASE/'a_clean_well_lit_collage_style_marketing_banner_l.png').convert('RGB')
C=Image.open(BASE/'a_clean_bright_modern_korean_web_landing_page_co.png').convert('RGB')
fontpath='/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'

def background(tint):
    w,h=1024,680
    a=np.array(tint[0],dtype=float).reshape(1,1,3)
    b=np.array(tint[1],dtype=float).reshape(1,1,3)
    yy=np.linspace(0,1,h,dtype=float).reshape(h,1,1)
    xx=np.linspace(0,1,w,dtype=float).reshape(1,w,1)
    t=yy*.72+xx*.28
    rgb=(a*(1-t)+b*t).clip(0,255).astype(np.uint8)
    return Image.fromarray(rgb,'RGB')

def panel(canvas, photo, xy, target_size, radius=24, centering=(.5,.5)):
    x,y=xy;w,h=target_size
    im=ImageOps.fit(photo,(w,h),method=Image.Resampling.LANCZOS,centering=centering)
    mask=Image.new('L',(w,h));md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,w-1,h-1),radius=radius,fill=255)
    # no bright rectangular blank overlay: only a translucent rounded shadow
    shadow=Image.new('RGBA',(w+38,h+50),(0,0,0,0));sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((20,12,20+w,12+h),radius=radius,fill=(17,47,86,65))
    shadow=shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.paste(shadow,(x-20,y-17),shadow)
    canvas.paste(im,(x,y),mask)

def decor(im):
    d=ImageDraw.Draw(im,'RGBA')
    d.ellipse((62,55,146,139),outline=(38,122,183,63),width=4)
    d.ellipse((843,548,1000,706),outline=(21,175,155,65),width=8)
    return im

# 1) Four independent, photo-only industry examples. Crop from generated full-size
# four-service strip, NOT from old 200x133 thumbnail nor from text/monitor border.
industry=decor(background(((239,250,250),(220,238,249))))
# All four regions are inside the photo strip, above text captions.
service_regions=[(777,436,951,680),(958,436,1128,680),(1134,436,1294,680),(1300,436,1524,680)]
for i,box in enumerate(service_regions):
    src=B.crop(box)
    panel(industry,src,(48+i*240,170),(210,324),radius=23,centering=(.5,.43))
# no letters, laptop, or cup inside industry image
industry.save(OUT/'industry-services.webp','WEBP',quality=89,method=6)

# 2) Contact scene. The photographed operator starts to the RIGHT of the text
# column in source3: x>=508 intentionally excludes the auto-generated word cards.
contact=decor(background(((238,249,248),(220,237,249))))
phone_crop=A.crop((1152,340,1464,861))
operator_crop=C.crop((510,11,748,470))
panel(contact,phone_crop,(126,117),(307,475),radius=29,centering=(.5,.49))
panel(contact,operator_crop,(565,100),(333,490),radius=29,centering=(.50,.44))
contact.save(OUT/'mobile-contact.webp','WEBP',quality=90,method=6)

# 3) Domains: use a *generic* generated mock UI from source1 rather than a collage
# whose screen said '제작사례'. Explicit Korean disclosure in the artwork itself.
managed=decor(background(((242,249,253),(224,242,246))))
mock=A.crop((255,150,1140,873))
panel(managed,mock,(50,119),(530,405),radius=24,centering=(.52,.50))
d=ImageDraw.Draw(managed,'RGBA')
# conceptual network, no customer-owned brand/domain names shown
nodes=[(742,211),(863,166),(858,374),(713,436)]
for nx,ny in nodes:
    d.line((684,317,nx,ny),fill=(42,112,172,93),width=6)
    d.ellipse((nx-24,ny-24,nx+24,ny+24),fill=(232,250,249,255),outline=(51,143,161,184),width=4)
    d.ellipse((nx-7,ny-7,nx+7,ny+7),fill=(26,160,157,255))
# text badge below photo, not covering any existing UI
label='가상 홈페이지 화면 예시 · 실제 고객사례 아님'
fnt=ImageFont.truetype(fontpath,23)
metrics=d.textbbox((0,0),label,font=fnt);tw=metrics[2]-metrics[0]
left=50;top=560;right=max(580,left+tw+32)
d.rounded_rectangle((left,top,right,top+47),radius=13,fill=(246,251,255,255),outline=(147,184,216,160),width=2)
d.text((left+15,top+10),label,font=fnt,fill=(34,68,105,255))
managed.save(OUT/'managed-domain.webp','WEBP',quality=89,method=6)

records=[]
for p in sorted(OUT.glob('*.webp')):
    im=Image.open(p)
    records.append({'name':p.name,'size':p.stat().st_size,'width':im.width,'height':im.height,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT/'repair-results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# contact sheet allows compact visual inspection of defects
thumb=Image.new('RGB',(1050,3*745),(248,251,254));d=ImageDraw.Draw(thumb)
font=ImageFont.truetype(fontpath,29)
for i,p in enumerate(sorted(OUT.glob('*.webp'))):
    panel_image=Image.open(p).convert('RGB')
    thumb.paste(panel_image,(13, i*745+10))
    d.text((22,i*745+699),p.name,font=font,fill='#112a48')
thumb.save(OUT/'comparison-sheet.jpg',quality=88)
print(json.dumps(records,ensure_ascii=False,indent=2))