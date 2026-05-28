# Demo storyboard — the "STOP" moment

Goal: a 40–50s hero GIF for Product Hunt / README that lands one idea in the
first 5 seconds — **Precept stops an AI agent from breaking your codebase.**

Lead with the conflict (agent about to do the wrong thing), show Precept's
verdict, end with the agent doing the right thing. No setup, no narration.

---

## Storyboard (shot by shot)

| Time | On screen | Caption (lower third) |
| --- | --- | --- |
| 0:00 | Terminal prompt, clean repo | `Your AI agent is about to touch payments.` |
| 0:04 | Type: `precept analyze "add a refund endpoint to /payments"` | — |
| 0:08 | Decision banner renders: **ASK — Risk: HIGH** | `Precept reads the change before any code is written.` |
| 0:14 | `Reuse: PaymentClient, IdempotencyMiddleware` | `It already knows what to reuse.` |
| 0:20 | `Team rule: idempotency keys required (alice, approved)` | `…and what your team decided.` |
| 0:26 | `Cascade: refund → webhook → ledger` | `…and what this change will break.` |
| 0:32 | Cut to Claude Code: `/precept add a refund endpoint` → agent reuses `PaymentClient`, follows the rule, pauses for approval | `So the agent does it right — the first time.` |
| 0:42 | Logo + tagline | `Precept — the guardrail for your AI agent.` |

Keep the terminal font large (≥ 22pt), dark theme, no window chrome clutter.

---

## Option A — VHS (recommended, deterministic GIF)

[charmbracelet/vhs](https://github.com/charmbracelet/vhs) renders a GIF from a
script, so every take is identical. Save as `demo.tape` and run `vhs demo.tape`.

```tape
# demo.tape
Output demo.gif
Set FontSize 24
Set Width 1200
Set Height 700
Set Theme "Dracula"
Set TypingSpeed 60ms

Type "precept analyze 'add a refund endpoint to /payments'"
Sleep 800ms
Enter
Sleep 4s          # let the ASK / HIGH banner + reuse + risk render

Sleep 2s
Type "# Precept said ASK — so the agent reuses PaymentClient and waits for approval"
Sleep 2s
```

For the Claude Code half (0:32), record a second clip in Claude and stitch, or
screen-record the `/precept` reply and crop to the `Decision:` / `Reuse:` lines.

## Option B — asciinema (terminal-authentic)

```bash
asciinema rec demo.cast
# in the recording session:
precept analyze "add a refund endpoint to /payments"
exit
# convert to GIF with agg:
agg demo.cast demo.gif --font-size 24 --theme dracula
```

---

## Recording checklist

- Seed memory first so the `Team rule:` line is real, not empty:
  `precept memory decide payment "Use idempotency keys" --body "All payment calls require an idempotency key"`
- Run against a repo that actually has a `payment` domain + a `PaymentClient`
  asset, so `Reuse:` and `Cascade:` populate. Verify with `precept analyze … --json` first.
- Trim dead air. The banner should appear within 8s of pressing Enter.
- Export at ≤ 8 MB so it autoplays inline on GitHub and Product Hunt.

## Where it ships

- README: replace the static `assets/logo-full.png` hero with `demo.gif`.
- Product Hunt: first gallery item (the thumbnail that decides the click).
