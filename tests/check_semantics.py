"""Regression checks for factual claims that structural Markdown checks cannot cover."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import marshal
import sqlite3
import sys
import types
import unicodedata
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOLVERS=ROOT/'src/solvers'
sys.path.insert(0,str(SOLVERS))
from forensic_tools import png

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ct='VW2mfl6UNp2XYoGKO4K9dp9SdZ+RYpJPe4O9WIaoTJh='
assert len(ct)==44 and len(base64.b64decode(ct))==32
assert len(b'RBH{')==4 and base64.b64encode(b'RBH')==b'UkJI'

db=sqlite3.connect(':memory:')
db.execute('CREATE TABLE m(id INTEGER PRIMARY KEY)')
db.executemany('INSERT INTO m VALUES (?)',[(i,) for i in (1,2,4,5,6)])
assert db.execute('INSERT INTO m DEFAULT VALUES').lastrowid==7
demo=load('lethe_demo',SOLVERS/'lethe/mechanism_demo.py')
demo.exercise(False);demo.exercise(True)

assert unicodedata.normalize('NFKC','Ｅ')=='E'
assert unicodedata.normalize('NFKC','Е')!='E'
assert unicodedata.normalize('NFKC','．．／.sealed/TR-0344')=='../.sealed/TR-0344'
assert unicodedata.normalize('NFKC','а')!='a'
lines=(SOLVERS/'honest-hashes/ciphertext.txt').read_text(encoding='utf-8').splitlines()
assert len(lines)==18 and all(len(line)==64 for line in lines)
canonical=lambda s:s.translate(str.maketrans('асе','ace'))
assert canonical(lines[0])==canonical(lines[11])==hashlib.sha256(b'123456').hexdigest()
bits=''.join({'a':'0','c':'0','e':'0','а':'1','с':'1','е':'1'}[c] for line in lines for c in line if c in 'aceасе')
assert len(bits)==240
decoded=bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))
assert decoded==b'RBH{n0t_3v3ry_a_1s_an_a}'+b'\0'*6

chunks,_=png((SOLVERS/'night-4018/night_4018.png').read_bytes())
import struct,zlib
width,height,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',chunks[0][1])
assert (width,height,depth,color,interlace)==(1672,741,8,2,0)
inflated=zlib.decompress(b''.join(v for k,v in chunks if k==b'IDAT'))
assert len(inflated)==941*(1+1672*3)==4720997

pyc=(SOLVERS/'the-keeper-of-salt-reach/logbook').read_bytes()
code=marshal.loads(pyc[16:])
t=next(x for x in code.co_consts if isinstance(x,types.CodeType) and x.co_name=='_t')
seed=int.from_bytes(hashlib.sha256(t.co_code).digest()[:4],'big')
assert seed==0x23ba3afa and seed^0x5a5a5a5a==0x79e060a0

cycles=load('vault_cycles',SOLVERS/'clockmakers-vault/solve_cycles.py')
binary=(SOLVERS/'clockmakers-vault/clockmakers_vault').read_bytes()
key=binary[0x2004:0x2008];target=binary[0x22c0:0x22e0]
raw=list(cycles.recover(target,key))
printable=[x for x in raw if all(32<=v<=126 for v in x)]
flags=[x for x in printable if x.startswith(b'RBH{') and x.endswith(b'}')]
assert len(raw)==65536 and len(printable)==6 and len(flags)==1
assert all(cycles.transform(flags[0],bytes(v^mask for v in key))==target for mask in range(256))
# Test the algebraic cancellation beyond a single recovered flag.
for x in (bytes(32),bytes(range(32)),bytes((i*37+19)&255 for i in range(32))):
    expected=cycles.transform(x,key)
    assert all(cycles.transform(x,bytes(v^mask for v in key))==expected for mask in range(256))

quiet=np.asarray(Image.open(SOLVERS/'the-quiet-hour/the_quiet_hour.png').convert('RGB'),dtype=np.float32)
diff=quiet[:,1:]-quiet[:,:-1]
lags=list(range(40,151))
for row,expected in [(20,[118]),(260,[96,85])]:
    values=[np.mean(diff[row,d:]*diff[row,:-d]) for d in lags]
    top=[lags[i] for i in np.argsort(values)[::-1][:len(expected)]]
    assert top==expected,(row,top)

print('Semantic checks: Base64 sizes, SQLite lifecycle, Unicode, hash carrier, PNG scanlines, bytecode seed, VM cycles/key invariance, stereogram periods: PASS')
