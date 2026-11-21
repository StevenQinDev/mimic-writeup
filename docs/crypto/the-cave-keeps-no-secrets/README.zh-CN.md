# The Cave Keeps No Secrets, Only Order

[English](README.en.md) · Mimic CTF 2026 · Crypto · 300 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Crypto | 300 | 题目密文 | 自定义字符表、模减法、rail fence |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-cave-keeps-no-secrets-only-order)

题面是六行诗。第一眼最容易抓的是每行第一个词：Fire、All、Chained、A、Dawn、Every，拼起来是 `FACADE`。它太显眼，显眼到像是答案——但它不是 flag，它只是后面那层字符表的原料。这题的真正结构是三组参数各由一条线索给出，缺一条就解不动。

## FACADE 只是原料

`FACADE` 六个字母里有重复：A 出现两次。按首次出现去重，得到 `facde`。再追加标准十六进制表里还没用到的字符 `0123456789b`，拼成一张 16 字符的自定义表：

```text
facde0123456789b
```

这张表的用途是替换十六进制字母表——密文里的每个字符按位置对应到 `0123456789abcdef`，而不是直接按字面值解析。

## 三个参数，三条线索

题面里的三处细节分别决定了一件事：

| 线索 | 给出的参数 |
|---|---|
| 每节共有的最长单词 `illusion` | 镜像反转成 `noisulli`，作循环模加法密钥 |
| 诗正好三节 | rail fence 的轨数 = 3 |
| 六个首词 | 自定义 hex 字符表 |

`illusion` 取镜像是题面说的「镜子」，不是任意选的单词：它是三节里每节都出现、而且长度最长的一个。

## 倒着拆

拿到密文：

```text
7f9d875d53768b47854b569988768e7890888b909a4b768a785d808253946e475c79475e949d7687
```

按上面的参数反推，顺序是：

1. 自定义表第 j 个字符 → 标准表第 j 个字符
2. 按 hex 解析成 40 字节（脚本会重新算一遍并打印，不靠手数）
3. 每字节减去循环密钥 `noisulli` 的对应字节，对 256 取模
4. 按三轨的顺序还原

第 4 步是最容易做错的地方。三轨**不是**把 40 字节平均切成三段，也不是按矩形逐列读。正确做法是先按 rail fence 的行号序列 `0,1,2,1,0,1,2,1,...` 统计每行出现多少次，按这个次数把密文切成三段，再沿行号序列逐字符取回。首行和末行的长度一般和中间行不一样。

```text
RBH{th3_sh4d0w_n3v3r_l13s_th3_w4ll_d03s}
```

模减法后，按轨道收集的文本应切成 **10、20、10** 字节。这来自 40 个位置的锯齿行号计数，不能平均切分：

```text
rail 0: Rts03_s3l0
rail 1: B{h_hdwnvrl3_h_4ld3}
rail 2: H34_31tw_s
```

## 回编码确认

把明文按上面的规则重新走一遍：按三轨收集 → 加回循环密钥（mod 256）→ 映射回自定义 hex 表，结果必须与原始密文逐字符相同。

字符表和镜像词都有题面依据，但「模 256 加法 + rail fence」这个具体组合不是从故事里必然推出的，是靠完整输出和回编码确认的。复杂度 O(n)。

## 复现

```powershell
python src/solvers/the-cave-keeps-no-secrets/solve.py
```

[完整脚本](../../../src/solvers/the-cave-keeps-no-secrets/solve.py)，只依赖 Python 标准库。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
