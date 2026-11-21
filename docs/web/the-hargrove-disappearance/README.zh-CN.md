# The Hargrove Disappearance

[English](README.en.md) · Mimic CTF 2026 · Web · 500 分 · [题目页面](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/the-hargrove-disappearance)

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Web | 500 | 案件报告 API | NFKC 路径穿越 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-hargrove-disappearance) · [历史实例](http://98.80.121.178:9002) · [赛事链接](../../OFFICIAL-LINKS.md)

这是一道 500 分题。难点不在构造 payload，在于先搞明白这个 API 到底在拿 `module` 干什么——它没有直接回显，能看到的只有报错。

## 先让报错说话

注册后（`POST /register`，然后保持同一会话）：

```text
GET /report?module=ballistics
```

正常返回 ballistics 档案。构造不同类型的模块名，可以观察三种错误状态：

```text
unknown simple name       -> no such table: mod.notes
missing subdirectory      -> unable to open database
non-database file         -> file is not a database
```

这三句话的差别很关键，它们分别对应三种情况：

| 报错 | 实际状态 |
|---|---|
| `no such table` | 数据库能打开，但没有这张表 |
| `unable to open database` | 路径无法打开，不存在只是可能原因之一 |
| `file is not a database` | 路径存在，但不是 SQLite 文件 |

这三种状态之间的差别，使报错可以用于目录探测。

但有个陷阱要避开：**单独的「缺表」错误不能证明程序刚刚创建了数据库**。一个已存在的空库同样会返回 `no such table`。如果据此判断「这个路径是我创建的」，后面的推理就全歪了。

## 过滤和归一化，顺序反了

接下来试路径。

`a/../b` 会被处理成 `a/b`——说明程序在**过滤** `../`。但 `．．／x` 能往上跳一级。

下面是说明处理顺序的模型。官方描述会反复清除 ASCII 穿越片段；这里用一次替换展示相同的归一化缺陷，不将它当作恢复出的服务端源码：

```python
normalized = unicodedata.normalize('NFKC', value.replace('../', ''))
```

拆开看这个顺序为什么致命：

1. 先 `replace('../', '')`，删掉所有 ASCII 的 `../`
2. 此时全角点 `．`（U+FF0E）和全角斜杠 `／`（U+FF0F）**不是 ASCII**，一个都没被删
3. 然后才做 NFKC，全角符号被折叠成普通的 `../`
4. 后续检查未能约束在预期的模块目录内

正确的顺序是先规范化、再检查。反过来，就等于把检查放在了一次变形之前。

还有一条有用的观察：两层上跳会被拒绝。说明外层还是有路径边界的，能越过的只有一层——这个限制决定了 payload 的构造方式。

## 找到封存目录

模块数据库的位置是 `modules/<ref>`。案件笔记里给出编号 `TR-0344`。用上面的目录探测法比对，能发现一个 `.sealed` 目录。

组合起来：

```text
．．／.sealed/TR-0344
```

从 `modules/` 上跳一层，落到兄弟目录 `.sealed/TR-0344`。

返回的档案提到身份复核和 23:44 的监控中断：

```text
RBH{23_44_cameras_died_the_tea_stayed_warm_3055d0a6}
```

## 本地复现与修复

`mechanism_demo.py` 用标准库演示「先过滤、后 NFKC」这个顺序，不连接题目服务。

修复有四条，顺序很重要：

1. **先规范化再检查**。所有编码、归一化、解码做完之后，再判断路径
2. **基于规范路径判断边界**。解析路径后用 `candidate.is_relative_to(base)` 或 `os.path.commonpath` 检查祖先关系，不能使用原始字符串前缀
3. **授权在打开文件之前**。先问「这个人能不能读」，再问「文件在哪」
4. **读操作不该创建数据库**，错误信息也不该泄露目录结构——`unable to open` 和 `no such table` 的区别本身就是一份目录地图

```powershell
python src/solvers/the-hargrove-disappearance/mechanism_demo.py
```

[机制示例](../../../src/solvers/the-hargrove-disappearance/mechanism_demo.py)

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
