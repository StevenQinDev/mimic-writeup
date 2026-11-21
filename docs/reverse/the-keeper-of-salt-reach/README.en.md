# The Keeper of Salt Reach

[中文](README.zh-CN.md) · Mimic CTF 2026 · Reverse · 300 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Reverse | 300 | Python 3.12 bytecode | Per-byte constraints |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-keeper-of-salt-reach)

The attachment is an extensionless file named `logbook` whose identification by `file` depends on its magic database. It is Python 3.12 bytecode — the first four bytes `cb 0d 0d 0a` are the pyc magic.

Handle it statically: skip the 16-byte pyc header, parse the code object with `marshal`, and read only the constants. Do not execute or import the challenge module. The interpreter version must match; use Python 3.12 for this code-object layout and bytecode interpretation.

## Everything lives in the constants

Two things matter among the constants:

- `Q`: 560 hex characters, that is 280 bytes
- `N = 35`

The seed is not supplied externally either. Hash the raw `co_code` of the nested function `_t` with SHA-256 and read the first four bytes big-endian as a 32-bit initial seed. **The seed comes from the bytecode itself**, which is why a different build will not open.

The disassembled `gettrace` branch changes the seed by XOR `0x5a5a5a5a` when tracing is active. The ordinary seed is `0x23ba3afa`; the tracing variant is `0x79e060a0`. Static parsing uses the ordinary seed without executing that branch.

## Group structure

The key for group i:

```text
SHA256(seed_be32 || byte(i))[:8]
```

Each group is eight bytes. After XOR decryption a fixed rule verifies it:

```text
(sum(block[:7]) * 31 + 7) & 255 == block[7]
```

Within the first seven bytes, bytes 0..5 hold three opcode/argument pairs, byte 6 holds the target, and byte 7 holds the checksum (zero-based offsets).

## Every byte is constrained into place

Four raw opcodes appear:

| Opcode | Operation |
|---|---|
| 60 | addition modulo 256 |
| 161 | XOR |
| 87 | rotate left |
| 233 | multiply by `(k \| 1)` |

That mapping comes from bytecode analysis, not from reverse-engineering the target string. Analytical inversion is also valid: reverse the operation order, subtract additions, XOR again, rotate right, and multiply by the odd factor's modular inverse.

Enumerate 0 to 255 per group, apply the three operations, and compare against the target. Exactly **one** candidate survives per group, and there is a structural reason: addition, XOR, and rotation are bijections, and multiplication by an odd number modulo 256 is invertible, so their composition maps each target to exactly one input byte.

After each group the seed updates:

```text
seed = (seed * 131 + block[6] * 257 + i + 1) mod 2^32
```

The order matters: the update uses the **decrypted target byte**, not the raw ciphertext byte. Solving every group independently from the initial seed desynchronises from group two onward.

```text
RBH{th3_l1ght_w4s_n3v3r_l1t_4t_4ll}
```

## Verification

All 35 check bytes pass and all 35 byte candidates are unique. The enumeration costs roughly 35 × 256 × 3 operations — the original `_v()` never has to run.

The file also carries strings that look like hints. They are decoys and take no part in any computation.

## Reproduction

```powershell
python src/solvers/the-keeper-of-salt-reach/solve.py
```

[Complete solver](../../../src/solvers/the-keeper-of-salt-reach/solve.py), Python standard library only.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
