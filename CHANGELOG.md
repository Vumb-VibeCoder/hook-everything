# Changelog

All notable changes to `hook-everything` are documented in this file.

## [5.1.0] - 2026-11-03

### Added

Version 5.1.0 introduces automated testing, continuous integration, semantic versioning, and expanded multilingual coverage across the scanner and documentation.

| Component | Summary of Additions |
|---|---|
| `tests/test_slop_scan.py` | Zero-dependency `unittest` suite (14 test methods) covering all 18 scanner dimensions, Task A fixes, `--version`, `BrokenPipeError` handling, the human Vietnamese sample, and context-sensitive matching for `harness`, `vital`, and `realm`. |
| `.github/workflows/ci.yml` | GitHub Actions workflow running `--selftest`, `unittest`, raw `--max-score 15` checks on `README.md`, `AGENTS.md`, and `SKILL.md`, and `--strip-markdown --max-score 15` checks on `CHANGELOG.md` and `research/SOURCES.md`. |
| `VERSION` & `--version` | Explicit semantic version file (`5.1.0`) kept in sync with `slop_scan.__version__` and `python3 tools/slop_scan.py --version`. |
| `tools/slop_scan.py` CLI Flags | Added `--strip-markdown` (for auditing reference and skill docs that quote banned phrases on purpose), `--max-score N` (for CI gating), and silent `BrokenPipeError` exit (`exit 0`) when piped to tools like `head`. |
| Expanded Lexical & CJK Support | Added curly quote normalization (`’ ‘ “ ”` -> `' "`), 16 previously unindexed phrases from `skills/anti-slop/SKILL.md` (`empower`, `streamline`, `revolutionize`, `transformative`, `indelible`, `production-ready`, `blazingly fast`, `comprehensive error handling`, `a deep dive into`, `in the wake of`, `en conclusion`, `un tapiz de`, `une pléthore de`, `es ist wichtig zu beachten`), Rule 58 Chinese/Japanese/Korean phrases, CJK character counting, sentence splitting on `。！？`, a ~60-word natural Vietnamese human self-test sample, and a 35-assertion `--selftest` suite. |
| Lite vs. Full Routing Lane | Documented a fast 2-to-3 skill Lite lane in `AGENTS.md` and `README.md` for short edits alongside the 7-stage Full lane for multi-touch campaigns and product architecture. |
| English Glosses | Added plain-quote English glosses under Vietnamese examples in `skills/anti-slop/SKILL.md` (Rules 12, 16, 53, 54, 76, 78, 79, 80, 83) and `examples/before-after.md` (Example 15). |

### Changed

Scanner precision was tightened to reduce false positives on technical and financial writing without losing real detections. Specifically, `tools/slop_scan.py` now ignores em-dashes inside fenced code blocks and inline code spans, flags `leverage` only in verb-like contexts (leaving `leverage ratio` and `debt leverage` unflagged), flags `harness` / `harnessing` only as a marketing verb (`harness the power of`, `harnessing your data` while ignoring `climbing harness` and `test harness`), flags `vital` only in cliché frames (`vital role`, `vital for`, `is vital`, `vital to` while ignoring `vital signs` and `Vital Farms`), and flags `realm` only in `the realm of`. Rule-of-three triad detection now ignores pure-number lists and day/month abbreviations, see-saw concession detection catches `While/Although` at the start of any line, and unpunctuated multiline text falls back to splitting on newlines.

Empirical evidence ratings in `research/SOURCES.md` and `skills/psychology-map/SKILL.md` were restructured into a 31-row table (`M1`–`M30` plus `REF-1`) with explicit `STRONG`, `MIXED`, and `WEAK` definitions and a DOI verification caveat. Fourteen mechanisms with contested replication or indirect UX transfer were recalibrated to `MIXED` (`M3`, `M4`, `M5`, `M6`, `M12`, `M16`, `M18` citing Gal & Rucker 2018, `M20` citing Helmreich, Aronson & LeFan 1970, `M22`, `M23`, `M24` citing Burger 1999, `M25`, `M26`, `M28` citing Scheibehenne, Greifeneder & Todd 2010, and `M29`), while row `M30` splits the rating into `ELM = STRONG; Construal Level Theory = MIXED`.

Across all documentation and skill files, slang labels (`"Anti-Lùa Gà"`, `"Văn Mẫu AI"`, `"Văn Mẫu Dịch Máy"`) were replaced with standard English terms (`"Anti-Scam"`, `"AI Boilerplate"`, `"Machine-Translated Boilerplate"`), unsourced industry stats were softened to `"working heuristic, verify with your own data"`, frontmatter `description` fields were shortened to `<= 220` characters, and example score claims were calibrated to exact v5.1 scanner outputs.
