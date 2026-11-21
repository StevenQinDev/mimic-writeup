# Three Guards — Original Prompt

> Reproduced from the Mimic CTF 2026 challenge page. The original English statement is unchanged; any Web or Telegram links in it refer to the competition environment.

| Field | Value |
|---|---|
| Challenge ID | 37 |
| Category | Crypto |
| Points | 300 |
| Difficulty | Medium |
| Source | [Mimic CTF 2026 challenge page](https://ctf.rarebytehub.com/events/mimic/challenges) |

## Original statement

````text
Every night, the King’s vault is guarded by three guards.

The first and the third guard speak the truth. The middle one decides who gets to speak.

Last night, a spy slipped into the guard room and copied the King’s decree. The report was written in the guards’ own tongue, signed with their names first (their name is the title of this tale). The spy never learned what it says, only how it begins:

The King's decree: the vault code is RBH{

Each second, every guard speaks his lowest bit and shifts right. The XOR of his tapped bits (before the shift) enters at the top.

Guard 1: 17 bits, taps [0, 3]
Guard 2: 19 bits, taps [0, 1, 2, 5]
Guard 3: 18 bits, taps [0, 7]

The middle guard picks the speaker: if his bit is 1, Guard 1 speaks, otherwise Guard 3. Eight bits make a byte, highest bit first, and each byte is XORed with the decree. All seeds are secret and non-zero.

c1oToD5pgTjnkVWjQr4ZflOD+h4KueNOl+qXRiBe7B27fbxyveiiDqFkWBsf7dEk7MubeIBMA5oJg/IpamGTKAE+UM==

Find the vault code.
````

## Attachments

No downloadable attachment. All required input is in the prompt.

## Writeups and files

- [English writeup](README.en.md)
- [中文题解](README.zh-CN.md)
- [Input hashes](../../input-manifest.json)

The challenge statement and attachments belong to Rare Byte Hub and their authors. They are included for reference and excluded from the repository's MIT license.
