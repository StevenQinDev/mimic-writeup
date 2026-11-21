import unicodedata as u
name='Ｅ'
assert name.lower() not in {'e'}
assert u.normalize('NFKC',name)=='E'
assert u.normalize('NFKC','Е')!='E'
print('Synthetic normalization demonstration: fullwidth E matches; Cyrillic E does not')
