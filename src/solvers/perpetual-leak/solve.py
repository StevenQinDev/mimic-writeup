#!/usr/bin/env python3
"""Recover the XOR key from the complete chess move stream.

Each move contributes its origin and destination square indices as two
6-bit values. Concatenate the values, pack them MSB first, and XOR the
result with intercepted.txt. Encoding each square as a full byte would
produce an incorrectly aligned keystream.
"""
import sys
import pathlib

import chess
import chess.pgn

CHESS = pathlib.Path(__file__).with_name("chess_moves.txt")
WIRE = pathlib.Path(__file__).with_name("intercepted.txt")


def keystream(game: chess.pgn.Game, n: int) -> bytes:
    bits = []
    board = game.board()
    for move in game.mainline_moves():
        bits.append(f"{move.from_square:06b}")
        bits.append(f"{move.to_square:06b}")
        board.push(move)
    blob = "".join(bits)
    return bytes(int(blob[i:i + 8], 2) for i in range(0, len(blob) - 7, 8))[:n]


def main() -> int:
    game = chess.pgn.read_game(CHESS.open(encoding="utf-8"))
    assert game is not None and not game.errors, "Invalid PGN"
    ct = bytes.fromhex(WIRE.read_text(encoding="utf-8").strip())
    ks = keystream(game, len(ct))
    assert len(ks) == len(ct), "Insufficient move bits"
    pt = bytes(a ^ b for a, b in zip(ct, ks))
    print(f"ciphertext : {len(ct)} bytes")
    print(f"plaintext  : {pt!r}")
    print(f"flag       : {pt.decode()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
