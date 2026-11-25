# Harbor Bean Co.: an AI company that runs itself (Paperclip tutorial)

Companion code for the video **"Let's Build an AI Company That Runs Itself (Paperclip Tutorial)"**.

[Paperclip](https://paperclip.ing) (open source, MIT) runs a *company* of AI agents on your own machine: a goal, an org chart, tickets, plan approval, budgets, and a pause button. In this demo a CEO, a Writer and a Developer build a one-page landing site for **Harbor Bean Co.**, a made-up coffee roaster. Everything stays local: no deploys, no domains, no email.

## What's here

| Path | What it is |
| --- | --- |
| `goal.md` | The company goal |
| `brand/harbor-bean.md` | Brand brief the agents work from |
| `agents/ceo.md`, `agents/writer.md`, `agents/developer.md` | Each agent's instructions (`AGENTS.md`) |
| `scripts/setup_company.py` | Creates secrets, budgets, goal, project and agents through the local Paperclip API |
| `safety-checklist.md` | Run this before you press **Run now** |
| `examples/harbor-bean-site/` | The actual files the agents produced in the recorded run |

## Quick start

```bash
# 1) Install and start Paperclip locally (dashboard on http://127.0.0.1:3100)
PAPERCLIP_TELEMETRY_DISABLED=1 npx paperclipai onboard --yes

# 2) In the dashboard, create the company "Harbor Bean Co." (the wizard), then:
mkdir -p ~/harbor-bean-workspace && cp brand/harbor-bean.md ~/harbor-bean-workspace/
export HARBOR_WORKSPACE=~/harbor-bean-workspace
export GEMINI_API_KEY=...        # free key from Google AI Studio
export ANTHROPIC_API_KEY=...     # optional: for the CEO (and Developer with DEV_ON_ANTHROPIC=1)
python3 scripts/setup_company.py # never prints your keys; ids go to scripts/state.json (git-ignored)

# 3) Create one task for the CEO in Plan mode, approve the plan, and watch the tickets.
# 4) When done: pause every agent.
```

Requires Node.js 20+, Python 3.10+, the Gemini CLI (`npm i -g @google/gemini-cli`) for the Gemini agents, and Claude Code for the Anthropic agent.

## Models used in the video

| Agent | Model | How |
| --- | --- | --- |
| CEO | `claude-haiku-5-5` | Paperclip Runner with Claude Code, own Anthropic key. **Pin the model**: a blank model resolves to a much pricier one. |
| Writer | `gemini-3.5-flash-lite` | Gemini CLI engine, free tier |
| Developer | `gemini-3-flash-preview`, then `claude-haiku-5-5` | Started free; switched to Haiku when its free daily quota ran out during review |

Gemini agents also need `GEMINI_CLI_TRUST_WORKSPACE=true` in their env, or the CLI refuses to run in the workspace.

## Real results from the recorded run (25 Nov 2026)

- Paperclip **v2026.1117.0**, local mode on 127.0.0.1.
- **7 tickets, all done**: HAR-1 plan (CEO), HAR-2 copy (Writer), HAR-3 page (Developer), and **HAR-4 to HAR-7, fix tickets the CEO opened on its own** after reviewing the work (remove invented facts, fix WCAG AA colour contrast, re-sync copy).
- **22 agent runs**: 14 succeeded, 7 failed, 1 cancelled. The failures were 4 free-tier quota limits and 3 setup mistakes, all kept in the run log.
- The CEO's plan took **25 s**; the Writer's first copy took **21 s**. About **23 minutes** from the plan run to the CEO's final review.
- The finished page is in `examples/harbor-bean-site/`. It makes no network requests, and the form never submits anywhere.

### Costs: read this before you trust the dashboard

Paperclip's Costs page showed **$0.00 with "19 run costs unavailable"**. It had no price for the models used, so every event was *unpriced*, and the $5 company cap could not count them.

Real token use reported by Paperclip:

| Model | Runs | Input | Cached input | Output |
| --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 7 | 197,330 | 3,189,803 | 50,682 |
| gemini-3.5-flash-lite (free) | 6 | 255,602 | 603,768 | 18,987 |
| gemini-3-flash-preview (free) | 3 | 251,423 | 276,794 | 19,332 |
| gemini-3.6-flash (free) | 1 | 58,060 | 286,269 | 2,073 |

At Anthropic's list prices for Haiku 5.5 ($0.10 in / $0.01 cache read / $0.50 out per million tokens for prompts up to 100k tokens, five times that above 100k), the Haiku usage works out to between about **$0.08 and $0.41**. This is a calculation from the token counts, not a bill. Your provider's billing page is the source of truth.

### Two gotchas

1. **Free usage trips the budget at $0.00.** Budgets default to `unpricedUsagePolicy: "block"`. Free Gemini usage is unpriced, so the first free run paused the whole company with nothing spent. `setup_company.py` sets `"allow"`; the dollar caps still apply to priced usage.
2. **The Gemini free tier runs out fast.** About 5 requests a minute and 20 a day per model on 25 Nov 2026, and one agent run makes many requests. Give the busiest agent (the CEO) a cheap paid model, or spread agents across different free models.

## Safety

- Run it on `127.0.0.1` only. Don't install deploy, email or chat connectors for this demo.
- Keep keys in Paperclip secrets. Never commit `.env` or `scripts/state.json`.
- Pause every agent when you are done.

## License

MIT
