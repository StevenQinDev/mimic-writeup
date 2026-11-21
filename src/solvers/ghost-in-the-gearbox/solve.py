from elftools.elf.elffile import ELFFile

from pathlib import Path
BIN = Path(__file__).with_name("ghost_gearbox.elf")

# .text 0x12d3-0x12ff implements a tiny VM over a 114-byte instruction stream at
# .rodata 0x22c0.  Instructions are (op, arg) with both bytes xored by 0x5a:
#   0x6d (=> 0x37)  load  acc = password[arg^0x5a]
#   0xf8 (=> 0xa2)  xor   acc ^= arg^0x5a
#   0x06 (=> 0x5c)  add   acc += arg^0x5a
#   0xcb (=> 0x91)  check acc == arg^0x5a
#   0x5a (=> 0x00)  success
# The success path (0x1323) prints flag[i] = table[0x22a0 + i] ^ password[i % 14]
# for 27 bytes, then a newline.
VM_VADDR = 0x22C0
VM_LEN = 0x72
FLAG_VADDR = 0x22A0
FLAG_LEN = 27
PW_LEN = 14


def read_rodata(path):
    with open(path, "rb") as f:
        elf = ELFFile(f)
        sec = elf.get_section_by_name(".rodata")
        return sec["sh_addr"], sec.data()


def main():
    base, rodata = read_rodata(BIN)

    def at(vaddr, n):
        return rodata[vaddr - base:vaddr - base + n]

    program = at(VM_VADDR, VM_LEN)
    flag_tbl = at(FLAG_VADDR, FLAG_LEN)

    acc = 0
    pw = bytearray()
    i = 0
    while True:
        op = program[i]
        arg = program[i + 1]
        if op == 0x5A:
            break
        if op == 0x6D:
            idx = arg ^ 0x5A
            if idx != len(pw):
                raise SystemExit("unexpected load index %d at %d" % (idx, i))
            # look ahead: xor, add, check
            ops = [program[i + 2 + 2 * k] for k in range(3)]
            args = [program[i + 3 + 2 * k] for k in range(3)]
            if ops != [0xF8, 0x06, 0xCB]:
                raise SystemExit("unexpected op sequence %s" % ops)
            x = args[0] ^ 0x5A
            a = args[1] ^ 0x5A
            c = args[2] ^ 0x5A
            ch = ((c - a) & 0xFF) ^ x
            pw.append(ch)
            acc = ch
            i += 8
            continue
        if op == 0xF8:
            acc ^= arg ^ 0x5A
        elif op == 0x06:
            acc = (acc + (arg ^ 0x5A)) & 0xFF
        elif op == 0xCB:
            if acc != (arg ^ 0x5A):
                raise SystemExit("constraint failed at offset %d" % i)
        else:
            raise SystemExit("unknown op 0x%02x at %d" % (op, i))
        i += 2

    password = bytes(pw)
    assert len(password) == PW_LEN
    for j in range(PW_LEN):
        args = [program[8*j+3+2*k] ^ 0x5a for k in range(3)]
        assert ((password[j] ^ args[0]) + args[1]) & 255 == args[2]
    flag = bytes(flag_tbl[k] ^ password[k % PW_LEN] for k in range(FLAG_LEN))

    print("password:", repr(password))
    print("flag    :", flag.rstrip(b"\x00").decode())


if __name__ == "__main__":
    main()
