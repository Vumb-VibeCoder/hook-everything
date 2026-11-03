#!/usr/bin/env python3
"""Unit tests for the hidden-character audit in tools/slop_scan.py (v5.2.0)."""
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
SCRIPT = os.path.join(REPO_ROOT, "tools", "slop_scan.py")

import slop_scan  # noqa: E402


def tags(s: str) -> str:
    return "".join(chr(0xE0000 + ord(c)) for c in s)


class TestHiddenAudit(unittest.TestCase):
    def test_clean_text_reports_nothing(self):
        rep = slop_scan.audit_hidden("Plain ASCII text, with café and 中文.\n")
        self.assertEqual(rep["total"], 0)
        self.assertEqual(rep["mixed_script_count"], 0)

    def test_zero_width_and_odd_spaces(self):
        rep = slop_scan.audit_hidden("a​b c d e f")
        self.assertEqual(rep["categories"]["zero-width"]["total"], 1)
        self.assertEqual(rep["categories"]["odd-space"]["total"], 2)
        self.assertIn("U+202F", rep["categories"]["odd-space"]["codepoints"])

    def test_bidi_and_soft_hyphen(self):
        rep = slop_scan.audit_hidden("x‮y­z")
        self.assertIn("bidi-control", rep["categories"])
        self.assertIn("soft-hyphen", rep["categories"])

    def test_tag_characters_are_decoded(self):
        rep = slop_scan.audit_hidden("hi" + tags("secret") + "!")
        self.assertEqual(rep["decoded_tag_text"], ["secret"])
        self.assertEqual(rep["categories"]["tag-char"]["total"], 6)

    def test_flag_emoji_tag_sequence_is_not_flagged(self):
        flag = "\U0001F3F4" + tags("gbeng") + chr(0xE007F)
        self.assertEqual(slop_scan.audit_hidden(flag)["total"], 0)

    def test_emoji_zwj_and_vs16_are_not_flagged(self):
        family = "\U0001F468‍\U0001F469"
        heart = "❤️"
        self.assertEqual(slop_scan.audit_hidden(family + heart)["total"], 0)

    def test_vs16_after_plain_letter_is_flagged(self):
        self.assertEqual(slop_scan.audit_hidden("k️")["categories"]["variation-selector"]["total"], 1)

    def test_cjk_ideographic_space_is_not_flagged(self):
        self.assertEqual(slop_scan.audit_hidden("中　文")["total"], 0)

    def test_lookalike_word_detected(self):
        rep = slop_scan.audit_hidden("send рayment now")
        self.assertEqual(rep["mixed_script_count"], 1)

    def test_pure_cyrillic_word_not_flagged(self):
        self.assertEqual(slop_scan.audit_hidden("привет мир")["mixed_script_count"], 0)

    def test_control_characters(self):
        rep = slop_scan.audit_hidden("a\x00b\x1bc\td\n")
        self.assertEqual(rep["categories"]["control"]["total"], 2)


class TestHiddenClean(unittest.TestCase):
    def test_clean_strips_and_normalizes(self):
        raw = "a​b c d" + tags("x") + "e‮f"
        self.assertEqual(slop_scan.clean_hidden(raw), "ab c def")

    def test_clean_keeps_emoji_sequences(self):
        s = "\U0001F468‍\U0001F469 ❤️"
        self.assertEqual(slop_scan.clean_hidden(s), s)

    def test_clean_is_idempotent(self):
        raw = "x​y z" + tags("hi")
        once = slop_scan.clean_hidden(raw)
        self.assertEqual(slop_scan.clean_hidden(once), once)
        self.assertEqual(slop_scan.audit_hidden(once)["total"], 0)


class TestHiddenCli(unittest.TestCase):
    def run_cli(self, text, *flags):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write(text)
            path = fh.name
        try:
            return subprocess.run([sys.executable, SCRIPT, path, *flags], capture_output=True, text=True)
        finally:
            os.unlink(path)

    def test_fail_on_hidden_exit_code(self):
        self.assertEqual(self.run_cli("ok​text", "--fail-on-hidden").returncode, 1)
        self.assertEqual(self.run_cli("ok text", "--fail-on-hidden").returncode, 0)

    def test_hidden_flag_prints_report(self):
        out = self.run_cli("ok text", "--hidden").stdout
        self.assertIn("odd-space", out)
        self.assertIn("not proof of AI authorship", out)

    def test_json_includes_hidden_chars(self):
        import json
        out = self.run_cli("ok​text", "--json", "--hidden").stdout
        self.assertEqual(json.loads(out)["hidden_chars"]["total"], 1)

    def test_clean_to_stdout(self):
        self.assertEqual(self.run_cli("a​b", "--clean", "-").stdout, "ab")


if __name__ == "__main__":
    unittest.main()
