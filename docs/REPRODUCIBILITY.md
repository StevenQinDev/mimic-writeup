# Running and Reproducing / 运行与复现

## Environment / 环境

The project targets Python 3.12 and was tested with Python 3.12.10. Exact dependency versions are pinned in `requirements-lock.txt`.

本项目使用 Python 3.12，并以 Python 3.12.10 完成验证；完整依赖版本见 `requirements-lock.txt`。

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --requirement requirements-lock.txt
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements-lock.txt
```

## Offline suite / 离线套件

`scripts/verify_offline.py` runs 15 solver or extractor scripts across 13 challenges and four local Web examples in isolated output directories. Child processes block socket connections, and original executables are parsed statically rather than executed.

`scripts/verify_offline.py` 在独立输出目录中运行 15 个求解或提取脚本，覆盖 13 道题，并运行 4 个 Web 机制示例。子进程禁用 socket 连接，并静态解析题目二进制，不执行原始 ELF 或 Python 字节码。

Challenge scripts write generated files to `outputs/<challenge>/` regardless of the shell's current directory. The directory is ignored by Git.

题目脚本会把生成文件写入 `outputs/<challenge>/`，与当前 shell 的工作目录无关；该目录不进入 Git。

```powershell
python scripts/verify_offline.py
python tests/check_collection.py
python tests/check_semantics.py
python scripts/render_evidence.py
```

The latest run is recorded in `docs/test-results.json`. It keeps the OS family, Python major.minor version, and run date, while leaving out build identifiers, clock times, and time zones. The same check covers all 19 prompts, 38 articles, flag sets, language navigation, local links, and attachment sizes and hashes.

最近一次运行结果保存在 `docs/test-results.json`，只记录操作系统家族、Python 主次版本和运行日期，不记录 build 标识、时钟时间或时区。同一套检查还覆盖 19 个题面、38 篇文章、flag 集合、双语导航、本地链接、附件大小和 SHA-256。

## Manual steps / 手工步骤

| Type / 类型 | Challenges / 题目 | How to reproduce / 复现方式 |
|---|---|---|
| Visual reading / 人工读图 | The Stopped Clock, Night 4,018, Halvard’s Light, The Quiet Hour | Generate the listed images, then compare the text / 运行脚本生成图片，再按文章核对文字 |
| Public sources / 公开来源 | Project Borealis | Follow the linked Space Norway, USGS, Polar Journal, and VesselFinder records in order / 按文章列出的公开来源逐项核对 |
| Platform flow / 平台流程 | I Am Because We Are | Complete the membership-verification flow from the prompt / 按原题完成群组与私聊验证 |
| HTTP state analysis / HTTP 状态分析 | Lethe | Follow the official request history and run the in-memory rowid example / 对照官方请求历史并运行内存数据库示例 |

## Web challenges / Web 题说明

The Web addresses come from the original prompts and refer to historical competition instances. All four Web articles include local mechanism examples. Their historical requests are documented for reading, not executed by these examples. Lethe and Postmarked incorporate the organizer’s published request observations. Current reachability is not treated as proof of the original behavior.

四道 Web 题的目标地址来自原题，属于赛事期间的历史实例。四道题均提供本地机制示例。文中的历史请求供阅读，示例不发送这些请求。Lethe 与 Postmarked 补充采用了组织方公开的请求观察。文中不会把历史地址是否仍可访问当作漏洞验证。

## Known limits / 已知限制

- **Lethe:** the official solution documents the orphan echo at 9 and recovery of its complete flag. The local demo verifies rowid reuse and a dangling association, not the historical server implementation.
- **Project Borealis:** public sources confirm the cable incident, station, and vessel fields; the supplied photograph provides visual context.
- **I Am Because We Are:** membership verification depends on the event-time group and bot, so the flow cannot be replayed offline. The official article confirms the workflow but does not print its flag.
- **Forensic images:** final text is read visually; the scripts do not perform OCR.

- **Lethe：** 官方题解记录了编号 9 的孤立回声及完整 flag 的恢复。本地示例验证编号复用和残留关联，不等于复现历史服务端实现。
- **Project Borealis：** 公开来源可以逐项确认断缆、站点和船舶字段；题目照片提供现场背景。
- **I Am Because We Are：** 成员验证依赖赛事期间的实时群组和机器人，无法在离线仓库中重放。官方文章确认流程，但没有展示 flag。
- **取证图片：** 最终文字由人工辨读，脚本不进行 OCR。

## What each check establishes / 各项检查的范围

`check_collection.py` checks all 19 original prompts, 38 language articles, official source links, attachment hashes and publication hygiene. `check_semantics.py` checks numerical claims, Unicode code points, PNG scanline counts, and independently simulated VM behavior. The offline suite runs 19 entries: 15 solver/extractor runs and four synthetic Web demonstrations. `render_evidence.py` regenerates four explanatory images; the remaining forensic images are produced by their challenge solvers. None of these checks substitutes for reading the explanations.

`check_collection.py` 检查 19 份原题、38 篇文章、官方来源链接、附件哈希和公开文本卫生；`check_semantics.py` 检查关键数值、Unicode 码点、PNG 扫描行数与独立 VM 行为。离线套件共运行 19 项：15 次求解或提取运行与 4 个合成 Web 示例。`render_evidence.py` 重生成四张解释图，其余取证图由对应题目脚本生成；自动检查不能替代对正文推理的阅读。
