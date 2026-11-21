# Mirage

[中文](README.zh-CN.md) · Mimic CTF 2026 · Crypto · 100 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Crypto | 100 | Challenge ciphertext | Base64 index subtraction |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-mirage)

The four-byte prefix is `RBH{`. Its first three bytes, `RBH`, have the fixed Base64 encoding `UkJI`. The ciphertext opens with `VW2m`. Two four-character strings line up, and the difference is the start of the key. That is a far better foothold than "it looks like Base64".

```text
VW2mfl6UNp2XYoGKO4K9dp9SdZ+RYpJPe4O9WIaoTJh=
```

## This is encryption over Base64, not Base64

The character set and the trailing `=` padding both point at Base64, but directly decoding the 44-character string yields 32 bytes that are not the expected flag. This motivates testing another layer.

The order matters: decode-then-decrypt and encrypt-then-encode give very different results. The known prefix suggests a testable model. `UkJI` is the Base64 of the plaintext, and it lands exactly where a four-character block should. In this model, encryption operates **on Base64 character indices**, and the output is still valid Base64 that happens to be transported as text.

## Four characters, one candidate key

The standard Base64 alphabet:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Model the layer as repeating addition, `C_i = (P_i + K_i) mod 64`, and evaluate the four known positions:

| Position | Ciphertext | C_i | Known character | P_i | (C_i − P_i) mod 64 | Key character |
|---|---|---:|---|---:|---:|---|
| 0 | V | 21 | U | 20 | 1 | B |
| 1 | W | 22 | k | 36 | 50 | y |
| 2 | 2 | 54 | J | 9 | 45 | t |
| 3 | m | 38 | I | 8 | 30 | e |

That gives `Byte`. The subtraction must use **alphabet indices**, not ASCII byte values; the two readings agree in a few places by coincidence and diverge quickly.

## Test a period-four candidate against the whole message

Treat `Byte` as a period-4 key, subtract it from every non-padding character modulo 64, and keep the `=`:

```text
UkJIezN2M3J5X2ZsNGdfc3Q0cnRzX3cxdGhfVWtKSX0=
```

Four known positions produce one candidate period. They **cannot prove** the period is 4: periods of 8 or 12 would also match the first four characters. The real test is whether the whole string decodes to readable text and whether re-encoding reproduces the ciphertext exactly:

```text
RBH{3v3ry_fl4g_st4rts_w1th_UkJI}
```

The flag says it outright: every flag starts with `UkJI`.

The solver re-encodes the plaintext, adds the repeating key back, and asserts the result equals the original ciphertext. Runtime and space are both O(n).

## Reproduction

Python standard library only:

```powershell
python src/solvers/mirage/solve.py
```

[Complete solver](../../../src/solvers/mirage/solve.py)

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
