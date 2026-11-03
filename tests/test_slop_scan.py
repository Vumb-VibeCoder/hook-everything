#!/usr/bin/env python3
"""Unit test suite for tools/slop_scan.py (v5.2.0).

Covers every scanner indicator, Task A fixes, --version, BrokenPipeError handling,
human Vietnamese sample, and context-sensitive harness/vital/realm matching.
Zero external dependencies; runs with `python3 -m unittest discover -s tests`.
"""
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import slop_scan  # noqa: E402


class TestSlopScanRulesAndFixes(unittest.TestCase):
    def test_a1_normalize_curly_quotes_and_apostrophes(self):
        text = "In today\u2019s fast-paced world, it\u2019s important to note that \u201cseamless\u201d workflows matter."
        res = slop_scan.scan(text)
        self.assertGreaterEqual(res["score"], 20)
        self.assertTrue(any("stock AI" in h for h in res["hits"]))

    def test_a2_missing_stock_words_and_multilingual_phrases(self):
        phrases = [
            "empower", "harness the power of", "streamline", "revolutionize", "transformative",
            "vital for", "indelible", "production-ready", "blazingly fast",
            "comprehensive error handling", "a deep dive into", "in the wake of",
            "the realm of", "en conclusion", "un tapiz de", "une pléthore de",
            "es ist wichtig zu beachten"
        ]
        for p in phrases:
            res = slop_scan.scan(f"Here is a sample sentence containing {p} in context.")
            self.assertTrue(
                any("stock AI" in h for h in res["hits"]),
                f"Expected stock phrase '{p}' to be flagged, got hits={res['hits']}",
            )

    def test_a2_and_a3_cjk_phrases_and_token_sentence_counting(self):
        cjk_text = (
            "在当今快节奏的数字时代，人工智能不仅仅是一个工具，而是发挥着至关重要的作用。"
            "总而言之，让我们一起探索。結論として、単なる道具ではなく重要な役割を果たしています。"
            "오늘날 빠르게 변화하는 세상에서 중요한 역할을 합니다。"
        )
        res = slop_scan.scan(cjk_text)
        self.assertGreaterEqual(res["words"], 45)
        self.assertGreaterEqual(res["sentences"], 3)
        self.assertTrue(any("stock AI" in h for h in res["hits"]))
        self.assertTrue(any("negative parallelism" in h for h in res["hits"]))

    def test_a4_ignore_em_dashes_in_code_blocks_and_inline_code(self):
        text = (
            "We deployed the fix at 4:55 PM on Friday. Nothing broke.\n"
            "Inline code `foo — bar — baz — qux` and fenced block:\n"
            "```python\n"
            "# a — b — c — d — e\n"
            "x = '—'\n"
            "```\n"
            "All checks passed in 12 seconds."
        )
        res = slop_scan.scan(text)
        self.assertFalse(any("em-dash" in h for h in res["hits"]))

    def test_a5_leverage_verb_only_not_noun_compounds(self):
        noun_text = (
            "The company reduced its debt leverage and kept a conservative leverage ratio. "
            "Operating leverage and financial leverage remained within target bounds."
        )
        res_noun = slop_scan.scan(noun_text)
        self.assertFalse(any("leverage" in h for h in res_noun["hits"]))

        verb_text = "We leverage distributed queues and leveraging worker pools to process jobs."
        res_verb = slop_scan.scan(verb_text)
        self.assertTrue(any("leverage" in h for h in res_verb["hits"]))

    def test_harness_vital_realm_context_sensitivity(self):
        # 1. harness / harnessing: positive vs negative
        res_h_pos = slop_scan.scan("We harness the power of AI and harnessing your data to grow.")
        self.assertTrue(any("harness" in h for h in res_h_pos["hits"]))
        res_h_neg = slop_scan.scan("Clip the climbing harness, check the wiring harness, and run the test harness.")
        self.assertFalse(any("harness" in h for h in res_h_neg["hits"]))
        self.assertEqual(res_h_neg["score"], 0)

        # 2. vital: positive vs negative
        for v_phrase in ("vital role", "vital for", "is vital", "vital to"):
            res_v_pos = slop_scan.scan(f"This step {v_phrase} system reliability.")
            self.assertTrue(any("vital" in h for h in res_v_pos["hits"]), f"Failed on {v_phrase}")
        res_v_neg = slop_scan.scan("Check the patient's vital signs and buy pasture-raised eggs from Vital Farms.")
        self.assertFalse(any("vital" in h for h in res_v_neg["hits"]))
        self.assertEqual(res_v_neg["score"], 0)

        # 3. realm: positive vs negative
        res_r_pos = slop_scan.scan("This moves the problem into the realm of distributed consensus.")
        self.assertTrue(any("the realm of" in h for h in res_r_pos["hits"]))
        res_r_neg = slop_scan.scan("Set the Kerberos realm in the config or explore the fantasy realm.")
        self.assertFalse(any("realm" in h for h in res_r_neg["hits"]))
        self.assertEqual(res_r_neg["score"], 0)

    def test_human_vietnamese_sample_scores_clean(self):
        res_vi = slop_scan.scan(slop_scan.HUMAN_VI_SAMPLE)
        self.assertGreaterEqual(res_vi["words"], 55)
        self.assertLessEqual(res_vi["score"], 15)

    def test_version_flag_and_broken_pipe_handling(self):
        script = os.path.join(REPO_ROOT, "tools", "slop_scan.py")
        with open(os.path.join(REPO_ROOT, "VERSION"), encoding="utf-8") as vf:
            version_file = vf.read().strip()
        self.assertEqual(slop_scan.__version__, version_file)

        proc_ver = subprocess.run(
            [sys.executable, script, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc_ver.returncode, 0)
        self.assertEqual(proc_ver.stdout.strip(), f"slop_scan {version_file}")

        # BrokenPipeError test: pipe README.md scan into `head -n 1`
        readme_path = os.path.join(REPO_ROOT, "README.md")
        cmd = f"{sys.executable} {script} {readme_path} | head -n 1"
        proc_pipe = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc_pipe.returncode, 0)
        self.assertNotIn("Traceback", proc_pipe.stderr)
        self.assertNotIn("BrokenPipeError", proc_pipe.stderr)
        self.assertIn("slop score:", proc_pipe.stdout)

    def test_a6_triad_ignores_numbers_and_calendar_abbreviations(self):
        clean_lists = (
            "Ports 80, 443, and 8080 are open. "
            "Backups run on Mon, Wed, and Fri during Jan, Feb, and Mar. "
            "We also check Monday, Tuesday, and Wednesday logs."
        )
        res_clean = slop_scan.scan(clean_lists)
        self.assertFalse(any("rule-of-three" in h for h in res_clean["hits"]))

        slop_triads = (
            "Our fast, reliable, and secure engine builds clean, modular, and testable code "
            "for modern, agile, and distributed teams."
        )
        res_triad = slop_scan.scan(slop_triads)
        self.assertTrue(any("rule-of-three" in h for h in res_triad["hits"]))

    def test_a7_seesaw_concession_at_start_of_any_line(self):
        text = (
            "Normal opening line here.\n"
            "While the first option is cheap, it fails under heavy load.\n"
            "Although the second option is faster, it uses twice the memory."
        )
        res = slop_scan.scan(text)
        self.assertTrue(any("see-saw" in h for h in res["hits"]))

    def test_a8_unpunctuated_text_splits_on_newlines(self):
        text = (
            "First unpunctuated heading line\n"
            "Second unpunctuated line with several more words inside it\n"
            "Third short line\n"
            "Fourth unpunctuated line with extra details for variety"
        )
        res = slop_scan.scan(text)
        self.assertEqual(res["sentences"], 4)

    def test_all_other_scanner_rules(self):
        text = (
            "### Caching: How Redis Improves Latency\n"
            "To truly understand caching, we must look back. "
            "The system serves as a core engine, highlighting our speed. "
            "The result? Faster loads from startups to Fortune 500 enterprises. "
            "Experts argue that this article explores the best method.\n"
            "Furthermore, it works well.\n"
            "Moreover, it scales."
        )
        res = slop_scan.scan(text)
        hit_blob = " | ".join(res["hits"])
        self.assertIn("participial", hit_blob)
        self.assertIn("copula", hit_blob)
        self.assertIn("self-Q&A", hit_blob)
        self.assertIn("pedagogical", hit_blob)
        self.assertIn("framing", hit_blob)
        self.assertIn("transition stacking", hit_blob)

    def test_forced_trend_and_scam_hype_rules(self):
        text = (
            "With the recent explosion of AI agents, you can 10x your revenue! "
            "Use this secret blueprint — spots are filling up fast!"
        )
        res = slop_scan.scan(text)
        hit_blob = " | ".join(res["hits"])
        self.assertIn("trend-jacking", hit_blob)
        self.assertIn("scam/hype", hit_blob)

    def test_strip_markdown_and_max_score_cli(self):
        script = os.path.join(REPO_ROOT, "tools", "slop_scan.py")
        proc = subprocess.run(
            [sys.executable, script, "--selftest"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("ALL PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
