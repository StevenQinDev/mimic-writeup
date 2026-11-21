import io
import struct
import sys
import zipfile
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forensic_tools import output_dir, png, spectrogram
out=output_dir('halvards-light')
d=Path(__file__).with_name('halvards_light.png').read_bytes()
chunks,tail=png(d)
z=zipfile.ZipFile(io.BytesIO(tail))
a=np.asarray(Image.open(io.BytesIO(d)).convert('RGB'),dtype=np.float32)
Image.fromarray(np.clip((a-5)*255/35,0,255).astype(np.uint8)).save(out/'dark-water.png')
z.setpassword(b'marigold')
for info in z.infolist(): print(info.filename,info.file_size,'encrypted:',bool(info.flag_bits&1))
# ZIP password: MARIGOLD read from enhanced dark water, converted to lowercase.
log=z.read('keeper_log.txt').decode()
(out/'keeper_log.txt').write_text(log,encoding='utf-8')
print(log)
spectrogram(z.read('signal.wav'),out/'spectrogram.png')
ihdr=chunks[0][1]; width,height=struct.unpack('>II',ihdr[:8])
print('IHDR:',width,height, list(ihdr[8:]))
raw=zlib.decompress(b''.join(v for k,v in chunks if k==b'IDAT'))
stride=len(raw)//height
filters=raw[::stride]
(out/'scanline-headers.bin').write_bytes(filters)
print('Filter values:',sorted(set(filters)),'first 100:',list(filters[:100]))
