"""Model the vault VM and solve its 32-byte check with Z3."""
import sys
from pathlib import Path
if len(sys.argv)>1:
    binary=Path(sys.argv[1])
else:
    binary=Path(__file__).with_name("clockmakers_vault")
b=binary.read_bytes()
def rol(v,n):
    n &= 7
    return ((v<<n)|(v>>((8-n)&7)))&255

def vm(x):
    mem=list(x)+[0]*224
    mem[96:128]=b[0x22c0:0x22e0]
    mem[128:132]=b[0x2004:0x2008]
    r=[0]*8; pc=0; mismatch=0
    for step in range(10000):
        op,a,c,_=b[0x21e0+4*pc:0x21e4+4*pc]
        op ^= (pc*0x35+17)&255
        pc+=1; a &= 7
        if op==0x9f:r[a]=c
        elif op==0xed:r[a]=r[c&7]
        elif op==0x93:r[a]&=r[c&7]
        elif op==0xbc:r[a]=(r[a]+c)&255
        elif op==0x89:r[a]=mem[r[c&7]]
        elif op==0x5e:r[a]^=r[c&7]
        elif op==0x2b:r[a]=rol(r[a],r[c&7])
        elif op==0xc7:r[a]=rol(r[a],c)
        elif op==0xb6:mem[r[a]]=r[c&7]
        elif op==0xd4:r[a]=(r[a]+1)&255
        elif op==0x56:
            if r[a]:pc+=c if c<128 else c-256
        elif op==0x63:mismatch |= int(r[a]!=r[c&7])
        elif op==0xa3:return mismatch==0,step+1
        else:raise ValueError(hex(op))
    raise RuntimeError("step limit")
# Recover rather than merely check the known candidate.
import z3
v=[z3.BitVec("v%d"%i,8) for i in range(32)]
k=b[0x2004:0x2008]
y=[z3.RotateLeft(v[i]^k[i&3],i)^v[(i+7)&31] for i in range(32)]
s=z3.Solver()
s.add(*[y[i]^z3.RotateLeft(y[(i+13)&31],3)==b[0x22c0+i] for i in range(32)])
s.add(*[z3.And(c>=32,c<=126) for c in v])
s.add(*[v[i]==c for i,c in enumerate(b"RBH{")],v[-1]==125)
assert s.check()==z3.sat
m=s.model();answer=bytes(m.eval(c).as_long() for c in v)
assert vm(answer)[0]
assert not vm(bytes([answer[0]^1])+answer[1:])[0]
print("Recovered bytes:", repr(answer))
print("Flag:", answer.rstrip(b"\x00").decode())
print("VM accepted; altered input rejected; steps:", vm(answer)[1])
s.add(z3.Or(*[c!=m.eval(c) for c in v]))
assert s.check()==z3.unsat
print("Unique printable RBH flag confirmed")
