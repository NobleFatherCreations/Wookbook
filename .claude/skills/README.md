# Project skills

Same principle as `.claude/agents/`: these live in the repo so they're
available automatically in any future session, no install step.

| Skill | Invoke with | What it does |
|---|---|---|
| `impeccable` | `/impeccable <command> <target>` or just describe the design task | Design/UX skill — 23 sub-commands (`critique`, `audit`, `polish`, `bolder`, `quieter`, `animate`, `layout`, etc). This is the actual source of the "impeccable" skill referenced in `BOOKS.md`/the review package. Apache 2.0, inspected: minimal disclosed telemetry (an opt-out-able anonymous "choice ping"), no daemon. **Partially wired**: the reference docs (what makes it useful) work as-is; the deterministic `detect.mjs`/`live` browser-iteration scripts need `npm install` run inside `.claude/skills/impeccable/scripts/` first — not done yet, since it pulls in dependencies (css-tree, htmlparser2, marked, etc.) that haven't been vetted for this repo yet. |
| `grill-me` | `/grill-me` | Stateless planning interview — walks a plan/design as a decision tree, one question at a time. |
| `ponytail` | `/ponytail`, or just describe a coding task | Forces the simplest solution — YAGNI-first, stdlib/native before dependencies. |
| `ponytail-review` | `/ponytail-review` | Reviews a diff for over-engineering only (not correctness/security). |
| `ponytail-audit` | `/ponytail-audit` | Same, but whole-repo instead of a diff. |
| `ponytail-help` | `/ponytail-help` | Quick reference for all ponytail commands. |
| `ponytail-debt` | `/ponytail-debt` | Harvests `ponytail:` comments left in code into a debt ledger. |
| `ponytail-gain` | `/ponytail-gain` | Shows ponytail's benchmarked impact (less code, cost, time). |

## Vendored from skills.sh (2026-10-22, copied by hand to avoid the skills CLI's install telemetry; markdown only, no scripts/hooks)

| skill | source | commit |
|---|---|---|
| site-architecture | coreyhaines31/marketingskills | e85f3cb |
| copy-editing | coreyhaines31/marketingskills | e85f3cb |
| ux-heuristics | wondelai/skills | c172996 |
| refactoring-ui | wondelai/skills | c172996 |
| frontend-design | anthropics/skills | dbd4588 |
| web-design-guidelines | vercel-labs/agent-skills | 063bee9 |
| better-accessibility | jakubkrehel/skills | 4c66b1f |
| web-accessibility | addyosmani/web-quality-skills | afa8da9 |
| web-perf | cloudflare/skills | 86505e4 |
