# False-positive baseline (preliminary)

How often does `tools/slop_scan.py` flag text written by humans before LLMs? This is a first, small measurement. It is not yet enough to justify the 15/100 threshold.

## Method

- 15 Python Enhancement Proposals from `python/peps` (raw `.rst` files), all first published 2001-2017, so before LLM-written text existed. Later edits to the files are minor.
- Command: `python3 tools/slop_scan.py <file> --json`, default mode and `--strip-markdown`.
- Score = `score` field (0-100). Threshold under test: 15.

## Results

| File | Words | Default | `--strip-markdown` |
|---|---:|---:|---:|
| pep-0001 | 6341 | 14 | 14 |
| pep-0007 | 1122 | 33 | 34 |
| pep-0008 | 6886 | 42 | 42 |
| pep-0257 | 1496 | 14 | 15 |
| pep-0273 | 1275 | 6 | 6 |
| pep-0285 | 2336 | 12 | 12 |
| pep-0289 | 1506 | 13 | 13 |
| pep-0318 | 4394 | 21 | 28 |
| pep-0333 | 10235 | 54 | 54 |
| pep-0343 | 4835 | 26 | 19 |
| pep-0380 | 2450 | 20 | 20 |
| pep-0484 | 12122 | 35 | 35 |
| pep-0498 | 3210 | 29 | 29 |
| pep-0557 | 4652 | 32 | 32 |
| pep-0572 | 6305 | 26 | 26 |

Median 26, max 54. 10 of 15 files score above 15 in both modes.

## Rules firing most often on this set

| Rule | Files |
|---|---:|
| repetitive consecutive sentence openers | 15 / 15 |
| stock AI words/phrases | 10 / 15 |
| scam/hype marketing triggers | 9 / 15 |
| copula avoidance | 4 / 15 |
| mechanical transition stacking | 4 / 15 |
| em-dash overuse | 3 / 15 |

## Caveats

- PEPs are reStructuredText with literal code blocks and tables. `--strip-markdown` only removes Markdown code fences, so code and RST markup are still scanned as prose. That probably inflates scores. A plain-prose or Markdown set is needed to separate this effect.
- "Repetitive sentence openers" firing on every file, and "hype triggers" firing on specification text, suggest those rules need a look for false positives. Not yet investigated.
- Technical specifications are one genre. Blog posts, essays and marketing copy written by humans are not covered.

## Next steps

- Re-run on Markdown prose (pre-2020 blog posts, READMEs, docs) with code blocks stripped.
- Check why the two rules above fire so broadly, and adjust or add exemptions.
- Revisit the default threshold once a larger set exists.
