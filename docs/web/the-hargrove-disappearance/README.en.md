# The Hargrove Disappearance

[中文](README.zh-CN.md) · Mimic CTF 2026 · Web · 500 points · [Challenge page](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/the-hargrove-disappearance)

| Category | Points | Input | Result |
|---|---:|---|---|
| Web | 500 | Case-report API | NFKC path traversal |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-hargrove-disappearance) · [Historical instance](http://98.80.121.178:9002) · [Event links](../../OFFICIAL-LINKS.md)

This is a 500-point challenge. The hard part is determining how the API interprets `module`; the application provides only error messages.

## Let the errors talk

After registering (`POST /register`, then staying in the same session):

```text
GET /report?module=ballistics
```

It returns the ballistics record. Crafted probes produce three distinct error states:

```text
unknown simple name       -> no such table: mod.notes
missing subdirectory      -> unable to open database
non-database file         -> file is not a database
```

The distinction matters, and each message maps to a state:

| Error | Actual state |
|---|---|
| `no such table` | the database opened, but has no such table |
| `unable to open database` | the path cannot be opened; absence is one possible cause |
| `file is not a database` | the path exists and is not SQLite |

That distinction turns the error text into an oracle for directory probing.

One trap to avoid: **a missing-table error alone does not prove the program just created a database**. An existing empty database returns the same message. Concluding "this path is mine" from that leads the rest of the reasoning astray.

## Filtering and normalisation, in the wrong order

Now try paths.

`a/../b` is reduced to `a/b`, so the program **filters** `../`. But `．．／x` escapes one level up.

An illustrative ordering model explains the traversal. The official article describes repeated ASCII stripping; this single-pass example demonstrates the same normalization mismatch without claiming to be recovered source:

```python
normalized = unicodedata.normalize('NFKC', value.replace('../', ''))
```

Why that order is fatal:

1. `replace('../', '')` removes every ASCII `../` first
2. fullwidth `．` (U+FF0E) and `／` (U+FF0F) are **not ASCII**, so nothing is removed
3. NFKC then folds the fullwidth forms into ordinary `../`
4. later checks do not enforce the intended module-directory boundary

The correct order is normalise first, then check. Doing it backwards puts the check before a transformation that recreates the very sequence it was meant to stop.

One useful constraint from probing: two levels of ascent are rejected. The outer boundary still exists, so only one level is available, and that shapes the payload.

## Reaching the sealed record

Module databases live at `modules/<ref>`. The case notes give the identifier `TR-0344`. Directory probing by error message reveals a `.sealed` directory.

Combining them:

```text
．．／.sealed/TR-0344
```

That ascends one level from `modules/` into the sibling `.sealed/TR-0344`.

The returned record mentions an identity review and a 23:44 surveillance interruption:

```text
RBH{23_44_cameras_died_the_tea_stayed_warm_3055d0a6}
```

## Local reproduction and the fix

`mechanism_demo.py` demonstrates the "filter first, normalise second" ordering with the standard library and does not connect to the challenge service.

Four fixes, and the order of operations is the point:

1. **normalise before checking** — after all decoding, normalisation, and unfolding, then validate the path
2. **check boundaries on the resolved path** — resolve the candidate and require `candidate.is_relative_to(base)` (or use `os.path.commonpath`), rather than a raw string prefix
3. **authorise before opening the file** — ask "may this user read it" before asking "where is it"
4. **a read must not create a database**, and errors must not leak directory structure — the difference between `unable to open` and `no such table` is itself a directory map

```powershell
python src/solvers/the-hargrove-disappearance/mechanism_demo.py
```

[Mechanism demo](../../../src/solvers/the-hargrove-disappearance/mechanism_demo.py)

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
