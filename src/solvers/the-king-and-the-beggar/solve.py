import base64
s = "ytq0mge1mZa0ndG2ndbMntm0ody0ngu0mZaZndq0odyWntK1nJbMntm0nZa5nwm0zJC1nZu2"
h = base64.b64decode(s.swapcase(), validate=True).decode('ascii')
c = bytes.fromhex(h[::-1])
keys = {a ^ b for a,b in zip(c, b'RBH{')}
assert len(keys) == 1
k = keys.pop()
p = bytes(x ^ k for x in c)
assert base64.b64encode(bytes(x ^ k for x in p).hex()[::-1].encode()).decode().swapcase() == s
print('hex text:', h)
print('key:', hex(k))
print(p.decode())
