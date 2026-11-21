# Lethe

[中文](README.zh-CN.md) · Mimic CTF 2026 · Web · 300 points · [Challenge page](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/lethe)

| Category | Points | Input | Result |
|---|---:|---|---|
| Web | 300 | HTTP identifiers, status codes, and record lifecycle | Orphan echo recovery and SQLite rowid reuse |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-lethe) · [Historical instance](http://98.80.121.178:8000) · [Event links](../../OFFICIAL-LINKS.md)


The title names the river of forgetting. The important distinction is between a **memory row** and its **echo**: deleting one can leave the other behind. The request observations below come from the organizer's official solution; the local example reproduces the database mechanism without contacting the event service.

## 1. Compare memory existence with echo existence

For `/memory/N`, a readable record returns 200, an existing record owned by someone else returns 403, and a missing record returns 404. `/resonance/N` independently indicates whether an echo exists.

| Identifiers | Memory state | Interpretation |
|---|---|---|
| 1, 2, 4, 5, 6 | Sealed, 403 | Existing rows that this session cannot delete |
| 3, 9 | Missing, 404; resonance present | Orphan echoes: the row has gone but its echo survives |
| 10, 11, 12 | Owned, 200 | Rows that this session may delete |

This second endpoint is what makes 9 a reasoned target. A gap alone does not establish that a memory previously existed there. An echo without a memory does.

## 2. Work out which identifier can be reclaimed

An ordinary SQLite `INTEGER PRIMARY KEY`, when omitted on insert, normally chooses **one greater than the largest current rowid**. It does not fill the smallest hole. `AUTOINCREMENT` has a different non-reuse rule; it is not the model used here.

With rows 10–12 present, the next row is 13. Forgetting that highest row and creating another reuses 13. More usefully, forgetting all the owned high rows leaves 6 as the largest surviving identifier. The next three insertions receive 7, 8, then 9.

Why not reclaim 3? Sealed row 6 is a floor the session cannot remove. Deleting owned rows cannot make the allocator descend below that floor. Of the two orphan echoes, 9 is reachable.

## 3. Recreate 9 and read its inherited echo

The official sequence uses the following routes. These are historical request descriptions, not commands required by the offline scripts:

```text
GET  /memory/N and /resonance/N   compare row and echo existence
POST /forget/10                 remove owned high row
POST /forget/11                 remove owned high row
POST /forget/12                 largest remaining id is now 6
POST /remember                  new memory 7
POST /remember                  new memory 8
POST /remember                  new memory 9
GET  /memory/9                  read the new memory and inherited echo
```

If an exploratory insertion created 13, forget it as well before starting the three insertions. The new title and body are unimportant. The old echo is associated with the raw number 9, so the new row acquires an association intended for the deleted row. The echo contains the **complete** flag, including its suffix:

```text
RBH{th3_r1v3r_f0rg3ts_th3_row_n0t_th3_numb3r_9_b0a6}
```

There is no need to infer a hash formula for `b0a6`; it is read as part of the recovered text.

## 4. Reproduce the identity error locally

```powershell
python src/solvers/lethe/mechanism_demo.py
```

The [in-memory SQLite example](../../../src/solvers/lethe/mechanism_demo.py) seeds sealed and owned rows plus synthetic `DEMO_ONLY` echoes. It checks that deleting owned rows allocates `[7, 8, 9]`, that the new 9 inherits stale text, and that a foreign key with cascading deletion prevents the stale association. It also checks the counterexample: a vacant 3 is not allocated while 6 still exists.

The defect is a lifetime mismatch between related records. Use a stable identity for associations, enforce referential integrity with foreign keys enabled, and apply authorization to the associated object. Avoid treating an integer that may be reused as proof of historical identity. This example verifies that mechanism; the event HTTP observations remain attributed to the official article.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
