# The Clockmaker’s Vault

[中文](README.zh-CN.md) · Mimic CTF 2026 · Reverse · 300 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Reverse | 300 | ELF | VM constraints and Z3 |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-clockmaker-s-vault)


The executable implements a 53-instruction VM with eight byte registers and 256 bytes of memory. Static decoding reduces its check to two rounds of rotations and XORs. We solve those equations in two independent ways: Z3 and an exhaustive walk of two short dependency cycles.

## Recover the instruction and memory layout

The dispatcher is at virtual address `0x1210`. For this attachment, the program occupies 53 four-byte records `(op,a,c,pad)` at file offset `0x21e0`. Decode the opcode at instruction index `pc` before dispatch:

```python
op ^= (pc * 0x35 + 0x11) & 255
```

Input bytes occupy memory `0..31`, the target occupies `96..127`, and four key bytes occupy `128..131`. The target is stored at file offset `0x22c0`; the key at `0x2004` is `a5 dc 13 4a`. File offsets and virtual addresses are different concepts even when some values coincide in this ELF.

## Flatten the check

For indices modulo 32 and byte rotations modulo eight:

```text
y[i] = rol8(x[i] XOR key[i & 3], i) XOR x[(i + 7) & 31]
target[i] = y[i] XOR rol8(y[(i + 13) & 31], 3)
```

The dependencies prevent solving an isolated byte without an assumption. They do not prevent inversion: guessing a single byte lets us traverse an entire cycle.

## Method one: byte-vector constraints

The [Z3 solver](../../../src/solvers/clockmakers-vault/solve.py) creates 32 eight-bit vectors, adds both equations, and restricts the result to printable ASCII with prefix `RBH{` and final `}`. Fixed-width vector operations preserve the VM's byte semantics. The recovered input is:

```text
RBH{cl0ckmaker_hid_a_vm_in_here}
```

An independent instruction-level simulator checks the recovered bytes against the decoded VM. Its signed jumps are relative to the already incremented instruction counter. The answer is accepted in 1510 steps; flipping its first byte is rejected. A blocking clause makes Z3 return unsatisfiable for another answer **under those printable flag constraints**.

## Method two: walk the cycles with no SMT dependency

Rearrange round two:

```text
y[(i+13)&31] = ror8(y[i] XOR target[i], 3)
```

Guess `y[0]` in `0..255`. Since `gcd(13,32)=1`, stepping by 13 visits every index before returning to zero. Propagate 31 steps and check the closing equation. Then guess `x[0]` and rearrange round one:

```text
x[(i+7)&31] = y[i] XOR rol8(x[i] XOR key[i&3], i)
```

Since `gcd(7,32)=1`, this also visits every index. Again check cycle closure. The [standard-library solver](../../../src/solvers/clockmakers-vault/solve_cycles.py) independently enumerates **65,536 raw solutions, six fully printable solutions, and one printable `RBH{...}` flag**. These counts show why an unconstrained uniqueness claim would be wrong. The work is at most 256 × 256 × 32 byte steps after recovering the intermediate cycles.

## Why the apparent anti-debug key change cancels

The `ptrace` failure branch XORs each of the four key bytes with `0x5a`. For any common XOR mask `c`, round one gains `rol8(c,i)`. Round two therefore gains:

```text
rol8(c,i) XOR rol8(c,i+13+3) = 0
```

The two rotation amounts differ by 16, a multiple of eight. Thus the final transform is invariant under this uniform key change. The cycle solver checks all 256 possible uniform masks against the recovered input and target. This is a property of these equations, not a general reason to disregard anti-debug branches.

## Reproduction

```powershell
python src/solvers/clockmakers-vault/solve.py
python src/solvers/clockmakers-vault/solve_cycles.py
```

The first command needs `z3-solver`; the second uses only the standard library. Both parse the original ELF as bytes. The executable itself is not run.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
