# GHOST IN THE GEARBOX

[English](README.en.md) · Mimic CTF 2026 · Reverse · 100 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Reverse | 100 | ELF | VM 字节码与 XOR |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-ghost-in-the-gearbox)

`ghost_gearbox.elf` 是 stripped 的 x86-64 ELF。它没有直接比较密码，而是把密码丢给一个小型 VM 去校验——所以逆向的对象不是 `main` 里的比较逻辑，是 VM 的指令集。

全程静态解析，不执行 ELF。

## 先定位三块东西

静态分析给出几个关键位置：

| 位置 | 内容 |
|---|---|
| `0x1199` | `main` |
| `0x12d3–0x12ff` | 解释器 |
| `0x22c0` | VM 程序，114 字节 |
| `0x22a0` | 输出表，27 字节 |

读这些地址时要注意一个坑：**虚拟地址不等于文件偏移**。脚本用 ELF 的 `.rodata` 起始地址做换算，而不是把地址直接当偏移用。

## 指令集只有五种

VM 的每条指令是两个字节 `(op, arg)`，但两个字节都先 XOR `0x5a`。还原之后：

| 原始操作码 | 解码后操作码 | 含义 |
|---|---|---|
| `6d` | `37` | 载入密码字节 |
| `f8` | `a2` | XOR |
| `06` | `5c` | 模 256 加法 |
| `cb` | `91` | 相等检查 |
| `5a` | `00` | 结束 |

每个密码位置用四条指令处理一遍，14 组加一个结束标记，正好 114 字节——和 VM 程序的长度对上。这个数字本身就是验证：如果指令分组错位，长度不会这么整齐。

## 反解一个字节

一组参数记作 X、A、C，执行顺序是：

```text
((p[i] XOR X) + A) mod 256 = C
```

两边倒推：

```text
p[i] = ((C - A) mod 256) XOR X
```

XOR 与模加法可逆，载入指令指定输入位置，比较指令给出目标，因此不需要搜索。脚本会检查操作码的排列和下标，从附件里读参数，恢复出：

```text
gh0st_1n_g34rs
```

长度是 14。这个数要算，不能靠眼看——`g34rs` 里数字和字母混排，数错一位后面全错。

## 拿密码解输出表

输出表 27 字节，第 i 字节和 `password[i mod 14]` 异或：

```text
RBH{th3_g34rbox_n3v3r_l13s}
```

脚本把每个恢复出的字节重新代回 VM 约束验证一遍。文中的地址和操作码都对应当前这个附件，换一个编译产物就不成立。

## 第一组实例

解码后字节为 `37 00 a2 1f 5c 8f 91 07`：载入字节 0，XOR `1f`，加 `8f`，与 `07` 比较。因此 `((0x07 - 0x8f) & 255) ^ 0x1f = 0x67`，即字母 `g`。

## 复现

```powershell
python src/solvers/ghost-in-the-gearbox/solve.py
```

[完整脚本](../../../src/solvers/ghost-in-the-gearbox/solve.py)。依赖 pyelftools。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
