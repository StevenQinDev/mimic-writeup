from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
meta = json.loads((ROOT / "docs/event-snapshot.json").read_text(encoding="utf-8"))
assert len(meta["challenges"]) == 19
readme = (ROOT / "README.md").read_text(encoding="utf-8")
assert readme.index("A bilingual collection") < readme.index("本仓库收录")
assert "## Capability map / 能力覆盖图" in readme
assert "## Technical coverage / 技术索引" in readme
assert "## Challenges / 题目索引" in readme
assert "```mermaid" in readme
assert "docs/OFFICIAL-LINKS.md" in readme
for stale in (
    ROOT / "docs/VERIFICATION.md",
    ROOT / "docs/verification-current.json",
    ROOT / "docs/NOTES.md",
):
    assert not stale.exists(), f"stale public path remains: {stale.relative_to(ROOT)}"

about = (ROOT / "docs/ABOUT.md").read_text(encoding="utf-8")
reproducibility = (ROOT / "docs/REPRODUCIBILITY.md").read_text(encoding="utf-8")
official_links_text = (ROOT / "docs/OFFICIAL-LINKS.md").read_text(encoding="utf-8")
for page_text, heading in (
    (about, "# About These Writeups / 关于本文集"),
    (reproducibility, "# Running and Reproducing / 运行与复现"),
    (official_links_text, "# Event and Challenge Links / 赛事与题目入口"),
):
    assert page_text.startswith(heading + "\n"), heading
assert "THIRD-PARTY-NOTICES.md" in readme
assert "THIRD-PARTY-NOTICES.md" in about
assert (ROOT / "THIRD-PARTY-NOTICES.md").is_file()
index_intro = "每题目录包含完整原题 `PROMPT.md`、中英文章和附件入口。"
assert readme.count(index_intro) == 1
index_start = readme.index("## Challenges / 题目索引")
index_end = readme.index("## Running scripts / 运行脚本", index_start)
index_section = readme[index_start:index_end]
index_rows = re.findall(
    r"^\| .*?\[中文\]\(docs/([^/]+)/([^/]+)/README\.zh-CN\.md\)",
    index_section,
    flags=re.MULTILINE,
)
assert len(index_rows) == 19
assert index_rows == [
    (challenge["category"], challenge["slug"]) for challenge in meta["challenges"]
]
assert index_section.count("[Prompt](docs/") == 19
assert index_section.count("[English](docs/") == 19
for line in index_section.splitlines():
    if "[English](docs/" in line:
        assert line.index("[English](docs/") < line.index("[中文](docs/"), (
            "English writeup link must precede Chinese"
        )
index_table = [line for line in index_section.splitlines() if line.startswith("|")]
column_counts = [line.count("|") - 1 for line in index_table]
assert len(set(column_counts)) == 1, column_counts
assert column_counts[0] == 7, column_counts[0]

official_links = (ROOT / "docs/OFFICIAL-LINKS.md").read_text(encoding="utf-8")
assert "https://ctf.rarebytehub.com/events/mimic" in official_links
assert "https://ctf.rarebytehub.com/events/mimic/challenges" in official_links
assert "https://ctf.rarebytehub.com/events/mimic/writeups" in official_links
organizer_listings = re.findall(
    r"https://ctf\.rarebytehub\.com/events/mimic/writeups/challenge/[a-z0-9-]+",
    official_links,
)
assert len(organizer_listings) == 19
assert len(set(organizer_listings)) == 19
for port in (8000, 9000, 9001, 9002):
    target = f"http://98.80.121.178:{port}"
    assert official_links.count(f"]({target})") == 1

solution_sources = json.loads(
    (ROOT / "docs/solution-sources.json").read_text(encoding="utf-8")
)
assert set(solution_sources) == {"reviewed_on", "challenges"}
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", solution_sources["reviewed_on"])
source_entries = solution_sources["challenges"]
assert len(source_entries) == 19
assert [item["slug"] for item in source_entries] == [
    challenge["slug"] for challenge in meta["challenges"]
]
assert len({item["official_solution"] for item in source_entries}) == 19
assert sum(item["official_flag"] is not None for item in source_entries) == 18
assert [
    item["slug"] for item in source_entries if item["official_flag"] is None
] == ["i-am-because-we-are"]
for item in source_entries:
    assert item["official_solution"].startswith(
        "https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-"
    )
    assert item["corroboration"] in {
        "published flag and solution compared",
        "workflow only; flag not printed",
    }
    assert official_links.count(f"]({item['official_solution']})") == 1

flag_pattern = re.compile(r"RBH\{[A-Za-z0-9_]+\}")
source_by_slug = {item["slug"]: item for item in source_entries}
for challenge in meta["challenges"]:
    texts = {}
    for lang in ("zh-CN", "en"):
        page = ROOT / "docs" / challenge["category"] / challenge["slug"] / f"README.{lang}.md"
        assert page.is_file(), str(page)
        texts[lang] = page.read_text(encoding="utf-8")
        official_url = source_by_slug[challenge["slug"]]["official_solution"]
        assert texts[lang].count(f"]({official_url})") == 1, (
            f"missing or duplicate official solution link: {challenge['slug']} {lang}"
        )

    assert flag_pattern.search(texts["zh-CN"]), f"missing flag: {challenge['slug']}"
    assert set(flag_pattern.findall(texts["zh-CN"])) == set(
        flag_pattern.findall(texts["en"])
    ), f"flag mismatch: {challenge['slug']}"
    official_flag = source_by_slug[challenge["slug"]]["official_flag"]
    if official_flag is not None:
        assert official_flag in flag_pattern.findall(texts["en"]), (
            f"official flag absent from English article: {challenge['slug']}"
        )
        assert official_flag in flag_pattern.findall(texts["zh-CN"]), (
            f"official flag absent from Chinese article: {challenge['slug']}"
        )
    assert "README.en.md" in texts["zh-CN"], (
        f"missing English navigation: {challenge['slug']}"
    )
    assert "README.zh-CN.md" in texts["en"], (
        f"missing Chinese navigation: {challenge['slug']}"
    )
    if challenge["slug"] == "the-stopped-clock":
        assert "![原始图片中的钟面]" in texts["zh-CN"]
    if challenge["slug"] == "the-quiet-hour":
        assert "![水平差分相关性证据]" in texts["zh-CN"]
    assert "| 分类 | 分值 | 输入 | 结果 |" in texts["zh-CN"], (
        f"missing Chinese metadata table: {challenge['slug']}"
    )
    assert "| Category | Points | Input | Result |" in texts["en"], (
        f"missing English metadata table: {challenge['slug']}"
    )
    category = challenge["category"].upper() if challenge["category"] == "osint" else challenge["category"].capitalize()
    metadata_prefix = f"| {category} | {challenge['points']} |"
    assert metadata_prefix in texts["zh-CN"], (
        f"Chinese category or points mismatch: {challenge['slug']}"
    )
    assert metadata_prefix in texts["en"], (
        f"English category or points mismatch: {challenge['slug']}"
    )
    article_text = texts["zh-CN"] + "\n" + texts["en"]
    prohibited_article_terms = (
        "Actual run report",
        "Methods and credits",
        "Reproduction notes",
        "实际运行报告",
        "方法与来源说明",
        "复现说明",
        "original screenshot absent",
        "原截图缺失",
    )
    for term in prohibited_article_terms:
        assert term not in article_text, (
            f"internal article wording remains in {challenge['slug']}: {term}"
        )
    assert "复现指南" in texts["zh-CN"], f"missing Chinese reproducibility link: {challenge['slug']}"
    assert "Reproducibility guide" in texts["en"], (
        f"missing English reproducibility link: {challenge['slug']}"
    )
    assert texts["zh-CN"].count("[复现指南](") == 1, (
        f"duplicate Chinese reproducibility link: {challenge['slug']}"
    )
    assert texts["en"].count("[Reproducibility guide](") == 1, (
        f"duplicate English reproducibility link: {challenge['slug']}"
    )
manifest = json.loads((ROOT / "docs/input-manifest.json").read_text(encoding="utf-8"))
assert len(manifest) == 11
for item in manifest:
    path = ROOT / item["file"]
    data = path.read_bytes()
    assert len(data) == item["bytes"], f"size mismatch: {item['file']}"
    assert hashlib.sha256(data).hexdigest() == item["sha256"], (
        f"hash mismatch: {item['file']}"
    )

prompt_manifest = json.loads(
    (ROOT / "docs/prompt-manifest.json").read_text(encoding="utf-8")
)
assert len(prompt_manifest["challenges"]) == 19
prompt_entries = {item["slug"]: item for item in prompt_manifest["challenges"]}
manifest_files = {}
for item in manifest:
    manifest_files.setdefault(item["challenge"], set()).add(item["file"])

for challenge in meta["challenges"]:
    slug = challenge["slug"]
    prompt_page = ROOT / prompt_entries[slug]["prompt_file"]
    prompt_data = prompt_page.read_bytes()
    prompt_text = prompt_data.decode("utf-8")
    assert hashlib.sha256(prompt_data).hexdigest() == prompt_entries[slug]["prompt_sha256"]
    assert "## Original statement" in prompt_text
    assert f"| Challenge ID | {challenge['id']} |" in prompt_text
    assert set(prompt_entries[slug]["attachments"]) == manifest_files.get(slug, set())
    assert r"\r\n" not in prompt_text, f"literal line-break escape in prompt: {slug}"
    prompt_lines = prompt_text.splitlines()
    english_line = "- [English writeup](README.en.md)"
    chinese_line = "- [中文题解](README.zh-CN.md)"
    assert prompt_lines.count(english_line) == 1, f"English prompt link: {slug}"
    assert prompt_lines.count(chinese_line) == 1, f"Chinese prompt link: {slug}"
    assert prompt_lines.index(chinese_line) == prompt_lines.index(english_line) + 1, (
        f"prompt language links must be adjacent lines: {slug}"
    )
    if challenge["category"] == "web":
        target = prompt_entries[slug]["historical_target"]
        for lang in ("zh-CN", "en"):
            page = ROOT / "docs" / challenge["category"] / slug / f"README.{lang}.md"
            assert f"]({target})" in page.read_text(encoding="utf-8"), (
                f"missing competition-time Web target: {slug} {lang}"
            )

    folder = ROOT / "docs" / challenge["category"] / slug
    assert "[原题与附件](PROMPT.md)" in (
        folder / "README.zh-CN.md"
    ).read_text(encoding="utf-8")
    assert "[Original prompt and attachments](PROMPT.md)" in (
        folder / "README.en.md"
    ).read_text(encoding="utf-8")

for page in ROOT.rglob("*.md"):
    text = page.read_text(encoding="utf-8")
    fence_open = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if not re.fullmatch(r"`{3,}.*", line):
            continue
        if fence_open:
            fence_open = False
        else:
            assert re.fullmatch(r"`{3,}[A-Za-z0-9_+.-]+", line), (
                f"code fence needs a language at {page}:{line_number}"
            )
            fence_open = True
    assert not fence_open, f"unbalanced code fence: {page}"
    for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            assert (page.parent / target.split("#")[0]).exists(), (page, target)

public_text_files = [
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / ".gitignore",
    ROOT / ".gitattributes",
    ROOT / "pyproject.toml",
    ROOT / "requirements-lock.txt",
    ROOT / "requirements.txt",
]
for pattern in ("*.md", "*.py", "*.json", "*.toml", "*.txt"):
    public_text_files.extend(
        path
        for path in ROOT.rglob(pattern)
        if path.resolve() != Path(__file__).resolve()
        if not any(part in {".git", ".venv", "outputs"} for part in path.parts)
    )
public_text = "\n".join(
    path.read_text(encoding="utf-8") for path in sorted(set(public_text_files))
)
assert not re.search(r"(?:[A-Za-z]:\\Users\\|/Users/)", public_text), (
    "absolute local user path remains"
)
assert not re.search(r"\bT-\d{4}-\d{4}\b", public_text), "case identifier remains"
assert not re.search(r"\bMSC v\.?\d", public_text), "compiler build string remains"
assert not re.search(r"tags/v\d+\.\d+\.\d+", public_text), "full Python build string remains"
assert not re.search(r"\bWindows-\d+(?:\.\d+)?", public_text), "OS build string remains"
assert not re.search(r"\b(?:DESKTOP|LAPTOP)-[A-Z0-9]+", public_text), "host name remains"
assert not re.search(r"[+-]0?[89]:?00\b", public_text), "time-zone offset remains"

run_record = json.loads((ROOT / "docs/test-results.json").read_text(encoding="utf-8"))
assert set(run_record) == {"timestamp", "python", "platform", "scope", "results"}, (
    "unexpected fields in the run record"
)
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", run_record["timestamp"]), (
    "run record must keep the date only, with no clock time or zone"
)
assert re.fullmatch(r"\d+\.\d+", run_record["python"]), (
    "run record must keep the Python major.minor version only"
)
assert run_record["platform"] in {"Windows", "Linux", "Darwin"}, (
    "run record must keep the OS family only"
)
run_results = run_record["results"]
assert len(run_results) == 19
assert len({item["script"] for item in run_results}) == 19
expected_scripts = sorted(
    path.relative_to(ROOT).as_posix()
    for pattern in ("*/solve_cycles.py", "*/solve.py", "*/decrypt.py", "*/mechanism_demo.py")
    for path in (ROOT / "src/solvers").glob(pattern)
)
assert sorted(item["script"] for item in run_results) == expected_scripts
for item in run_results:
    script = ROOT / item["script"]
    assert script.is_file(), f"run record points at a missing script: {item['script']}"
    assert item["slug"] == script.parent.name
    assert item["exit_code"] == 0
    assert item["kind"] == (
        "demo" if script.name == "mechanism_demo.py" else "solver"
    )
    assert item["script_sha256"] == hashlib.sha256(script.read_bytes()).hexdigest(), (
        f"run record is stale: {item['script']}"
    )
assert sum(item["kind"] == "solver" for item in run_results) == 15
assert sum(item["kind"] == "demo" for item in run_results) == 4
assert len({item["slug"] for item in run_results if item["kind"] == "solver"}) == 13
assert len({item["slug"] for item in run_results if item["kind"] == "demo"}) == 4

print(
    "19 bilingual articles, official sources, flags, inputs, local links, "
    "and run record: PASS"
)
