"""Corto Senda v1: gráficos y música originales; sin servicios ni material de terceros.

python generar_intro.py
Requiere Pillow, numpy e imageio-ffmpeg. No modifica tesis, datos ni configuración.
"""
from pathlib import Path
import argparse
import json
import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WEB = ROOT / 'Sistema Rutinas PG/frontend/public/media'
W, H, FPS, SECONDS = 1920, 1080, 30, 30
BG, PANEL, INK, MUTED, GREEN, GOLD = '#151e1b', '#1d2a23', '#f2f4eb', '#bfccbd', '#c4ed95', '#e8bd65'
CREAM, FOREST = '#f6f3eb', '#244b3b'
FONT_DIR = Path('C:/Windows/Fonts')
FONTS = {}

def font(size, weight='regular'):
    key = (int(size), weight)
    if key not in FONTS:
        name = {'regular': 'segoeui.ttf', 'bold': 'segoeuib.ttf', 'light': 'segoeuil.ttf'}[weight]
        FONTS[key] = ImageFont.truetype(str(FONT_DIR / name), int(size))
    return FONTS[key]

def ease(v):
    v = max(0, min(1, v))
    return 1 - (1 - v) ** 3

def text(d, xy, value, size=40, color=INK, weight='regular', anchor=None):
    d.text(tuple(map(round, xy)), value, font=font(size, weight), fill=color, anchor=anchor)

def rr(d, box, fill=PANEL, outline=None, radius=30, width=2):
    d.rounded_rectangle(tuple(map(round, box)), radius=radius, fill=fill, outline=outline, width=width)

def check(d, x, y, size=25, color=GREEN, width=5):
    d.line([(x-size*.45, y), (x-size*.1, y+size*.32), (x+size*.5, y-size*.4)], fill=color, width=width, joint='curve')

def arrow(d, x, y, size=40, color=GREEN, width=5):
    d.line([(x-size, y), (x+size*.5, y)], fill=color, width=width)
    d.line([(x, y-size*.5), (x+size*.5, y), (x, y+size*.5)], fill=color, width=width, joint='curve')

def logo(d, x, y, scale=2, color=GREEN, progress=1):
    # Misma geometría de frontend/src/marca/identidad.mjs, símbolo Camino.
    points = [(10,36), (24,36)]
    points += [(24+8*math.cos(a),28+8*math.sin(a)) for a in np.linspace(math.pi/2,-math.pi/2,40)]
    points += [(23,20)]
    points += [(23+5*math.cos(a),15+5*math.sin(a)) for a in np.linspace(math.pi/2,3*math.pi/2,30)]
    points += [(38,10)]
    count = max(2, int(len(points)*progress))
    pts = [(x+a*scale,y+b*scale) for a,b in points[:count]]
    d.line(pts, fill=color, width=max(2,round(7*scale)), joint='curve')
    r = 3.5*scale
    for a,b in pts:
        d.ellipse((a-r,b-r,a+r,b+r),fill=color)
    if progress > .95:
        arrow_pts=[(x+32*scale,y+5*scale),(x+39*scale,y+10*scale),(x+32*scale,y+15*scale)]
        d.line(arrow_pts, fill=color,width=max(2,round(4*scale)),joint='curve')
        for a,b in arrow_pts:d.ellipse((a-2*scale,b-2*scale,a+2*scale,b+2*scale),fill=color)

def brand(d, x=100, y=66, color=INK, size=39):
    logo(d,x,y-6,1.25,color)
    text(d,(x+75,y-5),'Senda',size,color,'bold')

def pill(d, x, y, label, color=GREEN, light=False):
    width = d.textlength(label,font=font(25,'bold'))+46
    rr(d,(x,y,x+width,y+52), '#e6ebdf' if light else '#26372f',radius=26)
    text(d,(x+23,y+7),label,25,color,'bold')

def label(d, value, x=110, y=253, color=GREEN):
    d.line((x,y+21,x+45,y+21),fill=color,width=3)
    text(d,(x+65,y),value,26,color,'bold')

def background(t, light=False):
    im = Image.new('RGB',(W,H),CREAM if light else BG)
    d = ImageDraw.Draw(im)
    line = '#e6e8df' if light else '#22352b'
    # Líneas de un camino: movimiento continuo, sin destellos ni cortes blancos.
    for n in range(7):
        points=[]
        for x in range(0,W+20,20):
            y = 760+n*72+65*math.sin(x/470+t*.17+n*.18)
            points.append((x,y))
        d.line(points,fill=line,width=2)
    d.ellipse((1220,-400,2320,700), outline=line,width=2)
    d.ellipse((1320,-300,2220,600), outline=line,width=2)
    return im

def furniture(d, t, number, light=False):
    ink = FOREST if light else INK
    brand(d,color=ink)
    text(d,(1810,85),'TU PRÓXIMO PASO',23,FOREST if light else MUTED,anchor='ra')
    text(d,(110,995),'ENTRENAMIENTO   /   ALIMENTACIÓN   /   TU PROGRESO',22,FOREST if light else MUTED)
    text(d,(1810,995),f'{number:02d} / 06',22,FOREST if light else MUTED,anchor='ra')
    d.line((110,1053,1810,1053),fill='#d3d9cb' if light else '#33463a',width=3)
    d.line((110,1053,110+1700*min(t/SECONDS,1),1053),fill=FOREST if light else GREEN,width=4)

def draw_hook(d, u):
    label(d,'EL PRIMER PASO',y=228)
    text(d,(105,323),'Quieres empezar.',110,INK,'bold')
    text(d,(105,453),'¿Por dónde?',156,GREEN,'bold')
    text(d,(112,672),'Entrenar. Comer mejor. Ver tu avance.',43,MUTED)
    for i,(word,yy) in enumerate([('¿Qué entreno?',290),('¿Qué como?',440),('¿Cómo avanzo?',590)]):
        off=round(100*(1-ease((u-.3-i*.18)/.7)))
        xx=1275+off
        rr(d,(xx,yy,1805+off,yy+118),PANEL,'#3c5141',24)
        text(d,(xx+30,yy+30),word,41,INK,'bold')
        text(d,(xx+475,yy+30),'?',40,GREEN,'bold')

def draw_intro(d,u):
    p=ease(u/.9)
    logo(d,92,255,6,GREEN,p)
    text(d,(455,277),'Senda',186,INK,'bold')
    text(d,(110,566),'Un sistema web.',65,INK,'bold')
    text(d,(110,653),'Tu siguiente paso, más claro.',65,GREEN,'bold')
    for i,title in enumerate(['Entrenamiento','Alimentación','Tu progreso']):
        x=111+i*564
        offset=35*(1-ease((u-.45-i*.13)/.6))
        rr(d,(x,809+offset,x+530,903+offset),PANEL,'#3c5141',24)
        text(d,(x+30,830+offset),title,36,INK,'bold')
        arrow(d,x+480,856+offset,20)

def draw_training(d,u):
    label(d,'01 / ENTRENAMIENTO')
    text(d,(106,353),'Ten claro qué',104,INK,'bold')
    text(d,(106,476),'entrenar hoy.',104,GREEN,'bold')
    text(d,(112,651),'Una rutina según tu perfil.',43,MUTED)
    text(d,(112,716),'Registra series, carga y descansos.',37,MUTED)
    x=1070+round(65*(1-ease(u/.7)))
    rr(d,(x,226,x+735,890),PANEL,'#4e6153',34)
    pill(d,x+38,263,'TU SESIÓN')
    text(d,(x+38,348),'Una serie a la vez.',51,INK,'bold')
    text(d,(x+38,424),'Rutina · Registro · Descanso',30,MUTED)
    for i in range(3):
        y=502+i*99
        active=u>1+i*.57
        rr(d,(x+38,y,x+697,y+80),'#26372f' if active else '#18241e',radius=18)
        text(d,(x+60,y+15),f'Serie {i+1}',33,INK,'bold')
        text(d,(x+255,y+20),'Carga  /  Repeticiones',25,MUTED)
        if active: check(d,x+651,y+42,27)
        else: d.ellipse((x+631,y+21,x+669,y+59),outline='#4e6153',width=2)
    text(d,(x+38,830),'VISTA CONCEPTUAL · SIN DATOS PERSONALES',19,MUTED)

def draw_food(d,u):
    label(d,'02 / ALIMENTACIÓN',color=FOREST)
    text(d,(106,353),'Organiza',104,FOREST,'bold')
    text(d,(106,476),'tus comidas.',104,FOREST,'bold')
    text(d,(112,651),'Menú, porciones y compras.',43,FOREST)
    text(d,(112,716),'Todo en el mismo lugar.',37,'#526357')
    x=1070+round(65*(1-ease(u/.7)))
    rr(d,(x,226,x+735,890),'#fffdf8','#d3d9cb',34)
    pill(d,x+38,263,'TU ALIMENTACIÓN',FOREST,True)
    text(d,(x+38,348),'Del menú a tu mesa.',49,FOREST,'bold')
    # Plato abstracto editorial; no representa dosis ni prescripción.
    cx,cy=x+220,596
    d.ellipse((cx-150,cy-150,cx+150,cy+150),fill='#edece2',outline='#d3d9cb',width=2)
    d.ellipse((cx-125,cy-125,cx+125,cy+125),fill='#fffdf8')
    d.pieslice((cx-108,cy-108,cx+108,cy+108),-90,88,fill='#a1b598')
    d.pieslice((cx-108,cy-108,cx+108,cy+108),92,210,fill='#e8bd65')
    d.pieslice((cx-108,cy-108,cx+108,cy+108),214,266,fill='#c88761')
    for i,s in enumerate(['Tu menú','Tus porciones','Tus compras']):
        yy=479+i*91
        check(d,x+421,yy+22,22,FOREST,4)
        text(d,(x+457,yy),s,30,FOREST,'bold')
    rr(d,(x+38,777,x+697,837),'#e6ebdf',radius=18)
    text(d,(x+65,790),'Planifica tu semana.',30,FOREST,'bold')
    text(d,(x+38,858),'ILUSTRACIÓN CONCEPTUAL',19,'#526357')

def draw_progress(d,u):
    label(d,'03 / MI SENDA')
    text(d,(106,353),'Cada paso',104,INK,'bold')
    text(d,(106,476),'cuenta.',118,GREEN,'bold')
    text(d,(112,651),'Registra tu avance.',43,MUTED)
    text(d,(112,716),'Puntos, niveles e insignias personales.',35,MUTED)
    x=1070+round(65*(1-ease(u/.7)))
    rr(d,(x,226,x+735,890),PANEL,'#4e6153',34)
    pill(d,x+38,263,'TU PROGRESO')
    text(d,(x+38,348),'Haz visible tu constancia.',43,INK,'bold')
    for i in range(7):
        bh=(90+i*25)*ease((u-.25-i*.08)/1.1)
        bx=x+55+i*91
        rr(d,(bx,665-bh,bx+55,665),GREEN if i==6 else '#4e7156',radius=10)
    for i,s in enumerate(['Puntos','Niveles','Insignias']):
        xx=x+38+i*224
        rr(d,(xx,714,xx+210,812),'#26372f',radius=18)
        text(d,(xx+105,744),s,28,GOLD if i==2 else INK,'bold',anchor='ma')
    text(d,(x+38,848),'ESQUEMA ILUSTRATIVO · NO ES UN RESULTADO REAL',18,MUTED)

def draw_close(d,u,variant):
    # Seis segundos de cierre legible; el CTA permanece los últimos cuatro.
    if u<1.8:
        text(d,(960,335),'No tienes que hacerlo todo hoy.',76,INK,'bold',anchor='ma')
        text(d,(960,454),'Solo dar el primer paso.',100,GREEN,'bold',anchor='ma')
        logo(d,839,653,5,GREEN,ease(u/.7))
        return
    logo(d,643,233,3.5,GREEN)
    text(d,(835,231),'Senda',112,INK,'bold')
    if variant=='web':
        text(d,(960,433),'Tu siguiente paso empieza hoy.',77,INK,'bold',anchor='ma')
        rr(d,(609,591,1311,706),GREEN,radius=58)
        text(d,(932,613),'Crea tu cuenta gratis',43,FOREST,'bold',anchor='ma')
        arrow(d,1250,649,25,FOREST)
        text(d,(960,762),'Entrenamiento + alimentación + tu progreso',35,MUTED,anchor='ma')
        text(d,(960,846),'Para personas adultas · Orientación general',25,MUTED,anchor='ma')
    else:
        text(d,(960,437),'Tecnología para dar el siguiente paso.',67,INK,'bold',anchor='ma')
        text(d,(960,575),'PROYECTO DE GRADUACIÓN',30,GREEN,'bold',anchor='ma')
        text(d,(960,645),'Cristopher Leonardo Zepeda Esquivel',44,INK,'bold',anchor='ma')
        text(d,(960,725),'Universidad Mariano Gálvez de Guatemala',31,MUTED,anchor='ma')
        text(d,(960,784),'El Progreso, Jutiapa',29,MUTED,anchor='ma')

SCENES=[(0,4,draw_hook),(4,8,draw_intro),(8,13,draw_training),(13,18,draw_food),(18,24,draw_progress),(24,30,draw_close)]

def frame(t,variant='web'):
    idx=next((i for i,(a,b,_) in enumerate(SCENES) if a<=t<b),5)
    start,end,fn=SCENES[idx]
    light=idx==3
    im=background(t,light)
    layer=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(layer)
    fn(d,t-start,variant) if idx==5 else fn(d,t-start)
    # Breve desplazamiento inicial; cada escena tiene varios segundos de lectura.
    dy=round(32*(1-ease((t-start)/.55)))
    if dy: layer=layer.transform((W,H),Image.Transform.AFFINE,(1,0,0,0,1,-dy))
    # Disolución de 0.2 s sobre el mismo fondo, sin parpadeos.
    alpha=min(1,(t-start)/.2,1 if idx==5 else (end-t)/.18)
    alpha=max(0,alpha)
    if alpha<1: layer.putalpha(layer.getchannel('A').point(lambda a:round(a*alpha)))
    im.paste(layer,(0,0),layer)
    furniture(ImageDraw.Draw(im),t,idx+1,light)
    return im

def soundtrack(path):
    """Composición procedimental original, 112 BPM, re menor / si bemol / fa / do."""
    sr=48000
    count=sr*SECONDS
    left=np.zeros(count,dtype=np.float64)
    right=np.zeros(count,dtype=np.float64)
    rng=np.random.default_rng(31102026)
    def note(midi): return 440*2**((midi-69)/12)
    def add(at,duration,freq,amp,kind='pluck',pan=0):
        offset=round(at*sr); length=min(round(duration*sr),count-offset)
        if length<=0:return
        t=np.arange(length)/sr
        if kind=='pad':
            env=np.minimum(1,t/.32)*np.minimum(1,(duration-t)/.6)
            signal=(np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2.003*t))*env*.5
        elif kind=='kick': signal=np.sin(2*np.pi*(46*t+7*(1-np.exp(-t*25))))*np.exp(-t*17)
        elif kind=='hat': signal=rng.normal(0,1,length)*np.exp(-t*65)*np.minimum(1,t/.002)*.27
        else: signal=(np.sin(2*np.pi*freq*t)+.2*np.sin(2*np.pi*freq*2*t))*np.exp(-t*5)*np.minimum(1,t/.008)
        left[offset:offset+length]+=signal*amp*math.sqrt((1-pan)/2)
        right[offset:offset+length]+=signal*amp*math.sqrt((1+pan)/2)
    beat=60/112
    chords=[(50,57,62,65),(46,53,58,62),(41,53,57,60),(48,55,60,64)]
    for bar in range(14):
        at=bar*4*beat
        chord=chords[bar%4]
        for j,m in enumerate(chord): add(at,4*beat+.55,note(m+12),.075,'pad',(j-1.5)/4)
        for n in range(8):
            when=at+n*beat/2
            if when<28.7: add(when,1.0,note(chord[n%4]+24),.09,'pluck',-.35 if n%2 else .35)
        for n in range(4):
            when=at+n*beat
            if 3.8<when<28: add(when,.5,50,.27,'kick')
            if 7.8<when<27.8: add(when+beat/2,.12,0,.09,'hat',.15)
    # Resonancia final; cierre musical completo, no corte abrupto.
    for m in [50,57,62,65,74]: add(28.0,2.0,note(m),.12,'pad')
    stereo=np.stack([left,right],axis=1)
    for delay,gain in [(.18,.18),(.36,.08)]:
        off=round(delay*sr); stereo[off:]+=np.stack([right,left],axis=1)[:-off]*gain
    axis=np.arange(count)/sr
    fade=np.minimum(1,axis/.3)*np.minimum(1,(SECONDS-axis)/1.1)
    stereo*=fade[:,None]
    stereo*=.84/max(1e-9,np.abs(stereo).max())
    with wave.open(str(path),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr)
        out.writeframes((stereo*32767).astype('<i2').tobytes())

def render(variant):
    target=HERE/f'senda-intro-{variant}-1080p.mp4'
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-y','-v','warning','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-', '-i',str(HERE/'senda-musica-original.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(SECONDS),str(target)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for n in range(FPS*SECONDS):
            proc.stdin.write(frame(n/FPS,variant).tobytes())
            if n%150==0: print(f'{variant}: {n}/{FPS*SECONDS}',flush=True)
    finally: proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('Falló FFmpeg')
    return target

def package(web):
    WEB.mkdir(parents=True,exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg,'-y','-v','warning','-i',str(web),'-vf','scale=1280:720','-c:v','libx264','-preset','slow','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(WEB/'senda-intro-v1.mp4')],check=True)
    # Portada exclusiva: legible antes de pulsar reproducción y sin contexto previo.
    poster=background(6)
    d=ImageDraw.Draw(poster)
    brand(d)
    pill(d,1538,67,'30 SEGUNDOS')
    logo(d,1180,246,10,GREEN)
    label(d,'CONOCE SENDA',y=257)
    text(d,(106,363),'Tu siguiente',112,INK,'bold')
    text(d,(106,492),'paso empieza aquí.',112,GREEN,'bold')
    text(d,(112,690),'Entrenamiento. Alimentación. Tu progreso.',42,MUTED)
    rr(d,(112,805,684,908),GREEN,radius=52)
    d.polygon([(150,836),(150,878),(186,857)],fill=FOREST)
    text(d,(210,827),'Descubre cómo funciona',34,FOREST,'bold')
    poster.resize((1280,720),Image.Resampling.LANCZOS).save(WEB/'senda-intro-poster-v1.webp',quality=88)
    poster.save(HERE/'senda-portada.png')
    sheet=Image.new('RGB',(1280,1080),BG)
    for i,t in enumerate([1.5,6,10.5,15.5,20.5,28]):
        sheet.paste(frame(t).resize((640,360),Image.Resampling.LANCZOS),((i%2)*640,(i//2)*360))
    sheet.save(HERE/'senda-guion-visual.jpg',quality=92)
    metadata={'version':1,'duration_seconds':SECONDS,'fps':FPS,'master_resolution':[W,H],'web_resolution':[1280,720],'audio':'Música instrumental original sintetizada; sin voz','date':'2026-10-31','scenes':[{'start':a,'end':b,'scene':fn.__name__} for a,b,fn in SCENES]}
    (HERE/'manifiesto.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    HERE.mkdir(parents=True,exist_ok=True)
    if args.preview:
        WEB.mkdir(parents=True,exist_ok=True)
        # Muestras sin codificar vídeo, para revisar composición.
        for t in [1.5,6,10.5,15.5,20.5,28]: frame(t).save(HERE/f'escena-{t}.jpg')
        sheet=Image.new('RGB',(1280,1080),BG)
        for i,t in enumerate([1.5,6,10.5,15.5,20.5,28]):sheet.paste(frame(t).resize((640,360)),((i%2)*640,(i//2)*360))
        sheet.save(HERE/'senda-guion-visual.jpg',quality=92)
    else:
        soundtrack(HERE/'senda-musica-original.wav')
        web=render('web')
        render('presentacion')
        package(web)
        print('Entrega terminada.',flush=True)
