# Three Guards

[English](README.en.md) · Mimic CTF 2026 · Crypto · 300 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Crypto | 300 | 密文与 LFSR 参数 | LFSR 相关性分析 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-three-guards)

三个 LFSR 各 17、19、18 位，加起来 54 位状态。按 2^54 枚举是不用想的。但输出是 `z = a if b else c`——选择器把两个外侧寄存器和 z 绑在了一起，于是可以分开筛：先用相关性把 Guard 1 和 Guard 3 定下来，再用它们反解 Guard 2。

## 先把题面的提示变成字符表

提示是 `names first`。取标题去空格后的 `THREEGUARDS` 的全部字母，按首次出现去重：

```text
THREE GUARDS → THREGUADS
```

再把标准 Base64 表里还没出现的字符按原顺序补上，得到完整的 64 字符表：

```text
THREGUADSBCFIJKLMNOPQVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

用这张表替换标准 Base64 表解码，得到 67 字节。

已知明文前缀是 `The King's decree: the vault code is RBH{`，共 41 字节。与密文异或，按 MSB 优先拆成 328 位——这就是后面要比对的密钥流。

以 Guard 1 为例：先输出 `seed & 1`，取第 0、3 位 XOR 为反馈，右移后把反馈放到第 16 位。种子 1 因此先输出 1，再得到状态 65536。这明确了移位方向和输出时机，任一处反过来都会改变密钥流。

## 相关性为什么够用

如果三路输出近似均衡且独立，那么外侧路被选中的概率是 1/2；没被选中时，碰巧与 z 相等的概率也约 1/2。两者相加，外侧路与 z 的匹配率约 3/4。

这是**统计动机，不是对本题这 328 位的精确保证**。真实序列有偏差，所以匹配率只能用来排序，不能用来定论。

Guard 1 宽 17、taps 0/3；Guard 3 宽 18、taps 0/7。各自枚举非零种子（2^17 − 1 和 2^18 − 1 个），按与已知流的匹配位数排序：

| 寄存器 | 最佳种子 | 匹配位数 |
|---|---|---|
| Guard 1 | 64988 | 245 / 328 |
| Guard 3 | 214757 | 254 / 328 |

实现上不是一个个老老实实移位：先预计算 GF(2) 基向量序列，再用 Gray code 每次只异或一个基向量，距离用整数的 `bit_count()` 算。这让 2^17 + 2^18 次尝试在秒级跑完。

## 用 mask 反解选择器

令 `mask = a XOR c`。在 mask 为 1 的位置上，a 和 c 一定不同，此时 z 是由 b 决定的；在 mask 为 0 的位置上，a 和 c 相同，z 必然等于这个共同值。于是：

```text
(b AND mask) == ((z XOR c) AND mask)
```

这条式子把 b 的每一位约束了出来。328 位里能得到 157 个有效约束，在 Guard 2 的 2^19 − 1 个非零种子里只剩下一个满足全部条件：`478853`。

最终种子按三路顺序是：

```text
(64988, 478853, 214757)
```

```text
RBH{tw0_gu4rds_t0ld_th3_truth}
```

## 全长校验不能省

相关性只负责筛选，它给出的是候选，不是结论。真正的判据是把种子代回寄存器实现，重新解出完整明文，再重新加密、按自定义表编码，必须精确匹配全部 92 个字符（含填充）。

完整解密与回编码才是判定步骤。相关性只负责缩小搜索范围，不能单独证明结果。

搜索量从 2^54 降到 2^17 + 2^18 + 2^19，全部是对固定 328 位片段做整型运算。

## 复现

```powershell
python src/solvers/three-guards/solve.py
```

[完整脚本](../../../src/solvers/three-guards/solve.py)，只依赖 Python 标准库。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
