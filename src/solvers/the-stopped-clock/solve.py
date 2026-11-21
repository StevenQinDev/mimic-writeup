import base64
import io
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forensic_tools import output_dir, png, spectrogram
out=output_dir('the-stopped-clock')
d=Path(__file__).with_name('last_seen.png').read_bytes()
chunks,tail=png(d)
for k,v in chunks:
    if k==b'tEXt':
        label,value=v.split(b'\0',1)
        try: decoded=base64.b64decode(value,validate=True).decode()
        except (ValueError,UnicodeError): decoded=value.decode(errors='replace')
        print(label,decoded)
z=zipfile.ZipFile(io.BytesIO(tail))
print('Outer ZIP:',z.namelist())
spectrogram(z.read('voicemail.wav'),out/'spectrogram.png')
# Password transcribed from the spectrogram clue and the clock face.
inner=zipfile.ZipFile(io.BytesIO(z.read('leo_diary.zip')))
diary=inner.read('diary.txt',pwd=b'clock_0445').decode()
(out/'diary.txt').write_text(diary,encoding='utf-8')
print(diary)
for token in re.findall(r'UkJI[A-Za-z0-9+/=]+',diary): print(base64.b64decode(token).decode())
page=Image.open(io.BytesIO(inner.read('torn_page.png',pwd=b'clock_0445'))).convert('RGB')
a=np.asarray(page)
Image.fromarray((a[:,:,0]&1)*255).save(out/'red-lsb.png')
print('Saved red-lsb.png; suffix requires visual reading')
