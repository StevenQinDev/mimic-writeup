"""Recover the authenticated hidden log directly from the original PNG."""
from pathlib import Path
import base64, hashlib, io, struct, zipfile, zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forensic_tools import output_dir

out = output_dir("halvards-light")
data = Path(__file__).with_name("halvards_light.png").read_bytes()
pos = 8
assert data[:8] == b"\x89PNG\r\n\x1a\n"
while True:
    size = int.from_bytes(data[pos:pos+4], "big")
    kind = data[pos+4:pos+8]
    pos += size + 12
    if kind == b"IEND":
        break
archive = data[pos:]
z = zipfile.ZipFile(io.BytesIO(archive))
info = z.getinfo("keeper_log.txt")
off = info.header_offset
name_len, extra_len = struct.unpack_from("<HH", archive, off+26)
extra = archive[off+30+name_len:off+30+name_len+extra_len]
p = 0
while p < len(extra):
    tag, size = struct.unpack_from("<HH", extra, p)
    value = extra[p+4:p+4+size]
    p += 4+size
    if tag == 0x7876:
        blob = base64.b64decode(zlib.decompress(value), validate=True)
        break
else:
    raise ValueError("Missing local-header binding field")
assert blob[:3] == b"LK1"
p = 4 + blob[3]  # length-prefixed scheme, NOT NUL-terminated
scheme = blob[4:p].decode("ascii")
iters = int.from_bytes(blob[p:p+4], "big")
salt = blob[p+4:p+20]
nonce = blob[p+20:p+32]
ciphertext_and_tag = blob[p+32:]
# PNG metadata gives lowercase ship password; WAV spectrogram supplies 7QVWG.
key = hashlib.pbkdf2_hmac("sha256", b"marigold:7qvwg", salt, iters, 32)
plaintext = AESGCM(key).decrypt(nonce, ciphertext_and_tag, None)
assert AESGCM(key).encrypt(nonce, plaintext, None) == ciphertext_and_tag
(out / "decrypted-log.txt").write_bytes(plaintext)
print("scheme:", scheme)
print("iterations:", iters)
print("salt:", salt.hex())
print("nonce:", nonce.hex())
print("GCM authentication and ciphertext round trip: PASS")
print(plaintext.decode("utf-8"))
