"""Decode the single-image stereogram in The Quiet Hour.

The image contains horizontally repeating noise. Most of each row uses a
base period P_y, while the hidden text changes the local repeat distance to
P_y + delta(x, y). Mapping delta to grayscale reveals the glyphs.

1. Estimate P_y independently for every row from the horizontal difference.
2. In the range P_y +/- 25, find the best local repeat distance.
3. Apply a median filter and write the result to recovered.png.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d, median_filter

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forensic_tools import output_dir

SRC = Path(__file__).with_name("the_quiet_hour.png")
OUT = output_dir("the-quiet-hour")

img = np.asarray(Image.open(SRC).convert("RGB"), dtype=np.float32)
h, w, _ = img.shape
print(f"[*] image {w}x{h}")

# ---------- 1) Base period for each row ----------
diff = img[:, 1:] - img[:, :-1]
cands = np.arange(40, 151)
corr = np.stack(
    [np.mean(diff[:, d:] * diff[:, :-d], axis=(1, 2)) for d in cands], axis=1
)                                                   # (h, len(cands))
periods = cands[np.argmax(corr, axis=1)]            # One base period per image row.
print("[*] period percentiles:", np.percentile(periods, [5, 25, 50, 75, 95]).round(0).tolist())
print("[*] first 20 rows:", periods[:20].tolist())

# ---------- 2) Local repeat-distance offset ----------
diff = img - np.roll(img, 1, axis=1)                # difference from x-1
yy = np.arange(h)[:, None]
xx = np.arange(w)[None, :]

deltas = np.arange(-25, 26)
best_cost = np.full((h, w), np.inf, np.float32)
disparity = np.zeros((h, w), np.int16)

for delta in deltas:
    distances = periods[:, None] + delta
    shifted = diff[yy, (xx - distances) % w]
    err = np.mean((diff - shifted) ** 2, axis=2)     # RGB squared error
    err = uniform_filter1d(err, size=15, axis=1)     # horizontal smoothing
    upd = err < best_cost
    best_cost = np.where(upd, err, best_cost)
    disparity = np.where(upd, delta, disparity)

# ---------- 3) Denoise and write the result ----------
disparity = median_filter(disparity, size=(3, 7))
result = np.clip((disparity + 25) * 255 / 50, 0, 255).astype(np.uint8)
Image.fromarray(result).save(OUT / "recovered.png")
np.save(OUT / "disparity.npy", disparity)
print("[*] saved recovered.png / disparity.npy")
