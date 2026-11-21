# I Am Because We Are

[English](README.en.md) · Mimic CTF 2026 · Misc · 50 分 · [题目页面](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/i-am-because-we-are-2)

| 分类 | 分值 | 输入 | 结果 |
|---|---:|---|---|
| Misc | 50 | Telegram 群组访问 | 成员身份验证 |

[原题与附件](PROMPT.md) · [官方题解](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-i-am-because-we-are) · [赛事链接](../../OFFICIAL-LINKS.md)

这是一道 Telegram 成员验证题，没有附件或额外编码层。

## 验证流程

1. 加入 [Rare Byte Hub 群组](https://t.me/rarebytehub)。
2. 打开与 [@iambecausewearebot](https://t.me/iambecausewearebot) 的私聊。
3. 点击 **Start**（或发送 `/start`），打开机器人菜单。
4. 点击 **I've Joined - Verify Me**，读取返回结果。

## 记录结果

本文集记录的 flag 为：

```text
RBH{n0_0n3_3x1sts_4l0n3}
```

## 证据边界

官方文章确认了群组、机器人、Start 和验证按钮，但未展示 flag，因此它只交叉确认流程，不能独立确认这里保存的 flag 值。界面行为也不足以确定机器人内部调用哪个 API。

本题依赖赛事期间的 Telegram 资源，没有离线求解脚本；仓库测试不会操作机器人。

[复现指南](../../REPRODUCIBILITY.md) · [来源与许可](../../ABOUT.md)
