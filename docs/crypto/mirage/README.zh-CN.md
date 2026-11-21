# Mirage

[English](README.en.md) · Mimic CTF 2026 · Crypto · 100 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Crypto | 100 | 题目密文 | Base64 索引减法 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-mirage)

flag 的前缀 `RBH{` 有四个字节，其中前三字节 `RBH` 的 Base64 编码固定为 `UkJI`。而密文前四位是 `VW2m`。两个四位串对上了，差值就是密钥的开头。这题的入口只有这一个抓手，比「看起来像 Base64」可靠得多。

```text
VW2mfl6UNp2XYoGKO4K9dp9SdZ+RYpJPe4O9WIaoTJh=
```

## 这是 Base64 上的加密，不是 Base64

密文的字符集和末尾补位的 `=` 都指向 Base64。但 44 字符的密文直接解码得到 32 字节，并非预期的 flag，因此尝试额外的变换层。

方向有两种可能：先解码再解密，或先加密再编码。这两种差别很大。已知前缀提供了可检验的模型：`UkJI` 是明文的 Base64，它出现在密文里的位置和长度都吻合，据此尝试**加密作用在 Base64 字符的索引上**，输出仍是合法 Base64，最后才被当成文本传出来。

## 四个字符，一个候选密钥

标准 Base64 字母表：

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

按循环加法建模 `C_i = (P_i + K_i) mod 64`，四个已知位置各算一次：

| 位置 | 密文 | C_i | 已知字符 | P_i | (C_i − P_i) mod 64 | 密钥字符 |
|---|---|---:|---|---:|---:|---|
| 0 | V | 21 | U | 20 | 1 | B |
| 1 | W | 22 | k | 36 | 50 | y |
| 2 | 2 | 54 | J | 9 | 45 | t |
| 3 | m | 38 | I | 8 | 30 | e |

得到 `Byte`。这里减的必须是**字母表索引**，不是 ASCII 字节值——两种减法只在少数位置碰巧一致，多试几位就会分叉。

## 对整段数据检验周期 4 的候选

把 `Byte` 当成周期 4 的密钥，对所有非填充字符计算 `(C_i − K_(i mod 4)) mod 64`，保留 `=`：

```text
UkJIezN2M3J5X2ZsNGdfc3Q0cnRzX3cxdGhfVWtKSX0=
```

四个已知位置只能给出一组候选周期，它**不能证明**周期就是 4——周期 8 或 12 也可能在前四位上恰好重合。判据是整串解码后是否可读，以及回编码后是否逐字符还原：

```text
RBH{3v3ry_fl4g_st4rts_w1th_UkJI}
```

flag 本身就在说这件事：每个 flag 都以 `UkJI` 开头。

脚本最后把明文重新 Base64 编码、加回循环密钥，断言结果与原密文完全一致。时间与空间复杂度均为 O(n)。

## 复现

只需要 Python 标准库：

```powershell
python src/solvers/mirage/solve.py
```

[完整脚本](../../../src/solvers/mirage/solve.py)

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
