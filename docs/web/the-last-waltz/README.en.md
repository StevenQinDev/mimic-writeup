# The Last Waltz

[中文](README.zh-CN.md) · Mimic CTF 2026 · Web · 100 points · [Challenge page](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/the-last-waltz)

| Category | Points | Input | Result |
|---|---:|---|---|
| Web | 100 | Registration and mailbox | Unicode NFKC identity lookup |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-last-waltz) · [Historical instance](http://98.80.121.178:9000) · [Event links](../../OFFICIAL-LINKS.md)

The wax seal on the page shows an `E`. Registering `E` seems obvious — and returns "name already taken".

That error is the turning point. The name exists, but it is not mine. If registration and mailbox lookup treat compatible spellings differently, that disagreement is the exploitable condition.

## The fullwidth Ｅ

Register with the fullwidth `Ｅ` (U+FF25). The system accepts it, and the front page then returns letters belonging to `E`.

The observed behavior is consistent with compatibility normalisation (NFKC):

```python
unicodedata.normalize('NFKC', 'Ｅ') == 'E'  # True
unicodedata.normalize('NFKC', 'Е') == 'E'  # False, this is Cyrillic
```

Fullwidth Ｅ and Latin E are equivalent under NFKC, so any step that normalises treats them as the same name. Cyrillic `Е` (U+0415) looks nearly identical but is not equivalent — which makes it a useful control for the hypothesis.

The boundary is clean:

| Input | Result |
|---|---|
| fullwidth `ｅ` | reaches the target mailbox |
| modifier `ᴱ` | reaches the target mailbox |
| Cyrillic `Е` | ordinary welcome page only |

The pattern says: **the registration uniqueness check and the mailbox lookup do not use the same normal form**. The reserved-name check rejects the ASCII identity while accepting a compatible spelling; mailbox lookup then resolves that spelling to the same identity. These observations do not separately establish the exact uniqueness query or its source implementation.

## Reading the mail requires the same session

The flow is simple, but one detail matters: after registering you must keep using the same session. A new client is a new identity.

1. `POST /register` with `username` and a password of at least four characters
2. keep the session cookie from the response
3. request the front page with the same `requests.Session`
4. read the letter from `<article class="letter">`

```text
POST /register    username=Ｅ  password=***
GET  /            same session and cookie
```

The target mailbox holds four letters; one of them gives:

```text
RBH{Un1c0d3_Gh0st5_W34r_Ev3ry_F4c3}
```

The flag says it: a Unicode ghost can wear any face.

## Local verification and the fix

`mechanism_demo.py` compares a few code points under NFKC and issues no HTTP requests at all. It demonstrates the divergence between fullwidth and Cyrillic characters, not the full attack chain.

Username creation, uniqueness checks, reserved-name checks, and mailbox lookup must all use the same normal form. Store letters against a stable user ID so a change in display-name normalization cannot change mailbox ownership.

```powershell
python src/solvers/the-last-waltz/mechanism_demo.py
```

[Mechanism demo](../../../src/solvers/the-last-waltz/mechanism_demo.py)

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
