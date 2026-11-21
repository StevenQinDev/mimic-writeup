from pathlib import Path
s = Path(__file__).with_name('ciphertext.txt').read_text(encoding='utf-8')
mapping = {
    'a': '0', 'c': '0', 'e': '0',
    '\u0430': '1', '\u0441': '1', '\u0435': '1',
}
# Cyrillic a/e/es are distinct code points, not normalized Latin letters.
bits = ''.join(mapping[c] for c in s if c in mapping)
assert len(bits)%8 == 0
p = bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))
print('selected bits:', len(bits), 'raw bytes:', repr(p))
print(p.rstrip(b'\0').decode('ascii'))
