"""Recover both dependency cycles with the standard library; never execute the ELF."""
from pathlib import Path


def rol(v, n):
    n &= 7
    return ((v << n) | (v >> ((8-n) & 7))) & 255


def transform(x, key):
    y = [rol(x[i] ^ key[i & 3], i) ^ x[(i+7) & 31] for i in range(32)]
    return bytes(y[i] ^ rol(y[(i+13) & 31], 3) for i in range(32))


def recover(target, key):
    for first_y in range(256):
        y = [0] * 32
        y[0] = first_y
        i = 0
        for _ in range(31):
            j = (i+13) & 31
            y[j] = rol(y[i] ^ target[i], 5)  # ror8(..., 3)
            i = j
        if y[i] ^ rol(y[0], 3) != target[i]:
            continue
        for first_x in range(256):
            x = [0] * 32
            x[0] = first_x
            i = 0
            for _ in range(31):
                j = (i+7) & 31
                x[j] = y[i] ^ rol(x[i] ^ key[i & 3], i)
                i = j
            if y[i] == rol(x[i] ^ key[i & 3], i) ^ x[0]:
                yield bytes(x)


def main():
    binary = Path(__file__).with_name('clockmakers_vault').read_bytes()
    target, key = binary[0x22c0:0x22e0], binary[0x2004:0x2008]
    solutions = list(recover(target, key))
    printable = [x for x in solutions if all(32 <= c <= 126 for c in x)]
    flags = [x for x in printable if x.startswith(b'RBH{') and x.endswith(b'}')]
    assert len(solutions) == 65536 and len(printable) == 6 and len(flags) == 1
    answer = flags[0]
    assert all(transform(answer, bytes(k ^ mask for k in key)) == target for mask in range(256))
    assert transform(bytes([answer[0] ^ 1]) + answer[1:], key) != target
    print('Raw solutions:', len(solutions), '; printable:', len(printable), '; RBH flags:', len(flags))
    print('Flag:', answer.decode())
    print('All 256 uniform key XOR masks preserve the target; altered input rejected')


if __name__ == '__main__':
    main()
