"""Recover the Three Guards register seeds from the known plaintext."""

import base64
import re
import string


ENCODED = (
    "c1oToD5pgTjnkVWjQr4ZflOD+h4KueNOl+qXRiBe7B27fbxyveiiDqFkWBsf7dEk"
    "7MubeIBMA5oJg/IpamGTKAE+UM=="
)
KNOWN = b"The King's decree: the vault code is RBH{"
STANDARD = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
ALPHABET = "".join(dict.fromkeys(c for c in "THREE GUARDS" + STANDARD if c in STANDARD))
REGISTERS = ((17, (0, 3)), (19, (0, 1, 2, 5)), (18, (0, 7)))


def stream(seed, width, taps, length):
    """Pack chronological output bits into the low-to-high bits of an integer."""
    result = 0
    for t in range(length):
        result |= (seed & 1) << t
        feedback = 0
        for tap in taps:
            feedback ^= (seed >> tap) & 1
        seed = (seed >> 1) | (feedback << (width - 1))
    return result


def pack_bits(data):
    return sum(
        ((byte >> (7 - bit)) & 1) << (8 * i + bit)
        for i, byte in enumerate(data)
        for bit in range(8)
    )


def best_correlation(width, taps, target, length):
    # Linearity gives the stream for any seed by XORing its basis streams.
    # Consecutive Gray-code seeds differ in one bit, so enumeration is cheap.
    basis = [stream(1 << bit, width, taps, length) for bit in range(width)]
    sequence = 0
    best = (-1, 0, 0)
    for i in range(1, 1 << width):
        sequence ^= basis[(i & -i).bit_length() - 1]
        score = length - (sequence ^ target).bit_count()
        if score > best[0]:
            best = (score, i ^ (i >> 1), sequence)
    return best


def recover_selector(target, first, third, length):
    mask = first ^ third
    if (target ^ first) & ~mask:
        raise ValueError("Outer-register candidates contradict the known plaintext")
    wanted = (target ^ third) & mask
    width, taps = REGISTERS[1]
    basis = [stream(1 << bit, width, taps, length) & mask for bit in range(width)]
    sequence = 0
    candidates = []
    for i in range(1, 1 << width):
        sequence ^= basis[(i & -i).bit_length() - 1]
        if sequence == wanted:
            candidates.append(i ^ (i >> 1))
    if len(candidates) != 1:
        raise ValueError(f"Expected one selector seed, found {len(candidates)}")
    return candidates[0], mask.bit_count()


def scalar_keystream(seeds, byte_count):
    """Independent, step-by-step implementation for final verification."""
    states = list(seeds)
    result = bytearray()
    for _ in range(byte_count):
        byte = 0
        for _ in range(8):
            outputs = [state & 1 for state in states]
            byte = (byte << 1) | (outputs[0] if outputs[1] else outputs[2])
            for i, (width, taps) in enumerate(REGISTERS):
                feedback = 0
                for tap in taps:
                    feedback ^= (states[i] >> tap) & 1
                states[i] = (states[i] >> 1) | (feedback << (width - 1))
        result.append(byte)
    return bytes(result)


def main():
    ciphertext = base64.b64decode(ENCODED.translate(str.maketrans(ALPHABET, STANDARD)), validate=True)
    length = 8 * len(KNOWN)
    target = pack_bits(bytes(a ^ b for a, b in zip(ciphertext, KNOWN)))
    first = best_correlation(*REGISTERS[0], target, length)
    third = best_correlation(*REGISTERS[2], target, length)
    middle, constraints = recover_selector(target, first[2], third[2], length)
    seeds = (first[1], middle, third[1])
    key = scalar_keystream(seeds, len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
    if not plaintext.startswith(KNOWN):
        raise ValueError("Independent scalar decryption failed the known prefix")
    flag = re.search(rb"RBH\{[ -~]+?\}", plaintext)
    if flag is None:
        raise ValueError("No flag in the recovered plaintext")
    rebuilt = base64.b64encode(bytes(a ^ b for a, b in zip(plaintext, key))).decode()
    rebuilt = rebuilt.translate(str.maketrans(STANDARD, ALPHABET))
    if rebuilt != ENCODED:
        raise ValueError("Full ciphertext re-encoding did not match")
    print("Alphabet:", ALPHABET)
    print(f"Correlations: guard 1 = {first[0]}/{length}; guard 3 = {third[0]}/{length}")
    print("Selector constraints:", constraints, "(exactly one nonzero seed)")
    print("Seeds:", *seeds)
    print("Plaintext:", plaintext.decode("ascii"))
    print("Flag:", flag.group().decode("ascii"))
    print("Independent scalar decryption: PASS")
    print("Exact full ciphertext re-encoding: PASS")


if __name__ == "__main__":
    main()
