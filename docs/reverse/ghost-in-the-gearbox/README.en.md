# GHOST IN THE GEARBOX

[中文](README.zh-CN.md) · Mimic CTF 2026 · Reverse · 100 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Reverse | 100 | ELF | VM bytecode and XOR |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-ghost-in-the-gearbox)

`ghost_gearbox.elf` is a stripped x86-64 ELF. It does not compare the password directly; it hands it to a small VM, so the reverse-engineering target is the VM's instruction set rather than the comparison in `main`.

Everything here is static analysis. The ELF is never executed.

## Locating three things first

Static analysis gives several key locations:

| Location | Content |
|---|---|
| `0x1199` | `main` |
| `0x12d3–0x12ff` | interpreter |
| `0x22c0` | VM program, 114 bytes |
| `0x22a0` | output table, 27 bytes |

One trap when reading these: **virtual addresses are not file offsets**. The script converts through the ELF's `.rodata` start address instead of treating the address as an offset directly.

## Only five instructions

Each VM instruction is a two-byte pair `(op, arg)`, and both bytes are XORed with `0x5a` first. Decoded:

| Raw opcode | Decoded opcode | Meaning |
|---|---|---|
| `6d` | `37` | load a password byte |
| `f8` | `a2` | XOR |
| `06` | `5c` | addition modulo 256 |
| `cb` | `91` | equality check |
| `5a` | `00` | halt |

Every password position runs through four instructions; 14 groups plus a terminator come to exactly 114 bytes, matching the VM program length. That number is itself a check: misaligned instruction grouping does not produce such a clean length.

## Inverting one byte

Write one group's parameters as X, A, and C. Execution is:

```text
((p[i] XOR X) + A) mod 256 = C
```

Solve backwards:

```text
p[i] = ((C - A) mod 256) XOR X
```

The XOR and addition are invertible; load chooses the byte and comparison supplies the target, so no search is needed. The script validates the opcode ordering and indices, reads the parameters from the attachment, and recovers:

```text
gh0st_1n_g34rs
```

The length is 14. Count the bytes carefully: `g34rs` mixes digits and letters, and an off-by-one error breaks every downstream step.

## Decrypting the output table

The 27-byte output table is XORed with `password[i mod 14]`:

```text
RBH{th3_g34rbox_n3v3r_l13s}
```

The script substitutes each recovered byte back into the VM constraints as a check. The addresses and opcodes here belong to this particular attachment; a different build would not match.

## Worked first group

The decoded bytes are `37 00 a2 1f 5c 8f 91 07`: load byte 0, XOR `1f`, add `8f`, compare with `07`. Thus `((0x07 - 0x8f) & 255) ^ 0x1f = 0x67`, the letter `g`.

## Reproduction

```powershell
python src/solvers/ghost-in-the-gearbox/solve.py
```

[Complete solver](../../../src/solvers/ghost-in-the-gearbox/solve.py). Requires pyelftools.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
