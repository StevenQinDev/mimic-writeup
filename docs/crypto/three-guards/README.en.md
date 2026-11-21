# Three Guards

[中文](README.zh-CN.md) · Mimic CTF 2026 · Crypto · 300 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Crypto | 300 | Ciphertext and LFSR parameters | LFSR correlation analysis |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-three-guards)

Three LFSRs at 17, 19, and 18 bits hold 54 bits of state between them. Brute-forcing 2^54 is out of the question. But the output is `z = a if b else c`: the selector ties the two outer registers to z, which makes the problem separable. Correlation pins Guard 1 and Guard 3 first; those results then invert Guard 2.

## Turning the hint into an alphabet

The hint is `names first`. Take all letters of `THREEGUARDS` (the title without its space) and deduplicate in order of first appearance:

```text
THREE GUARDS → THREGUADS
```

Append the remaining standard Base64 characters in their original order to complete a 64-character alphabet:

```text
THREGUADSBCFIJKLMNOPQVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Decoding with this table in place of the standard one yields 67 bytes.

The known plaintext prefix is `The King's decree: the vault code is RBH{`, 41 bytes. XOR it with the ciphertext and split MSB-first into 328 bits — that is the keystream to match against.

For example, Guard 1 emits `seed & 1`, computes feedback from bits 0 and 3, then shifts right and inserts feedback at bit 16. Starting with seed 1 emits 1 and produces next state 65536. This states the direction and output timing explicitly; reversing either changes the keystream.

## Why correlation is enough

If the three outputs are roughly balanced and independent, an outer register is selected about half the time; when it is not selected, it coincidentally equals z about half the time. Together that gives a match rate near 3/4 for the outer rails against z.

This is a **statistical motivation, not a guarantee about these particular 328 bits**. Real sequences deviate, so match counts can rank candidates but cannot settle them.

Guard 1 is 17 bits with taps 0/3; Guard 3 is 18 bits with taps 0/7. Enumerate each register's non-zero seeds (2^17 − 1 and 2^18 − 1 candidates) and rank by matching bits against the known stream:

| Register | Best seed | Matching bits |
|---|---|---|
| Guard 1 | 64988 | 245 / 328 |
| Guard 3 | 214757 | 254 / 328 |

The implementation does not shift bit by bit. It precomputes the GF(2) basis-vector sequence, then walks it with Gray code so each step XORs exactly one basis vector, measuring distance with integer `bit_count()`. That brings 2^17 + 2^18 attempts down to a few seconds.

## Inverting the selector with a mask

Let `mask = a XOR c`. Where mask is 1, a and c differ, so z is decided by b. Where mask is 0, a and c agree, so z must equal that shared value. Hence:

```text
(b AND mask) == ((z XOR c) AND mask)
```

This constrains b bit by bit. The 328 bits yield 157 effective constraints, and among Guard 2's 2^19 − 1 non-zero seeds only one satisfies all of them: `478853`.

The seed triple, in register order:

```text
(64988, 478853, 214757)
```

```text
RBH{tw0_gu4rds_t0ld_th3_truth}
```

## A full-length check is not optional

Correlation only filters; it produces candidates, not conclusions. The real test feeds the seeds back into a register implementation, decrypts the entire plaintext, re-encrypts, and re-encodes through the custom alphabet. The result must match all 92 characters, padding included.

The full round trip is the deciding test. Correlation narrows the search; it cannot establish the result on its own.

The search drops from 2^54 to 2^17 + 2^18 + 2^19, all of it integer work on a fixed 328-bit window.

## Reproduction

```powershell
python src/solvers/three-guards/solve.py
```

[Complete solver](../../../src/solvers/three-guards/solve.py), Python standard library only.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
