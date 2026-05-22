# Knowlyx

**Cognitive enforcement layer for AI software development.**

AI coding tools generate code fast — but they don't understand your system. They duplicate utilities, ignore conventions, miss cross-service impact, and hallucinate imports. Knowlyx makes AI agents *understand* your codebase before they touch it.

> Knowledge is passive. Cognition must be enforced.

[![PyPI](https://img.shields.io/pypi/v/knowlyx)](https://pypi.org/project/knowlyx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

- [What it does](#what-it-does)
- [Install (pick one)](#install-pick-one)
- [Connect your AI assistant](#connect-your-ai-assistant)
- [5-minute first session](#5-minute-first-session)
- [Multi-repo workspace setup](#multi-repo-workspace-setup)
- [Share knowledge with team via git](#share-knowledge-with-team-via-git)
- [Daily workflow](#daily-workflow)
- [Why Knowlyx](#why-knowlyx)
- [How does it work](#how-does-it-work)
- [Roadmap & docs](#roadmap--docs)

---

## What it does

When you ask Claude *"add password reset flow"*, Knowlyx intercepts and returns:

```text
Domain:    auth (CRITICAL)
Decision:  WARN — follow required workflow before proceeding

Impact:    auth-service, notification-worker, audit-log
Cascade:   account enumeration, email bombing, token replay

Reuse:     EmailTemplate.tsx, useRateLimit hook, AuditLogger
Memory:    "Team uses SendGrid + SES fallback" (approved by alice@co 2 weeks ago)
           [3 more entries auto-synthesized by AI into common themes]

Workflow:
  1. Single-use token (15 min expiry)
  2. Rate limit per email + per IP
  3. Audit log every step
  4. Integration test with mock SMTP

Risk policy: Knowlyx decision is authoritative. You may UPGRADE risk
based on context. You may NEVER downgrade.
```

Claude reads this through MCP — it can't skip it. Result: first-try correct code.

---

## Install (pick one)

### One-line installer

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/knowlyx/knowlyx/main/install.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/knowlyx/knowlyx/main/install.ps1 | iex
```

### One-line installer + workspace + Claude Code in one shot

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/knowlyx/knowlyx/main/install.sh \
  | bash -s -- --workspace my-product --claude --repo .
```

**Windows:**

```powershell
$env:KNOWLYX_WORKSPACE="my-product"; $env:KNOWLYX_CLAUDE="1"
irm https://raw.githubusercontent.com/knowlyx/knowlyx/main/install.ps1 | iex
```

### Manual install (if you prefer)

```bash
# Option A — uv tool (recommended, isolates the install)
uv tool install knowlyx

# Option B — pipx
pipx install knowlyx

# Option C — uvx (no install, runs on demand)
uvx knowlyx --version
```

Requires Python 3.11+. The installer will install `uv` for you if it's missing.

---

## Connect your AI assistant

### Claude Code (one-liner)

```bash
claude mcp add knowlyx -- uvx knowlyx mcp --repo .
```

Verify:

```bash
claude mcp list
# → knowlyx ✓
```

### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "knowlyx": {
      "command": "uvx",
      "args": ["knowlyx", "mcp", "--repo", "."]
    }
  }
}
```

Restart Cursor.

### Cline (VS Code)

VS Code Settings → search "cline mcp" → add:

```json
{
  "cline.mcpServers": {
    "knowlyx": {
      "command": "uvx",
      "args": ["knowlyx", "mcp", "--repo", "."]
    }
  }
}
```

### Continue.dev

Edit `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uvx",
          "args": ["knowlyx", "mcp", "--repo", "."]
        }
      }
    ]
  }
}
```

### Windsurf / Zed / Codex

Any MCP-compatible client — same JSON pattern:

```json
{ "command": "uvx", "args": ["knowlyx", "mcp", "--repo", "."] }
```

### No AI assistant — just CLI

```bash
knowlyx scan .
knowlyx analyze "add password reset" --repo .
```

Knowlyx works standalone too — useful as a code review checklist and team decision log.

---

## 5-minute first session

```bash
# 1. Verify install
knowlyx --version

# 2. Scan your project (3 sec → mental model)
cd /path/to/your/project
knowlyx scan .

# 3. Run a cognition request
knowlyx analyze "add rate limiting to /login" --repo .

# 4. (Optional) Save a team decision
knowlyx memory decide auth \
  "Rate limit /login" \
  --body "5 attempts per email per 15min, plus 20 attempts per IP per hour. Use Redis sliding window."

# 5. Verify Claude/Cursor picks it up
# In Claude Code: type "rate limit login" and watch it call analyze_intent + recall_context
```

---

## Multi-repo workspace setup

Real products span multiple repos (api, web, mobile, worker, admin). Knowlyx tracks them as a single **workspace** with shared memory.

### Tech lead (once)

```bash
# 1. Create the central workspace
knowlyx workspace create my-product

# 2. Edit topology
# macOS/Linux:
$EDITOR ~/.knowlyx/workspaces/my-product/workspace.toml
# Windows:
notepad $env:USERPROFILE\.knowlyx\workspaces\my-product\workspace.toml
```

Paste:

```toml
name = "my-product"

[[repos]]
name = "api"
path = "../code/api"
role = "backend"
domains = ["billing", "auth"]
critical = true

[[repos]]
name = "web"
path = "../code/web"
role = "frontend"
domains = ["checkout"]

[[repos]]
name = "worker"
path = "../code/worker"
role = "worker"

[[dependencies]]
from = "web"
to = "api"
type = "api"

[[dependencies]]
from = "worker"
to = "api"
type = "event"
```

### Each developer (per repo)

```bash
cd ~/code/api
knowlyx init --link my-product
# auto-detects role + domains from package.json/pyproject.toml/etc
# writes .knowlyx/config.toml — commit this to git
git add .knowlyx/config.toml
git commit -m "link to knowlyx workspace"
```

Now every dev who clones `api` is automatically connected to `my-product`'s shared memory.

---

## Share knowledge with team via git

`~/.knowlyx/workspaces/my-product/` is just a folder of JSON + TOML. Push it to GitHub / GitLab / self-hosted — no infra needed.

### Tech lead — git init + push

```bash
# 1. Init git in the workspace folder
knowlyx sync init \
  --workspace my-product \
  --remote git@github.com:your-org/my-product-knowledge.git

# 2. Push
knowlyx sync push --workspace my-product -m "init"
```

### Each developer — clone shared knowledge

```bash
# Clone the shared knowledge to the expected path
git clone git@github.com:your-org/my-product-knowledge.git \
  ~/.knowlyx/workspaces/my-product

# That's it. The .knowlyx/config.toml in each repo points here.
```

Auth: uses your existing git auth (SSH key / HTTPS credential helper / `gh auth`). No Knowlyx-specific tokens needed.

Full setup including self-hosted GitLab, conflict resolution, and permissions: **[docs/git-sync.md](docs/git-sync.md)**

---

## Daily workflow

```bash
# Pull latest decisions before starting
knowlyx sync pull --workspace my-product

# Work normally — Claude/Cursor calls Knowlyx tools automatically.
# When you make important decisions, save them:
knowlyx memory decide billing \
  "Use Stripe for subscriptions" \
  --body "Stripe Billing for B2C, manual invoice for B2B over \$10k"

# Push at end of day
knowlyx sync push --workspace my-product -m "decisions from billing redesign"
```

Recommended aliases (`.bashrc` / `.zshrc`):

```bash
alias kw-pull='knowlyx sync pull --workspace my-product'
alias kw-push='knowlyx sync push --workspace my-product'
alias kw='knowlyx'
```

---

## Why Knowlyx

| Pain that every team has | Knowlyx solution |
|---|---|
| "We already have a helper for that" — duplicate utils | `get_reusable_assets` injects existing code |
| AI ignores CLAUDE.md / .cursorrules | MCP tool result — AI trusts tools more than markdown |
| Migration breaks downstream services | `get_cross_repo_impact` shows blast radius |
| AI hallucinates imports/functions | `validate_generated_code` blocks before write |
| Refactor misses call sites | `get_impact_analysis` lists every caller |
| 2-week onboarding for new devs | `scan + graph` = 5-min mental model |
| Silent API contract breakage | Risk gate + deprecation workflow |
| AI re-invents same decision team made last month | `get_domain_knowledge` + cached AI synthesis |

---

## How does it work

**No LLM inside Knowlyx — by design.** Knowlyx is 100% rule-based + pattern matching + graph algorithms. Deterministic, fast, free, offline, auditable.

The intelligence comes from Claude (or whatever AI you use): Knowlyx hands Claude **structured cognition data** through MCP, Claude does the reasoning and writing.

For tasks that need judgment (summarizing related memory, weighing historical risk):

- Knowlyx returns raw data + instructions
- Your AI agent does the synthesis
- Knowlyx caches the result so future sessions don't re-do it

Risk decisions follow the **upgrade-only** rule: Claude can make Knowlyx's decision stricter (`proceed` → `warn` → `ask` → `reject`), but never looser.

```text
┌─────────────────────────────────────────────────┐
│  AI Agent (Claude / Cursor / Cline / Codex)     │
└──────────────────┬──────────────────────────────┘
                   │ MCP protocol — 25 tools
┌──────────────────▼──────────────────────────────┐
│  ENFORCEMENT — analyze_intent, get_conventions, │
│  validate_generated_code, get_domain_knowledge, │
│  save_synthesis, assess_risk_in_context, …      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  REASONING — Intent → Impact → Risk → Decision  │
│  (rule-based, deterministic, no LLM)            │
└──────────────────┬──────────────────────────────┘
                   │
       ┌───────────┼───────────────────┐
       ▼           ▼                   ▼
┌──────────┐ ┌──────────┐         ┌──────────┐
│  GRAPH   │ │  MEMORY  │         │  PACKS   │
│ NetworkX │ │  v2 sch  │         │ 7 built  │
│ cascade  │ │ +synth   │         │   -in    │
└────┬─────┘ └──────────┘         └──────────┘
     │
┌────▼────────────────────────────────────────────┐
│  SCANNER — language/framework/architecture/     │
│  domains/conventions/reusable assets            │
└─────────────────────────────────────────────────┘
```

---

## Roadmap & docs

- **[ROADMAP.md](ROADMAP.md)** — versions + what's next
- **[CHANGELOG.md](CHANGELOG.md)** — every release
- **[docs/quickstart.md](docs/quickstart.md)** — 5-minute first session
- **[docs/cli.md](docs/cli.md)** — every CLI command
- **[docs/mcp.md](docs/mcp.md)** — MCP integration details
- **[docs/architecture.md](docs/architecture.md)** — 6 layers explained
- **[docs/multi-repo.md](docs/multi-repo.md)** — `knowlyx.toml` + cross-repo impact
- **[docs/distributed-knowledge.md](docs/distributed-knowledge.md)** — central store + per-repo link
- **[docs/git-sync.md](docs/git-sync.md)** — share workspace via GitHub/GitLab (full step-by-step)
- **[docs/usage-examples.md](docs/usage-examples.md)** — 7 real-world scenarios
- **[docs/cognition-packs.md](docs/cognition-packs.md)** — built-in domain knowledge

## Contribute

PRs welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

```bash
git clone https://github.com/knowlyx/knowlyx
cd knowlyx
uv sync --extra dev
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).


PRs welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

```bash
git clone https://github.com/knowlyx/knowlyx
cd knowlyx
uv sync --extra dev
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
