s = '7f9d875d53768b47854b569988768e7890888b909a4b768a785d808253946e475c79475e949d7687'
standard = '0123456789abcdef'
alphabet = ''.join(dict.fromkeys('facade'+standard))
c = bytes.fromhex(s.translate(str.maketrans(alphabet, standard)))
k = b'noisulli'
railtext = bytes((x-k[i%len(k)])%256 for i,x in enumerate(c))
pattern = [0,1,2,1]
rails = [pattern[i%4] for i in range(len(c))]
pos = 0
buckets = []
for r in range(3):
    n = rails.count(r)
    buckets.append(iter(railtext[pos:pos+n]))
    pos += n
p = bytes(next(buckets[r]) for r in rails)
encoded = bytes(p[i] for r in range(3) for i in range(len(p)) if rails[i]==r)
encoded = bytes((x+k[i%len(k)])%256 for i,x in enumerate(encoded))
assert encoded.hex().translate(str.maketrans(standard,alphabet)) == s
print('ciphertext bytes:', len(c), 'alphabet:', alphabet)
print(p.decode())
