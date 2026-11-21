"""PNG structure and offline spectrogram helpers."""
import io, struct, zlib, wave
from pathlib import Path
import numpy as np
from PIL import Image


def output_dir(name):
    path = Path(__file__).resolve().parents[2] / 'outputs' / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def png(data):
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    chunks=[]; at=8
    while at<len(data):
        size=struct.unpack('>I',data[at:at+4])[0]
        kind=data[at+4:at+8]; body=data[at+8:at+8+size]
        crc=struct.unpack('>I',data[at+8+size:at+12+size])[0]
        assert zlib.crc32(kind+body)&0xffffffff == crc
        chunks.append((kind,body)); at+=12+size
        if kind==b'IEND': return chunks,data[at:]
    raise ValueError('Missing IEND')
def spectrogram(data,output):
    with wave.open(io.BytesIO(data)) as w:
        assert w.getsampwidth()==2
        rate=w.getframerate(); channels=w.getnchannels()
        a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,channels).mean(axis=1)
    win=2048; hop=512
    frames=np.lib.stride_tricks.sliding_window_view(a,win)[::hop]
    db=20*np.log10(np.abs(np.fft.rfft(frames*np.hanning(win),axis=1))+1e-6)
    pixels=np.clip((db-(db.max()-90))/90*255,0,255).T[::-1].astype('uint8')
    Image.fromarray(pixels).save(output)
    print('WAV:',rate,'Hz;',channels,'channels;',len(a)/rate,'seconds')
    return pixels
