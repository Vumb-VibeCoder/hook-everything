# hook-everything (v5.1)

An evidence-backed skill suite for AI coding, marketing, product, and writing assistants. It teaches agents how human attention, motivation, memory, visual perception, and **trust** work. It also shows how to research live market dynamics without forced trend-jacking, calibrate hooks to audience processing states, layer psychological hooks simultaneously, and write with natural human stylometry across any language (85 anti-slop and anti-hype rules).

The foundational rule is simple: **every hook must survive the second look.** When a reader or user realizes how a page, essay, or onboarding flow was built, they should respect the craft and feel the experience was worth their time, never that they were tricked or forced.

## What's New in v5.1

1. **Precision Scanner & CJK Support (`tools/slop_scan.py` v5.1)** normalizes curly quotes before matching, adds 16 missing English and European phrases plus Rule 58 CJK phrases, counts CJK tokens and `。！？` sentence boundaries, ignores em-dashes inside code blocks, distinguishes verb vs. noun uses of `leverage`, ignores number and calendar triads, catches multiline `While/Although` see-saw clauses, and adds `--strip-markdown` and `--max-score` flags across a 35-assertion self-test.
2. **Evidence Recalibration & 31-Row Source Table (`research/SOURCES.md`, `skills/psychology-map`)** maps each mechanism `M1` through `M30` to its own row with explicit `STRONG`, `MIXED`, and `WEAK` definitions, adding replication meta-analyses (Scheibehenne et al. 2010 on choice overload, Gal & Rucker 2018 on loss aversion, Burger 1999 on foot-in-the-door, Helmreich et al. 1970 on pratfall).
3. **CI Pipeline & Unit Test Suite (`.github/workflows/ci.yml`, `tests/test_slop_scan.py`)** runs automated self-tests, `unittest` checks, and `--max-score 15` gates on root documentation files.

## What's New in v5.0 (Core Suite Capabilities)

1. **Live Market & Competitive Intelligence with Organic Fit Gate (`skills/market-intelligence`)** teaches agents how to run a 4-layer live web market scan (Category/Pricing Shifts, 2-to-4 Star Verbatim VoC Mining, Competitor Blind-Spot Mapping, and Macro Tailwinds) paired with the **Organic Fit Gate**, a strict filter that blocks forced trend-jacking and only weaves market signals in when they are causally relevant.
2. **Audience Calibration & Cognitive Routing (`skills/audience-calibration`)** draws on the **Elaboration Likelihood Model (ELM - Petty & Cacioppo 1986)** and **Construal Level Theory (Trope & Liberman 2010)** to calibrate hook speed and proof type across 4 distinct mindsets (Skeptical Practitioner/Developer, Time-Poor Executive, Fast-Scrolling Consumer, and Peer Forum/Community).
3. **Visual, Spatial & Micro-Interaction Hooks (`skills/visual-ux-hooks`)** covers perceptual psychology before a single word is read, including the **Von Restorff Isolation Effect (1933)**, **Choice Overload & Hick's Law (Iyengar & Lepper 2000)**, **Eye-Tracking Skimmer Brakes & Caption Hooks**, and **Doherty Flow (<400ms) vs. Labor Perception (>1.5s)**.
4. **Expanded Writing & Product Lifecycle Playbooks (`skills/writing-hooks`, `skills/product-hooks`)** detail mid-article retention architecture (False Summit turns, 90/10 Socratic chains, word-count pacing) alongside Day-1 to Day-30 habit graduation, multiplayer network loops, and humane offboarding.
5. **85-Rule Anti-Slop & Anti-Scam Engine (`skills/anti-slop` + `tools/slop_scan.py` v5.1)** includes **Dimension 9 (Forced Trend-Jacking & Scam/Hype Marketing Tells)** to catch unnatural news-pegs, unverified ROI multipliers, guru-blueprint claims, and fake spot limits.

## Lite Lane vs. Full Lane Routing

Not every request needs the full 7-stage pipeline. As defined in `AGENTS.md`, use the **Lite Lane** (`writing-hooks` or `product-hooks` -> `anti-slop` -> `value-check`) for single-paragraph rewrites, release notes, or quick draft cleanup. Reserve the **Full Lane** (market scan, audience calibration, bisociation ideation, and 4-note chord compounding) for full landing pages, cold outreach sequences, new product onboarding flows, and long-form essays.

## Repository Structure (12 Specialized Skills)

```text
hook-everything/
├── AGENTS.md                              # Master routing (Lite & Full lanes).
├── SKILL.md                               # Unified root skill manifest.
├── README.md                              # Documentation and quickstart.
├── CHANGELOG.md                           # Version history.
├── VERSION                                # Semantic version (5.1.0).
├── LICENSE                                # MIT License.
├── .github/workflows/ci.yml               # Automated CI test & lint workflow.
├── tests/test_slop_scan.py                # Zero-dependency unittest suite.
├── skills/
│   ├── psychology-map/SKILL.md            # 30 mechanisms across 6 layers.
│   ├── trust-architecture/SKILL.md        # ABI trust model & inoculation.
│   ├── market-intelligence/SKILL.md       # Live VoC mining & Organic Fit Gate.
│   ├── audience-calibration/SKILL.md      # ELM routing & Construal calibration.
│   ├── creative-ideation/SKILL.md         # Graveyard pruning & Bisociation.
│   ├── hook-compounding/SKILL.md          # Layering 3-4 hooks (5 Chords).
│   ├── visual-ux-hooks/SKILL.md           # Isolation, Choice Overload & timing.
│   ├── marketing-hooks/SKILL.md           # Zero-scam conversion engine.
│   ├── writing-hooks/SKILL.md             # Openers, False-Summit & 90/10 gaps.
│   ├── product-hooks/SKILL.md             # Sandbox onboarding & habit loops.
│   ├── anti-slop/SKILL.md                 # 85 stylometric & anti-hype rules.
│   └── value-check/SKILL.md               # 12-point ethical & subtlety gate.
├── tools/
│   └── slop_scan.py                       # Stylometry & anti-hype scanner (v5.1).
├── research/
│   └── SOURCES.md                         # 31-row bibliography & rating key.
└── examples/
    └── before-after.md                    # 16 annotated transformations.
```

## Installation

### Claude Code / Standard Skill Directories
```bash
cp -r skills/* .claude/skills/
cp -r tools/ .claude/tools/
```

### Cursor / Windsurf / Codex / Custom Agents
Copy `AGENTS.md` to your project root (or append it to `.cursorrules` / `CLAUDE.md`) and keep `skills/` and `tools/` in the workspace.

## Using the v5.1 Dual Anti-Slop & Anti-Hype Scanner (`tools/slop_scan.py`)

Requires Python 3.10+ with zero external dependencies. Evaluates 18 stylometric, structural, syntactic, and multilingual indicators.

```bash
# Scan a file and output a 0-100 score + concrete rewrite instructions.
python3 tools/slop_scan.py draft.txt --fix-hints

# Scan reference or skill docs that intentionally quote banned phrases.
python3 tools/slop_scan.py skills/anti-slop/SKILL.md --strip-markdown

# Enforce a maximum score threshold in CI (exits 1 if score > 15).
python3 tools/slop_scan.py README.md --max-score 15

# Run built-in 35-assertion test suite.
python3 tools/slop_scan.py --selftest
```

### Calibration Note on Scanner Scores
The `<= 15/100` clean threshold is an unvalidated heuristic for catching dense clusters of AI and marketing tropes, not a psychometric authorship detector. Reference files in this repository (such as `skills/anti-slop/SKILL.md` and `examples/before-after.md`) intentionally list and quote hundreds of banned phrases and "Before" anti-patterns on purpose as negative examples. Always scan reference and skill files with `--strip-markdown` so quoted negative examples and code spans are excluded from the prose score.
