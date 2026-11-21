# The Cave Keeps No Secrets, Only Order

[中文](README.zh-CN.md) · Mimic CTF 2026 · Crypto · 300 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Crypto | 300 | Challenge ciphertext | Custom alphabet, modular subtraction, rail fence |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-cave-keeps-no-secrets-only-order)

The prompt is a six-line poem. The first thing that jumps out is the first word of each line: Fire, All, Chained, A, Dawn, Every — `FACADE`. It is too conspicuous, conspicuous enough to look like the answer. It is not the flag; it is the raw material for the alphabet used one layer down. The real structure is three parameters, each supplied by a different clue, and missing any one of them stops the solve.

## FACADE is only raw material

`FACADE` repeats a letter: A appears twice. Deduplicating in order of first appearance gives `facde`. Appending the standard hex digits not yet used, `0123456789b`, produces a 16-character custom alphabet:

```text
facde0123456789b
```

This alphabet replaces the hexadecimal digit table: each ciphertext character maps by position onto `0123456789abcdef` rather than by its literal value.

## Three parameters, three clues

Three details in the prompt each decide one thing:

| Clue | Parameter it supplies |
|---|---|
| The longest word shared by every stanza, `illusion` | mirror-reversed to `noisulli`, used as the repeating modular-addition key |
| Exactly three stanzas | rail-fence depth = 3 |
| The six opening words | the custom hex alphabet |

Taking the mirror image of `illusion` is what the prompt means by "mirror", and it is not an arbitrary word: it is the only long word that appears in every stanza.

## Unwinding in reverse

The ciphertext:

```text
7f9d875d53768b47854b569988768e7890888b909a4b768a785d808253946e475c79475e949d7687
```

Unwinding runs in this order:

1. map the custom alphabet's j-th character to the standard table's j-th character
2. parse as hex into 40 bytes (the solver recomputes and prints this length rather than trusting a hand count)
3. subtract the repeating key `noisulli` byte by byte, modulo 256
4. restore the rail-fence order

Step 4 is where most attempts go wrong. The three rails are **not** the 40 bytes split into three equal parts, and this is not a rectangular column read. The correct procedure counts how many times each rail index occurs in the sequence `0,1,2,1,0,1,2,1,...`, slices the ciphertext into three runs of those lengths, then walks the index sequence to take characters back in order. The first and last rails generally differ in length from the middle one.

```text
RBH{th3_sh4d0w_n3v3r_l13s_th3_w4ll_d03s}
```

After modular subtraction, the rail-ordered text is split into lengths **10, 20, 10**. These lengths come from counting the 40 positions of the zigzag, not from equal division:

```text
rail 0: Rts03_s3l0
rail 1: B{h_hdwnvrl3_h_4ld3}
rail 2: H34_31tw_s
```

## Round-trip confirmation

Rebuild the ciphertext from the plaintext: collect by the three rails, add the repeating key back modulo 256, map through the custom hex alphabet, and compare character by character with the original.

The alphabet and the mirrored word are grounded in the prompt, but the specific combination of modular addition and rail fence is not a necessary reading of the story. The complete output and the round trip are what confirm it. Complexity is O(n).

## Reproduction

```powershell
python src/solvers/the-cave-keeps-no-secrets/solve.py
```

[Complete solver](../../../src/solvers/the-cave-keeps-no-secrets/solve.py), Python standard library only.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
