"""Static Python 3.12 pyc recovery. Never exec/eval the challenge code."""
import hashlib, marshal, types
from pathlib import Path
d = Path(__file__).with_name('logbook').read_bytes()
assert d[:4] == bytes.fromhex('cb0d0d0a'), 'Expected challenge Python 3.12 magic'
code = marshal.loads(d[16:])
q = next(x for x in code.co_consts if isinstance(x,str) and len(x)==560)
t = next(x for x in code.co_consts if isinstance(x,types.CodeType) and x.co_name=='_t')
seed = int.from_bytes(hashlib.sha256(t.co_code).digest()[:4], 'big')
enc = bytes.fromhex(q)
mapping = {60:0,161:1,87:2,233:3}
def rol(x,n):
    n &= 7
    return ((x<<n)|(x>>((8-n)&7)))&255
def apply(x,op,k):
    return [(x+k)&255, x^k, rol(x,k), (x*(k|1))&255][mapping[op]]
answer = bytearray()
for i in range(35):
    mask = hashlib.sha256(seed.to_bytes(4,'big')+bytes([i])).digest()[:8]
    block = bytes(a^b for a,b in zip(enc[8*i:8*i+8],mask))
    assert (sum(block[:7])*31+7)&255 == block[7]
    candidates = []
    for x in range(256):
        v = x
        for j in (0,2,4):
            v = apply(v,block[j],block[j+1])
        if v == block[6]: candidates.append(x)
    assert len(candidates)==1
    answer.append(candidates[0])
    seed = (seed*131+block[6]*257+i+1)&0xffffffff
print('35 checksums passed; unique byte at each position')
print(answer.decode())
