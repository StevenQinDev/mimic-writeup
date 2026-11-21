# The Last Waltz

[English](README.en.md) · Mimic CTF 2026 · Web · 100 分 · [题目页面](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/the-last-waltz)

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Web | 100 | 注册与信箱 | Unicode NFKC 身份查找 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-last-waltz) · [历史实例](http://98.80.121.178:9000) · [赛事链接](../../OFFICIAL-LINKS.md)

页面上的蜡封写着一个 `E`。按常理注册 `E` 就行了——结果报「名称已占用」。

这条报错是整题的转折点。占用说明那个名字在系统里存在，但我进不去；如果注册检查与信箱查询对兼容字符的处理不一致，这个分歧就是本题的入口。

## 全角的 Ｅ

试着用全角 `Ｅ`（U+FF25）注册。系统接受了，然后首页返回了属于 `E` 的信件。

观察结果与兼容归一化（NFKC）一致：

```python
unicodedata.normalize('NFKC', 'Ｅ') == 'E'  # True
unicodedata.normalize('NFKC', 'Е') == 'E'  # False，这是西里尔字母
```

全角 Ｅ 和拉丁 E 在 NFKC 下是等价的，所以任何做过 NFKC 的环节都会把它们当成同一个名字。而西里尔 `Е`（U+0415）长得几乎一样，NFKC 却不认为等价——这一点正好可以用来验证假设。

试出来的边界很清晰：

| 输入 | 结果 |
|---|---|
| 全角 `ｅ` | 能进目标信箱 |
| 修饰符 `ᴱ` | 能进目标信箱 |
| 西里尔 `Е` | 只有普通欢迎页 |

差异说明：**注册时的唯一性检查和信箱查询没有使用同一个规范形式**。保留名校验拒绝 ASCII 身份，却接受兼容形式；信箱查找随后把这个形式解析到同一身份。仅凭这些行为，不能分别确定唯一性查询的具体实现或服务端源码。

## 读信要保住会话

流程不难，但有个细节：注册后必须用同一个会话继续请求，换客户端就变成另一个身份了。

1. `POST /register`，提交 `username` 与至少四字符的 `password`
2. 保存响应里设置的会话 cookie
3. 用同一个 `requests.Session` 请求首页
4. 从 `<article class="letter">` 里读信件

```text
POST /register    username=Ｅ  password=***
GET  /            same session and cookie
```

目标信箱里一共四封，其中一封给出：

```text
RBH{Un1c0d3_Gh0st5_W34r_Ev3ry_F4c3}
```

flag 在说这事：Unicode 的幽灵能戴任何一张脸。

## 本地验证与修复

`mechanism_demo.py` 只比较几个码点在 NFKC 下的结果，不发任何 HTTP 请求。它演示的是全角字符和西里尔字符的分歧，不是完整攻击链。

用户名创建、唯一性检查、保留名校验和信箱查找必须使用同一个规范形式。信件应绑定稳定的用户 ID，避免显示名的规范化变化改变信箱归属。

```powershell
python src/solvers/the-last-waltz/mechanism_demo.py
```

[机制示例](../../../src/solvers/the-last-waltz/mechanism_demo.py)

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
