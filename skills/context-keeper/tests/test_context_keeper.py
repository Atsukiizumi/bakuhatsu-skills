"""Run from the package root: python -m unittest discover -s tests -v"""
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

S = Path(__file__).resolve().parents[1] / "scripts" / "context_keeper.py"
spec = importlib.util.spec_from_file_location("ck", S)
ck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ck)


class ContextKeeperTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def test_init_idempotent_preserves_edits(self):
        created = ck.init(self.root)
        self.assertEqual(len(created["created"]), 3)
        p = self.root / ".ai-context" / "ACTIVE.md"
        p.write_text("CUSTOM", encoding="utf-8")
        again = ck.init(self.root)
        self.assertFalse(again["created"])
        self.assertEqual(p.read_text(encoding="utf-8"), "CUSTOM")

    def test_scan_read_only_and_empty_repo(self):
        result = ck.scan(self.root)
        self.assertFalse((self.root / ".ai-context").exists())
        self.assertIn("agent_context_files", result)

    def test_validate_warns_for_placeholders(self):
        ck.init(self.root)
        result = ck.validate(self.root)
        self.assertTrue(result["structurally_valid"])
        self.assertFalse(result["ready_for_handoff"])
        self.assertTrue(any("[待填写]" in x for x in result["warnings"]))

    def test_hook_does_not_store_untrusted_transcript(self):
        ck.init(self.root)
        raw = '{"trigger":"auto", "transcript":"password=supersecret", "session_id":"ID123"}'
        with patch("sys.stdin", io.StringIO(raw)):
            out = ck.hook(self.root, "gemini", "precompress", True)
        self.assertEqual(out, {})
        event_log = (self.root / ".ai-context" / "runtime" / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("supersecret", event_log)
        self.assertNotIn("ID123", event_log)
        self.assertEqual(json.loads(event_log)["event"], "precompress")

    def test_sessionstart_contains_only_fixed_hint(self):
        with patch("sys.stdin", io.StringIO("{}")):
            out = ck.hook(self.root, "claude", "sessionstart", False)
        hint = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("ACTIVE.md", hint)
        self.assertLess(len(hint), 300)


if __name__ == "__main__":
    unittest.main()
