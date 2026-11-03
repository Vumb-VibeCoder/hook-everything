# hook-everything

[![CI](https://github.com/Vumb-VibeCoder/hook-everything/actions/workflows/ci.yml/badge.svg)](https://github.com/Vumb-VibeCoder/hook-everything/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-5.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Skills](https://img.shields.io/badge/skills-12-orange)

Skills that help an AI assistant write copy people actually want to read, and design flows people actually want to finish. It also ships a small scanner that tells you when a text sounds like a machine wrote it.

The one rule: a hook must survive the second look. When readers see how a page was built, they should respect the craft, not feel tricked.

## Quickstart (2 minutes)

**1. Install the skills**

```bash
git clone https://github.com/Vumb-VibeCoder/hook-everything.git
cd hook-everything

# Claude Code
mkdir -p .claude/skills .claude/tools
cp -r skills/* .claude/skills/
cp -r tools/* .claude/tools/
```

For Cursor, Windsurf, Codex or other agents, copy `AGENTS.md` into your project root (or append it to `.cursorrules` / `CLAUDE.md`) and keep `skills/` and `tools/` in the workspace.

**2. Ask your assistant**

```text
Rewrite this product announcement so it sounds human, then check it with the scanner.
```

**3. Check any text yourself**

```bash
python3 tools/slop_scan.py draft.txt --fix-hints
```

You get a score from 0 to 100 and a list of what to rewrite. Aim for 15 or lower. Needs Python 3.10+ and nothing else.

## Which skills does my task need?

| I want to... | Skills (in order) |
|---|---|
| Humanize or clean up a text in any language | `anti-slop` → `value-check` |
| Write a short email, release note or headline | `writing-hooks` → `anti-slop` → `value-check` |
| Write an essay, article or newsletter | `audience-calibration` → `trust-architecture` → `hook-compounding` → `writing-hooks` → `anti-slop` → `value-check` |
| Build a landing page, ad or outreach sequence | `market-intelligence` → `audience-calibration` → `trust-architecture` → `hook-compounding` → `marketing-hooks` → `visual-ux-hooks` → `anti-slop` → `value-check` |
| Design onboarding or a product flow | `psychology-map` → `trust-architecture` → `visual-ux-hooks` → `hook-compounding` → `product-hooks` → `value-check` |
| Find fresh angles and ideas | `market-intelligence` → `creative-ideation` → `hook-compounding` → `anti-slop` → `value-check` |

Short edits use the **Lite Lane** (2 to 3 skills). Campaigns and new products use the **Full Lane**. Details are in `AGENTS.md`.

## The 12 skills

| Skill | What it does |
|---|---|
| `psychology-map` | 30 behavior mechanisms, each rated by evidence strength |
| `trust-architecture` | Builds trust before asking for anything |
| `market-intelligence` | Reads live reviews and competitor gaps, and drops forced trend-jacking |
| `audience-calibration` | Matches speed, tone and proof to the reader |
| `creative-ideation` | Throws out the first obvious ideas and combines unrelated ones |
| `hook-compounding` | Layers 3 to 4 mechanisms into one hook |
| `visual-ux-hooks` | Layout, contrast, choice limits and response timing |
| `marketing-hooks` | Conversion copy without fake urgency or inflated claims |
| `writing-hooks` | Openers and mid-article retention |
| `product-hooks` | Onboarding, habits and humane offboarding |
| `anti-slop` | 85 rules for natural, non-hype writing |
| `value-check` | 12-point ethics and quality gate before you ship |

## Scanner cheatsheet

```bash
# Score a file and get rewrite hints
python3 tools/slop_scan.py draft.txt --fix-hints

# Scan a doc that quotes banned phrases on purpose
python3 tools/slop_scan.py skills/anti-slop/SKILL.md --strip-markdown

# Fail a CI job when the score is above 15
python3 tools/slop_scan.py README.md --max-score 15

# JSON output, or run the built-in tests
python3 tools/slop_scan.py draft.txt --json
python3 tools/slop_scan.py --selftest
```

The 15-point threshold is a working heuristic for dense clusters of AI and marketing tropes. It does not prove who wrote a text.

## Repository layout

```text
hook-everything/
├── AGENTS.md        # Routing rules for agents
├── SKILL.md         # Root skill manifest
├── skills/          # The 12 skills
├── tools/           # slop_scan.py
├── tests/           # unittest suite
├── research/        # Sources and evidence ratings
└── examples/        # Before/after rewrites
```

## Contributing

Run the checks before a pull request:

```bash
python3 tools/slop_scan.py --selftest
python3 -m unittest discover -s tests
```

See `CHANGELOG.md` for version history. Licensed under MIT.
