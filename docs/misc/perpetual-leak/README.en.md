# Perpetual Leak

[中文](README.zh-CN.md) · Mimic CTF 2026 · Misc · 300 points

| Category | Points | Input | Result |
|---|---:|---|---|
| Misc | 300 | PGN and ciphertext | Chess-coordinate bit packing and XOR |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-perpetual-leak)

A chessboard has 64 squares, which fits a 6-bit index exactly. This challenge lives entirely on that fact: each move contributes a start square and a destination square, twelve bits total, and the stream becomes a keystream.

## Do not treat the SAN text as the key

`chess_moves.txt` holds PGN movetext. The tempting shortcut is to hash or XOR the text itself, but the prompt says the secret was "played", not typed. The moves matter, not the string.

So parse the movetext into legal move objects with `python-chess` and read square indices. The library numbers a1=0, b1=1, … h8=63.

Each move contributes twelve bits, origin first:

```python
bits += f'{move.from_square:06b}{move.to_square:06b}'
```

## Bit alignment is the whole challenge

78 half-moves provide 936 bits; the 53-byte ciphertext needs only 424, and the remainder is unused. The bitstream is sliced MSB-first into bytes.

The error to avoid is how many bytes one move occupies:

```python
# Wrong: 16 bits per move, so the stream is misaligned from move one
key = b''.join(bytes([m.from_square, m.to_square]) for m in moves)
```

Origin and destination are 6 bits each, twelve bits together, **not two whole bytes**. Writing `bytes([...])` spends 16 bits per move and everything downstream disagrees.

Repeated positions are not excluded from the encoding. Only the first 424 keystream bits are consumed because the ciphertext is 53 bytes long; 36 half-moves already supply enough bits.

## Decryption

`P_i = C_i XOR K_i`:

```text
RBH{p3rp3tu4l_ch3ck_c4nt_h1d3_th3_k3y_1n_th3_squ4r3s}
```

## What the checks do and do not prove

`python-chess` replays the game and checks that each move is legal in its position. This checks the replay, not the authenticity of the score.

The XOR round trip, however, **cannot** validate the key: any key XORed twice returns the input, that is reflexivity, not evidence. Two findings support the model: the mapping from moves to square indices has a concrete basis, and all 53 decrypted bytes form readable flag text.

Cost grows linearly with the number of moves and the ciphertext length.

## A discovery check

XOR the first four ciphertext bytes with `RBH{`: the candidate key prefix is `31cd2419`. With a1=0, `e2e4` encodes `(12 << 6) | 28 = 0x31c`, `e7e5` gives `0xd24`, and `g1f3` gives `0x195`. Concatenating those 12-bit words starts `31c d24 195`, whose first four bytes are exactly `31 cd 24 19`. This connects the known prefix to the square-packing hypothesis.

## Reproduction

```powershell
python src/solvers/perpetual-leak/solve.py
```

[Complete solver](../../../src/solvers/perpetual-leak/solve.py). Requires `chess`.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
