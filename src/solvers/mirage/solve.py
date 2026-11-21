import base64
A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
s = 'VW2mfl6UNp2XYoGKO4K9dp9SdZ+RYpJPe4O9WIaoTJh='
# A four-character key is a hypothesis; the known three-byte RBH prefix
# fixes four Base64 symbols, independent of subsequent plaintext bytes.
k = [(A.index(x)-A.index(y))%64 for x,y in zip(s[:4], 'UkJI')]
t = ''.join('=' if c=='=' else A[(A.index(c)-k[i%4])%64] for i,c in enumerate(s))
p = base64.b64decode(t, validate=True)
assert ''.join('=' if c=='=' else A[(A.index(c)+k[i%4])%64] for i,c in enumerate(base64.b64encode(p).decode())) == s
print('key:', ''.join(A[x] for x in k))
print('Base64:', t)
print(p.decode())
