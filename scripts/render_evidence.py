"""Regenerate additional explanatory figures from the unchanged original inputs."""
from pathlib import Path
import sys
import base64
import hashlib
import io
import zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/solvers'))
from forensic_tools import png, spectrogram

def main():
    assets=ROOT/'docs/assets'
    source=ROOT/'src/solvers'
    a=np.asarray(Image.open(source/'halvards-light/halvards_light.png').convert('RGB'),dtype=np.float32)
    Image.fromarray(np.clip((a-5)*255/35,0,255).astype(np.uint8)).save(assets/'halvard-dark-water.png')
    _,tail=png((source/'halvards-light/halvards_light.png').read_bytes())
    with zipfile.ZipFile(io.BytesIO(tail)) as archive:
        archive.setpassword(b'marigold')
        spectrogram(archive.read('signal.wav'),assets/'halvard-spectrogram.png')
    im=Image.open(source/'the-stopped-clock/last_seen.png').convert('RGB')
    im.thumbnail((900,900))
    im.save(assets/'clock-face-context.png')
    chunks,_=png((source/'the-stopped-clock/last_seen.png').read_bytes())
    for kind,value in chunks:
        if kind==b'tEXt':
            key,text=value.split(b'\0',1)
            try:text=base64.b64decode(text,validate=True)
            except ValueError:pass
            print('Clock metadata:',key.decode(),text.decode())
    lines=(source/'honest-hashes/ciphertext.txt').read_text(encoding='utf-8').splitlines()
    canonical=lambda s:s.translate(str.maketrans('асе','ace'))
    digest=hashlib.sha256(b'123456').hexdigest()
    assert canonical(lines[0])==canonical(lines[11])==digest
    print('Hash first line sampled code points:',[(c,f'U+{ord(c):04X}') for c in lines[0] if c in 'aceасе'][:12])
    print('Hash normalized lines 1/12:',digest)
    a=np.asarray(Image.open(source/'the-quiet-hour/the_quiet_hour.png').convert('RGB'),dtype=np.float32)
    diff=a[:,1:]-a[:,:-1]
    lags=np.arange(40,151)
    curves=[]
    for row in (20,260):
        d=diff[row]
        curve=np.array([np.mean(d[lag:]*d[:-lag]) for lag in lags])
        curves.append(curve)
        top=lags[np.argsort(curve)[-8:][::-1]]
        print('Quiet row',row,'top lags:',top.tolist())
    canvas=Image.new('RGB',(960,480),'white');draw=ImageDraw.Draw(canvas)
    draw.text((40,15),'The Quiet Hour: horizontal-difference correlation by row',fill='black')
    for index,(curve,color,row) in enumerate(zip(curves,('#1264a3','#b34a13'),(20,260))):
        baseline=220+index*220
        draw.line((60,baseline,925,baseline),fill='#aaaaaa')
        draw.text((65,baseline-178),f'Row {row}; strongest lag {lags[curve.argmax()]}',fill=color)
        low,high=float(curve.min()),float(curve.max())
        points=[(60+int((lag-40)*865/110),baseline-int((value-low)/(high-low)*150)) for lag,value in zip(lags,curve)]
        draw.line(points,fill=color,width=2)
        for lag in range(40,151,10):draw.text((55+int((lag-40)*865/110),baseline+5),str(lag),fill='black')
    canvas.save(assets/'quiet-correlation.png')

if __name__=='__main__':main()
