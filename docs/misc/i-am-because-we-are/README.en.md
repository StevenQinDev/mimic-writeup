# I Am Because We Are

[中文](README.zh-CN.md) · Mimic CTF 2026 · Misc · 50 points · [Challenge page](https://ctf.rarebytehub.com/events/mimic/writeups/challenge/i-am-because-we-are-2)

| Category | Points | Input | Result |
|---|---:|---|---|
| Misc | 50 | Telegram group access | Membership verification |

[Original prompt and attachments](PROMPT.md) · [Official solution](https://ctf.rarebytehub.com/events/mimic/writeups/official-solution-i-am-because-we-are) · [Event links](../../OFFICIAL-LINKS.md)

This is a Telegram membership task. It has no attachment or encoding layer.

## Verification flow

1. Join the [Rare Byte Hub group](https://t.me/rarebytehub).
2. Open a private chat with [@iambecausewearebot](https://t.me/iambecausewearebot).
3. Press **Start** (or send `/start`) to open the bot's menu.
4. Press **I've Joined - Verify Me** and read the bot's response.

## Recorded result

The flag recorded in this collection is:

```text
RBH{n0_0n3_3x1sts_4l0n3}
```

## Evidence limit

The official article confirms the group, bot, Start action and verification button, but does not print a flag. It therefore corroborates the workflow, not this stored flag value. The interface does not establish the bot's internal API calls.

This task requires the event-time Telegram resources. There is no offline solver, and no bot interaction is performed by this repository's test suite.

[Reproducibility guide](../../REPRODUCIBILITY.md) · [Source and license](../../ABOUT.md)
