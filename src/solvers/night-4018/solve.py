import io
import struct
import sys
import zipfile
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forensic_tools import output_dir, png
out_dir=output_dir('night-4018')
d=Path(__file__).with_name('night_4018.png').read_bytes()
chunks,tail=png(d)
header=chunks[0][1]
w,h=struct.unpack('>II',header[:8])
assert header[8:] == bytes([8,2,0,0,0]), 'Expected noninterlaced RGB8'
raw=zlib.decompress(b''.join(v for k,v in chunks if k==b'IDAT'))
stride=1+3*w
assert len(raw)%stride==0
actual=len(raw)//stride
print('Declared:',w,h,'scanline height:',actual,'extra rows:',actual-h)
assert actual>h
out=bytearray(d[:8])
for k,v in chunks:
    if k==b'IHDR': v=v[:4]+struct.pack('>I',actual)+v[8:]
    out+=struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v)&0xffffffff)
Path(out_dir/'repaired.png').write_bytes(out)
rgb=np.asarray(Image.open(io.BytesIO(out)).convert('RGB'),dtype=float)/255
lin=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4)
x=(lin@np.array([0.4124564,0.3575761,0.1804375]))/0.95047
y=lin@np.array([0.2126729,0.7151522,0.0721750])
def f(t): return np.where(t>(6/29)**3,np.cbrt(t),t/(3*(6/29)**2)+4/29)
a=500*(f(x)-f(y))
band=a[h:]
lo,hi=np.percentile(band,[1,99])
Image.fromarray(np.clip((band-lo)/(hi-lo)*255,0,255).astype('uint8')).save(out_dir/'hidden-band.png')
print('Saved repaired.png and hidden-band.png; read the flag visually')
if tail:
    z=zipfile.ZipFile(io.BytesIO(tail))
    for n in z.namelist(): print('Tail decoy:',n,z.read(n).decode(errors='replace'))
