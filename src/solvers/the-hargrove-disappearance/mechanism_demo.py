import unicodedata as u
x='．．／.sealed/TR-0344'
y=u.normalize('NFKC',x.replace('../',''))
assert y=='../.sealed/TR-0344'
assert u.normalize('NFKC',x).replace('../','')=='.sealed/TR-0344'
print('Synthetic ordering demonstration:',y)
print('No filesystem traversal, database creation, or HTTP request was performed')
