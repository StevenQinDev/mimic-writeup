# The King and the Beggar

[中文](README.zh-CN.md) · Mimic CTF 2026 · Crypto · 100 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Crypto | 100 | 72-character ciphertext | Case swap, Base64, XOR |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-king-and-the-beggar)

The first step is misleading: all 72 characters sit inside the Base64 alphabet, so a direct `b64decode` succeeds. Being decodable proves nothing. The useful signal is what comes out.

```text
ytq0mge1mZa0ndG2ndbMntm0ody0ngu0mZaZndq0odyWntK1nJbMntm0nZa5nwm0zJC1nZu2
```

## Two layers of "high and low"

The prompt tells the story of a king and a beggar trading places and keeps repeating the idea of exchanging high and low. That phrase maps onto two different levels:

- characters: swap letter case (`swapcase`)
- data: swap the two nibbles inside each byte

Start with the first level only. Swapping case and Base64-decoding yields 54 hexadecimal characters:

```text
a440a530448640f5348644e430344486059560f5347095c4f75756
```

Not readable text, but 54 is even, which is 27 bytes. That is not a coincidence.

The second layer asks whether to swap nibbles and whether to reverse order. Write two adjacent bytes as `ab cd`, each letter being one nibble. Swapping nibbles gives `ba dc`; reversing the byte order afterwards gives `dc ba`. Reversing the hexadecimal **string** `abcd` gives `dcba` directly — the same result. So one line does both:

```python
h = base64.b64decode(s.swapcase(), validate=True).decode('ascii')
c = bytes.fromhex(h[::-1])
```

The `[::-1]` must apply to the hexadecimal text, not to the output of `bytes.fromhex()`. Reversing the parsed bytes only reverses byte order and leaves the nibbles alone.

## 0x37 is derived, not guessed

After the transformation the first four bytes are `65 75 7f 4c`. Assume the last layer is a repeating single-byte XOR. The flag prefix is known to be `RBH{`, so compute one candidate per position:

| Position | Current byte | Known plaintext byte | XOR |
|---|---|---|---|
| 0 | `65` | `52` (R) | `37` |
| 1 | `75` | `42` (B) | `37` |
| 2 | `7f` | `48` (H) | `37` |
| 3 | `4c` | `7b` ({) | `37` |

All four positions yield the same value, supporting the repeating one-byte XOR model. The script asserts that the candidate set has exactly one element instead of hard-coding `0x37`:

```python
keys = {a ^ b for a, b in zip(c, b'RBH{')}
assert len(keys) == 1
k = keys.pop()
p = bytes(x ^ k for x in c)
```

```text
RBH{n0th1ng_st4ys_th3_s4m3}
```

The four positions support a constant key at those positions. A longer key could share that prefix, so this does not prove that every later key byte is identical. The full output and round trip check the proposed model for consistency.

## Check the complete transform

XOR is self-inverse, so the whole chain can be walked backwards: plaintext XOR key → hex text → reverse → Base64 encode → swap case. The result must match the original 72 characters exactly.

```python
assert base64.b64encode(
    bytes(x ^ k for x in p).hex()[::-1].encode()
).decode().swapcase() == s
```

This pins down direction, order, and input integrity at once. Flip any single step and the string diverges.

## Reproduction

Run from the repository root using only Python's standard library:

```powershell
python src/solvers/the-king-and-the-beggar/solve.py
```

The [solver](../../../src/solvers/the-king-and-the-beggar/solve.py) embeds the prompt input and needs neither the network nor a particular working directory. Expected output includes the hexadecimal text above, `key: 0x37`, and the flag. Running with `python -O` disables the assertions.

## Notes and credit

- Use the complete challenge data; changing even one character changes the result.
- The key `0x37` comes from the known `RBH{` prefix and is confirmed by a full reverse transform.
- The presentation of the constant derivation takes cues from [DebajyotiRay's Mimic writeup](https://github.com/DebajyotiRay/mimic-ctf-writeup).

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
