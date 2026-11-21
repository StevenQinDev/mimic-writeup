# Honest Hashes

[中文](README.zh-CN.md) · Mimic CTF 2026 · Misc · 100 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Misc | 100 | ciphertext.txt | Unicode homoglyph bitstream |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-honest-hashes)

The attachment is 18 long strings that look exactly like SHA-256 digests. The title says "honest hashes" — the hashes are not lying, and the secret is not inside them. It is in the code points of the characters.

Lines 1 and 12 become the same digest after explicitly mapping Cyrillic `а/с/е` to Latin `a/c/e`. That digest is SHA-256 of `123456`; the differing code points carry information independently of the visible hash.

The difference is in Unicode: Latin lowercase `a`, `c`, `e` are U+0061 / U+0063 / U+0065; Cyrillic `а`, `с`, `е` are U+0430 / U+0441 / U+0435. They render almost identically and occupy different code points.

The first six sampled characters on line 1 are `e е e с a c`, with code points `U+0065 U+0435 U+0065 U+0441 U+0061 U+0063`. They encode `010100`. The explicit lookalike map reduces lines 1 and 12 to:

```text
8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
```

## Each letter is one bit

These three letters come in two forms each, which makes a binary channel:

- Latin form records 0
- Cyrillic form records 1

Other characters — digits and remaining letters — are not sampled. Walk the file in order and turn every hit into one bit:

```python
mapping = {'a':'0','c':'0','e':'0','а':'1','с':'1','е':'1'}
bits = ''.join(mapping[c] for c in text if c in mapping)
```

That gives 240 bits. Grouped MSB-first into bytes, it becomes 30 bytes: a 24-byte flag plus 6 zero bytes.

```text
RBH{n0t_3v3ry_a_1s_an_a}
```

The flag states the trick: not every a is an a.

## Two things not to get wrong

**Do not claim NFKC performs the conversion.** Unicode normalisation does not turn Cyrillic `а` into Latin `a`. This is an explicit mapping table, not normalisation. Getting the mechanism wrong undermines the conclusion.

**Do not overwrite the source text before analysing it.** Any replacement of the Cyrillic forms with Latin lookalikes destroys the hidden bits. Preserve the original UTF-8 bytes. The analysis has to run on the original bytes.

## Confirming the direction

Three things together count as evidence: 240 divides by 8, the decoded prefix is `RBH{`, and the full string is readable. Inverting 0 and 1, or switching to LSB-first, both produce noise.

The script prints the raw decoded bytes (padding included) and strips only trailing NULs. Complexity is O(n).

These strings look like ordinary SHA-256 digests, but recovering the message **requires cracking no hash at all**. The digest is only a carrier.

## Reproduction

```powershell
python src/solvers/honest-hashes/solve.py
```

[Complete solver](../../../src/solvers/honest-hashes/solve.py), Python standard library only.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
