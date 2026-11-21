# The Clockmaker’s Vault

[English](README.en.md) · Mimic CTF 2026 · Reverse · 300 分

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Reverse | 300 | ELF | VM 约束与 Z3 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-the-clockmaker-s-vault)


附件用 53 条指令、8 个字节寄存器和 256 字节内存实现了一个 VM。静态解码后，校验只剩两轮循环移位与 XOR。下面保留 Z3 方法，并增加独立的短循环枚举方法。

## 恢复指令和内存布局

调度器虚拟地址为 `0x1210`。本附件在文件偏移 `0x21e0` 保存 53 条四字节指令 `(op,a,c,pad)`。按指令下标 `pc` 先还原操作码：

```python
op ^= (pc * 0x35 + 0x11) & 255
```

内存 `0..31` 为输入，`96..127` 为目标，`128..131` 为四字节密钥。目标位于文件偏移 `0x22c0`，密钥在 `0x2004`，内容为 `a5 dc 13 4a`。虚拟地址与文件偏移是不同概念，不能因为本文件中部分数值相同就混用。

## 摊平校验公式

数组下标对 32 取模，字节旋转量对 8 取模：

```text
y[i] = rol8(x[i] XOR key[i & 3], i) XOR x[(i + 7) & 31]
target[i] = y[i] XOR rol8(y[(i + 13) & 31], 3)
```

字节间依赖使我们不能无条件地单独求出某个字节，但并不意味着无法求逆：猜一个起点，就能沿整个依赖环传播。

## 方法一：位向量约束

[Z3 脚本](../../../src/solvers/clockmakers-vault/solve.py) 建立 32 个八位变量，加入两轮等式，并限定为可打印 ASCII、前缀 `RBH{` 和末尾 `}`。定宽运算与 VM 的字节语义一致，得到：

```text
RBH{cl0ckmaker_hid_a_vm_in_here}
```

独立的逐指令模拟器再验证解出的输入。带符号跳转相对于已经递增的指令计数器计算。正确输入在 1510 步后通过，翻转首字节则被拒绝。加入排除当前答案的子句后 Z3 返回 unsat，说明答案**在这些可打印 flag 约束内唯一**。

## 方法二：不用 SMT，沿依赖环求解

第二轮改写为：

```text
y[(i+13)&31] = ror8(y[i] XOR target[i], 3)
```

枚举 `y[0]` 的 256 种值。因为 `gcd(13,32)=1`，每次加 13 会遍历全部下标。传播 31 步后检查闭环等式。随后枚举 `x[0]`，第一轮改写为：

```text
x[(i+7)&31] = y[i] XOR rol8(x[i] XOR key[i&3], i)
```

`gcd(7,32)=1`，同样遍历全部下标并检查闭环。[标准库脚本](../../../src/solvers/clockmakers-vault/solve_cycles.py) 独立枚举得到 **65,536 个原始解、6 个全可打印解、1 个可打印的 `RBH{...}` flag**。这也说明不能把带格式约束的唯一性扩大为整个输入空间唯一。中间环恢复后，最多进行 256 × 256 × 32 次字节传播。

## 反调试密钥变化为什么抵消

`ptrace` 失败分支把四个密钥字节各 XOR `0x5a`。对任意共同掩码 `c`，第一轮增加 `rol8(c,i)`，第二轮增加：

```text
rol8(c,i) XOR rol8(c,i+13+3) = 0
```

旋转量相差 16，是 8 的倍数，两项相同而异或抵消。因此最终变换不受这种统一密钥变化影响。循环脚本对恢复的输入检查全部 256 种共同 XOR 掩码，均得到原目标。这是当前公式的性质，不能推广为反调试分支总可忽略。

## 复现

```powershell
python src/solvers/clockmakers-vault/solve.py
python src/solvers/clockmakers-vault/solve_cycles.py
```

第一条依赖 `z3-solver`，第二条只用标准库。两者均把 ELF 当作字节读取，不执行原程序。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
