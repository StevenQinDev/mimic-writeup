# The King and the Beggar

[English](README.en.md) · Mimic CTF 2026 · Crypto · 100 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Crypto | 100 | 72 字符密文 | 大小写互换、Base64、XOR |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-king-and-the-beggar)

这题的陷阱在第一步：题面给的 72 个字符完全落在 Base64 字符集里，直接 `b64decode` 也不会报错。所以「能解码」什么都证明不了——真正的信号是解出来的东西长得像什么。

```text
ytq0mge1mZa0ndG2ndbMntm0ody0ngu0mZaZndq0odyWntK1nJbMntm0nZa5nwm0zJC1nZu2
```

## 高低互换，两处都要动

题面讲国王和乞丐交换位置，反复提「高低互换」。这个词有两层可以落地的地方：

- 字母层面：大小写互换（`swapcase`）
- 数据层面：半字节（nibble）互换

先只做第一层。把上面这串做大小写互换再 Base64 解码，得到 54 个十六进制字符：

```text
a440a530448640f5348644e430344486059560f5347095c4f75756
```

不是可读文本，但长度是 54，正好是偶数，也就是 27 字节——这不太像巧合。

第二层是要不要交换半字节、要不要反序。设两个相邻字节写作 `ab cd`（每个字母代表一个半字节）。交换半字节得 `ba dc`，再反转字节顺序得 `dc ba`。而直接反转十六进制**字符串** `abcd` 得到 `dcba`——两者结果完全一样。所以可以用一行完成两件事：

```python
h = base64.b64decode(s.swapcase(), validate=True).decode('ascii')
c = bytes.fromhex(h[::-1])
```

`[::-1]` 必须作用在十六进制文本上，不能作用在 `bytes.fromhex()` 之后的结果上，那样只会反转字节、不会交换半字节。

## 0x37 是算出来的，不是猜出来的

变换后前四字节是 `65 75 7f 4c`。假设最后一层是循环单字节 XOR，flag 前缀已知为 `RBH{`，那就四个位置各算一次：

| 位置 | 当前字节 | 已知明文字节 | 异或结果 |
|---|---|---|---|
| 0 | `65` | `52`（R） | `37` |
| 1 | `75` | `42`（B） | `37` |
| 2 | `7f` | `48`（H） | `37` |
| 3 | `4c` | `7b`（{） | `37` |

四个位置同一个值，才说明单字节 XOR 这个模型站得住。脚本把「候选集合大小为 1」写成断言，而不是把 `0x37` 硬编码进去：

```python
keys = {a ^ b for a, b in zip(c, b'RBH{')}
assert len(keys) == 1
k = keys.pop()
p = bytes(x ^ k for x in c)
```

```text
RBH{n0th1ng_st4ys_th3_s4m3}
```

四个位置支持这些位置使用相同密钥，但较长密钥也可能有相同前缀，不能据此证明后续密钥字节全部相同。完整明文与回编码用于检查所选模型的一致性。

## 回编码才是终点

XOR 是自反的，这让整条链可以倒着走一遍：明文 XOR 密钥 → 转十六进制文本 → 逆序 → Base64 编码 → 大小写互换，必须逐字符回到最初那 72 个字符。

```python
assert base64.b64encode(
    bytes(x ^ k for x in p).hex()[::-1].encode()
).decode().swapcase() == s
```

这一步同时锁住了变换方向、顺序和输入完整性。任何一环搞反，字符串都对不上。

## 复现

只需要 Python 标准库：

```powershell
python src/solvers/the-king-and-the-beggar/solve.py
```

[完整脚本](../../../src/solvers/the-king-and-the-beggar/solve.py) 里存着题面输入，不依赖当前目录或网络。正常输出包含解出的十六进制文本、`key: 0x37` 和 flag。注意 `python -O` 会关掉断言，那样校验就形同虚设。

## 说明与署名

- 题面数据必须逐字使用，改一个字符结果就变。
- `0x37` 由已知前缀算出，并由完整逆变换和回编码共同校验。
- 密钥推导的讲述方式参考了 [DebajyotiRay 的 Mimic writeup](https://github.com/DebajyotiRay/mimic-ctf-writeup)。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
