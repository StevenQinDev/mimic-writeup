# Perpetual Leak

[English](README.en.md) · Mimic CTF 2026 · Misc · 300 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Misc | 300 | PGN 与密文 | 棋盘坐标位打包与 XOR |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-perpetual-leak)

棋盘有 64 个格子，正好能用 6 位编号。这题就是吃这一条：每一步棋贡献起点和终点两个 6 位，拼起来当密钥流用。

## 别把 SAN 文本当密钥

`chess_moves.txt` 是 PGN 的 movetext。最直接的做法是把文本本身哈希一下或异或——但题面说的是秘密「下出来的」，重在走法，不在字符串。

所以要用 `python-chess` 把着法解析成合法着法对象，取方格编号。库的编号是 a1=0、b1=1、……、h8=63。

每步按起点、终点顺序贡献 12 位：

```python
bits += f'{move.from_square:06b}{move.to_square:06b}'
```

## 位对齐是这题的核心

78 个半回合足够提供 936 位，密文 53 字节只需要 424 位，多出来的部分不用。位流按 MSB 优先每 8 位切一个字节。

最容易错的地方是每步写几个字节：

```python
# 错：每步占 16 位，整个流从第一步就错位
key = b''.join(bytes([m.from_square, m.to_square]) for m in moves)
```

起点和终点各 6 位，合起来 12 位，**不是两个完整字节**。写成 `bytes([...])` 每步占 16 位，后面全部对不上。

重复局面不会被编码规则排除。密文只有 53 字节，所以仅消耗前 424 位密钥流，前 36 个半回合已足够提供这些位。

## 解密

`P_i = C_i XOR K_i`：

```text
RBH{p3rp3tu4l_ch3ck_c4nt_h1d3_th3_k3y_1n_th3_squ4r3s}
```

## 校验的意义有限，要看清

`python-chess` 能回放整局，检查每个着法在对应局面中合法；这只能验证回放，不能证明棋谱的真实性。

但 XOR 回算**不能**证明密钥是对的：任何密钥做完 XOR 再 XOR 都能还原，这是自反性，不是证据。真正支持这个模型的是两件事：棋谱到方格编号的映射有明确依据，以及解出来的全部 53 字节都落在可读的 flag 上，而不是只有前缀对。

复杂度随步数和密文长度线性增长。

## 如何发现打包方式

密文前四字节 XOR `RBH{` 得到候选密钥前缀 `31cd2419`。按 a1=0 编号，`e2e4` 编为 `(12 << 6) | 28 = 0x31c`，`e7e5` 为 `0xd24`，`g1f3` 为 `0x195`。拼接 12 位数据 `31c d24 195` 后，前四字节恰为 `31 cd 24 19`，把已知前缀与棋格打包假设联系起来。

## 复现

```powershell
python src/solvers/perpetual-leak/solve.py
```

[完整脚本](../../../src/solvers/perpetual-leak/solve.py)。依赖 `chess`。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
